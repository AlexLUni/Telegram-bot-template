import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

import app.const_texts as txts
from app.cache.user_cache import UserData
from app.database.models.enums import UserRole
from app.database.models.user_states import UserState
from app.filters import CallbackFilter
from app.helpers import handle_errors
from app.services.user_manager import update_user_state


logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type.in_({'private'}))


@router.callback_query(F.data.startswith('cancel'), CallbackFilter(role=UserRole.ADMIN))
@handle_errors
async def cancel(callback: CallbackQuery, user_data: UserData) -> None:
    """Cancel any database related procedures."""
    if not callback.message or not callback.bot or not callback.from_user:
        logger.warning('Callback missing required attributes in cancel')
        return

    await update_user_state(callback.from_user.id, UserState.DEFAULT)
    await callback.message.answer(txts.CANCEL[0], txts.CANCEL[1])
    await callback.bot.delete_message(callback.from_user.id, callback.message.message_id)
    await callback.answer()
