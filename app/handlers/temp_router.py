import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import app.const_texts as txts
import app.constants as cnst
import app.keyboards as kb
from app.cache.user_cache import UserData
from app.database.models import TemporaryMessage
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
    'speakers': txts.TEMP_SPEAKERS,
    'sessions': txts.TEMP_SESSIONS,
}


@router.callback_query(F.data.startswith('temp_mes_'))
async def view_temp(callback: CallbackQuery) -> None:
    """Send the chosen temp message."""
    if not callback.data or not callback.bot or not callback.message:
        logger.warning('Callback missing required attributes in view_temp')
        return
    mes_id = int(callback.data.split('_')[2])
    async with UnitOfWork(auto_commit=False) as uow:
        mes = await uow.temp.get_by_id(mes_id)
    if mes:
        await callback.bot.copy_message(callback.message.chat.id, mes.chat_id, mes.message_id)
    await callback.answer()


@router.message(Command('deltemp'), MessageFilter(role=UserRole.ADMIN))
@handle_errors
async def del_temp(message: Message, user_data: UserData) -> None:
    """Send a list of categories for deleting temporary messages."""
    if not message.from_user:
        logger.warning('Message missing required attributes in del_temp')
        return
    await update_user_state(message.from_user.id, UserState.DELETE_TEMP_CAT)
    await message.answer(txts.DEL_TEMP_CATEGORY[0], txts.DEL_TEMP_CATEGORY[1],
                        reply_markup=kb.del_temp_categories_value)


@router.callback_query(CallbackFilter(role=UserRole.ADMIN, state=UserState.DELETE_TEMP_CAT))
@handle_errors
async def del_temp_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a list of temp messages of chosen category for deleting."""
    if not callback.data or not callback.message:
        logger.warning('Callback missing required attributes in del_temp_cat')
        return
    sure_name = callback.data.split('_')[3]
    category = category_map.get(sure_name, '')
    await update_user_state(callback.from_user.id, UserState.DELETE_TEMP_MES)
    await callback.message.answer(txts.CHOOSE_MESSAGE[0], txts.CHOOSE_MESSAGE[1],
        reply_markup=await kb.delete_temp_entry_value(callback.from_user.id, category))
    await callback.answer()


@router.callback_query(CallbackFilter(role=UserRole.ADMIN, state=UserState.DELETE_TEMP_MES))
@handle_errors
async def delete_temp_mes(callback: CallbackQuery, user_data: UserData) -> None:
    """Delete the chosen temp message."""
    if not callback.data or not callback.message:
        logger.warning('Callback missing required attributes in delete_temp_mes')
        return
    mes_id = int(callback.data.split('_')[3])
    async with UnitOfWork(auto_commit=True) as uow:
        mes = await uow.temp.get_by_id(mes_id)
        if mes:
            await uow.temp.delete(mes)
    await update_user_state(callback.from_user.id, UserState.DEFAULT)
    await callback.message.answer(txts.ENTRY_DELETED[0], txts.ENTRY_DELETED[1])
    await callback.answer()


@router.message(Command('addtemp'), MessageFilter(role=UserRole.ADMIN))
@handle_errors
async def cmd_add_temp(message: Message, user_data: UserData) -> None:
    """Send a list of categories for adding temporary messages."""
    await message.answer(txts.ADD_TEMP_CATEGORY[0], txts.ADD_TEMP_CATEGORY[1],
                        reply_markup=kb.add_temp_categories)


@router.callback_query(F.data.startswith('add_temp_'), CallbackFilter(role=UserRole.ADMIN))
@handle_errors
async def add_temp_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Ask user to send description(name) of a new temporary message."""
    if not callback.data or not callback.message:
        logger.warning('Callback missing required attributes in add_temp_cat')
        return
    sure_name = callback.data.split('_')[2]
    async with UnitOfWork(auto_commit=True) as uow:
        temp = await uow.temp.add(TemporaryMessage(
            admin_id=callback.from_user.id,
            chat_id=cnst.MSG_VAULT,
            category=category_map.get(sure_name),
            status=UploadState.UNFINISHED,
        ))
    await update_user_state(callback.from_user.id, f'{UserState.TEMP_SEND_DATE}:{temp.id}')
    await callback.message.answer(txts.ADD_TEMP_DATE[0], txts.ADD_TEMP_DATE[1], reply_markup=kb.cancel)
    await callback.answer()


@router.message(MessageFilter(role=UserRole.ADMIN, state=UserState.TEMP_SEND_DATE))
@handle_errors
async def add_temp_date(message: Message, user_data: UserData) -> None:
    """Ask user to send name for speaker/session saving and save date."""
    if not message.from_user:
        logger.warning('Message missing required attributes in add_temp_date')
        return
    temp_id = int(user_data.state.split(':')[1])

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.temp.update_fields(filters={'id': temp_id}, update_values={'date': message.text})

    await update_user_state(message.from_user.id, f'{UserState.TEMP_SEND_NAME}:{temp_id}')
    await message.answer(txts.ADD_TEMP_NAME[0], txts.ADD_TEMP_NAME[1], reply_markup=kb.cancel)


@router.message(MessageFilter(role=UserRole.ADMIN, state=UserState.TEMP_SEND_NAME))
@handle_errors
async def add_temp_name(message: Message, user_data: UserData) -> None:
    """Ask user to send info message for speaker/session saving and save name."""
    if not message.from_user:
        logger.warning('Message missing required attributes in add_temp_name')
        return
    temp_id = int(user_data.state.split(':')[1])

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.temp.update_fields(filters={'id': temp_id}, update_values={'name': message.text})

    await update_user_state(message.from_user.id, f'{UserState.TEMP_SEND_MESSAGE}:{temp_id}')
    await message.answer(txts.ADD_TEMP_MESSAGE[0], txts.ADD_TEMP_MESSAGE[1], reply_markup=kb.cancel)


@router.message(MessageFilter(role=UserRole.ADMIN, state=UserState.TEMP_SEND_MESSAGE))
@handle_errors
async def add_temp_message(message: Message, user_data: UserData) -> None:
    """Save the entire data for temporary message in db."""
    if not message.bot or not message.from_user:
        logger.warning('Message missing attributes in add temp_message')
        return

    temp_id = int(user_data.state.split(':')[1])

    msg = await message.bot.copy_message(int(cnst.MSG_VAULT), message.chat.id, message.message_id)

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.temp.update_fields(
            filters={'id': temp_id},
            update_values={
                'message_id': msg.message_id,
                'status': UploadState.UPLOADED,
            },
        )

    await update_user_state(message.from_user.id, UserState.DEFAULT)
    await message.answer(txts.TEMP_ADDED[0], txts.TEMP_ADDED[1])
