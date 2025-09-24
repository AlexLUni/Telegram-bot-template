import logging
from collections.abc import Awaitable
from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from app.services.user_manager import create_user_if_not_exists, get_user_with_cache


logger = logging.getLogger(__name__)


class UserDataMiddleware(BaseMiddleware):
    """Inject user data into handler context."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, object]], Awaitable[object]],
        event: TelegramObject,
        data: dict[str, object],
    ) -> object:
        """Add user data to context."""
        user_id = None
        from_user = None

        try:
            if isinstance(event, Update):
                if event.message:
                    from_user = event.message.from_user
                elif event.callback_query:
                    from_user = event.callback_query.from_user
            elif isinstance(event, (Message, CallbackQuery)):
                from_user = event.from_user

            if not from_user or not from_user.id:
                return await handler(event, data)

            user_id = from_user.id

            user_data = await get_user_with_cache(user_id)

            if not user_data:
                user_data = await create_user_if_not_exists(
                    user_id=user_id,
                    first_name=from_user.first_name,
                    last_name=from_user.last_name,
                    username=from_user.username,
                )

            data['user_data'] = user_data
            data['user_role'] = user_data.role
            data['user_state'] = user_data.state

        except Exception:
            logger.exception('Error in UserDataMiddleware')
            data['user_data'] = None
            data['user_role'] = None
            data['user_state'] = None

        return await handler(event, data)
