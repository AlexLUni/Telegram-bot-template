import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import app.const_texts as txts
import app.constants as cnst
import app.keyboards as kb
from app.cache.user_cache import UserData
from app.database.models import ConstantMessage
from app.database.models.enums import UploadState, UserRole
from app.database.models.user_states import UserState
from app.database.uow import UnitOfWork
from app.filters import CallbackFilter, MessageFilter
from app.helpers import handle_errors
from app.services.user_manager import update_user_state


logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.type.in_({'private'}))

category_map = {
    'links': txts.CONST_LINKS,
    'newcomer': txts.CONST_NEWCOMER,
    'contacts': txts.CONST_CONTACTS,
}


@router.callback_query(F.data.startswith('const_mes_'))
async def view_const(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a consant message chosen by user."""
    if not callback.data or not callback.bot or not callback.message or not callback.from_user:
        logger.warning('Callback missing required attributes in view_const')
        return
    mes_id = int(callback.data.split('_')[2])
    async with UnitOfWork(auto_commit=False) as uow:
        mes = await uow.const.get_by_id(mes_id)
    if mes:
        await callback.bot.copy_message(callback.message.chat.id, mes.chat_id, mes.message_id)
    await callback.answer()


@router.message(Command('delconst'), MessageFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def del_const(message: Message, user_data: UserData) -> None:
    """Send a list of categories for deleting constant messages."""
    if not message.from_user:
        logger.warning('Message missing required attributes in del_const')
        return
    await update_user_state(message.from_user.id, UserState.DELETE_CONST_CAT)
    await message.answer(txts.DEL_CONST_CATEGORY[0], txts.DEL_CONST_CATEGORY[1],
                        reply_markup=kb.del_const_categories_value)


@router.callback_query(CallbackFilter(role=UserRole.SUPERADMIN, state=UserState.DELETE_CONST_CAT))
@handle_errors
async def del_const_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a list of entries of chosen category for constant message."""
    if not callback.data or not callback.from_user or not callback.message:
        logger.warning('Callback missing required attributes in del_const_cat')
        return
    sure_name = callback.data.split('_')[3]
    category = category_map.get(sure_name, '')
    await update_user_state(callback.from_user.id, UserState.DELETE_CONST_MES)
    await callback.message.answer(txts.CHOOSE_MESSAGE[0], txts.CHOOSE_MESSAGE[1],
        reply_markup=await kb.delete_const_entry_value(category))
    await callback.answer()


@router.callback_query(CallbackFilter(role=UserRole.SUPERADMIN, state=UserState.DELETE_CONST_MES))
@handle_errors
async def delete_const_mes(callback: CallbackQuery, user_data: UserData) -> None:
    """Delete a chosen constant message."""
    if not callback.data or not callback.from_user or not callback.message:
        logger.warning('Callback missing required attributes in delete_const_mes')
        return
    mes_id = int(callback.data.split('_')[3])
    async with UnitOfWork(auto_commit=True) as uow:
        mes = await uow.const.get_by_id(mes_id)
        if mes:
            await uow.const.delete(mes)
    await update_user_state(callback.from_user.id, UserState.DEFAULT)
    await callback.message.answer(txts.ENTRY_DELETED[0], txts.ENTRY_DELETED[1])
    await callback.answer()


@router.message(Command('addconst'), MessageFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def cmd_add_const(message: Message, user_data: UserData) -> None:
    """Send a list of categories for adding constant messages."""
    if not message.from_user:
        logger.warning('Message missing required attributes in addconst')
        return
    await message.answer(txts.ADD_CONST_CATEGORY[0], txts.ADD_CONST_CATEGORY[1],
                        reply_markup=kb.add_const_categories)


@router.callback_query(F.data.startswith('add_const_'), CallbackFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def add_const_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Ask user to send descriptipon(name) of a new constant message."""
    if not callback.data or not callback.from_user or not callback.message:
        logger.warning('Callback missing required attributes in add_const_cat')
        return
    sure_name = callback.data.split('_')[2]
    async with UnitOfWork(auto_commit=True) as uow:
        const = await uow.const.add(ConstantMessage(
            admin_id=callback.from_user.id,
            chat_id=cnst.MSG_VAULT,
            category=category_map.get(sure_name),
            status=UploadState.UNFINISHED,
        ))
    await update_user_state(callback.from_user.id, f'{UserState.CONST_SEND_NAME}:{const.id}')
    await callback.message.answer(txts.ADD_CONST_NAME[0], txts.ADD_CONST_NAME[1], reply_markup=kb.cancel)
    await callback.answer()


@router.message(MessageFilter(role=UserRole.SUPERADMIN, state=UserState.CONST_SEND_NAME))
@handle_errors
async def add_const_name(message: Message, user_data: UserData) -> None:
    """Ask user to send message text for saving and save message's description(name)."""
    if not message.from_user:
        logger.warning('Message missing required attributes in add_const_name')
        return

    const_id = int(user_data.state.split(':')[1])

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.const.update_fields(filters={'id': const_id}, update_values={'name': message.text})

    await update_user_state(message.from_user.id, f'{UserState.CONST_SEND_MESSAGE}:{const_id}')
    await message.answer(txts.ADD_CONST_MESSAGE[0], txts.ADD_CONST_MESSAGE[1], reply_markup=kb.cancel)


@router.message(MessageFilter(role=UserRole.SUPERADMIN, state=UserState.CONST_SEND_MESSAGE))
@handle_errors
async def add_const_message(message: Message, user_data: UserData) -> None:
    """Save the entire data for constant message in db."""
    if not message.from_user or not message.bot:
        logger.warning('Message missing required attributes in add_const_message')
        return

    const_id = int(user_data.state.split(':')[1])

    msg = await message.bot.copy_message(int(cnst.MSG_VAULT), message.chat.id, message.message_id)

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.const.update_fields(
            filters={'id': const_id},
            update_values={
                'message_id': msg.message_id,
                'status': UploadState.UPLOADED,
            },
        )

    await update_user_state(message.from_user.id, UserState.DEFAULT)
    await message.answer(txts.CONST_ADDED[0], txts.CONST_ADDED[1])
