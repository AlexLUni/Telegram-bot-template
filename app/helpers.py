import logging
import secrets
import string
from collections.abc import Awaitable
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from aiogram.exceptions import TelegramAPIError
from sqlalchemy.exc import SQLAlchemyError

import app.const_texts as txts
import app.constants as cnst
from app.database.models.user_states import UserState
from app.database.uow import UnitOfWork


logger = logging.getLogger(__name__)
P = ParamSpec('P')
R = TypeVar('R')


async def setup_initial_admins() -> None:
    """Initialize bot administrators before bot launch."""
    async with UnitOfWork(auto_commit=True) as uow:
        for user_id, user_info in cnst.ADMIN_IDS.items():
            await uow.users.upsert_do_nothing(
                conflict_columns=['user_id'],
                insert_values={
                    'user_id': user_id,
                    'first_name': user_info['first_name'],
                    'last_name': user_info['last_name'],
                    'username': user_info.get('username'),
                    'state': UserState.DEFAULT,
                    'role': user_info.get('role'),
                },
            )


def weekday_by_number(day_number: int) -> str:
    """Convert day number (0-6) to localized weekday name."""
    weekdays = [
        txts.DAY_MONDAY,
        txts.DAY_TUESDAY,
        txts.DAY_WEDNESDAY,
        txts.DAY_THURSDAY,
        txts.DAY_FRIDAY,
        txts.DAY_SATURDAY,
        txts.DAY_SUNDAY,
    ]
    return weekdays[day_number]


def handle_errors(func: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
    """Intercept and log exceptions in async handlers."""
    @wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await func(*args, **kwargs)
        except SQLAlchemyError:
            logger.exception('DB operation failed')
        except TelegramAPIError:
            logger.warning('Telegram API failure', exc_info=True)
        except Exception:
            logger.critical('Unexpected error', exc_info=True)
    return wrapped


def create_random_code(length: int = 8) -> str:
    """Generate secure random alphanumeric code."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
