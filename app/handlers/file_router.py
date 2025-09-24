import logging
import secrets
import string

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import app.const_texts as txts
import app.keyboards as kb
from app.cache.user_cache import UserData
from app.database.models import File
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
    'booklets': txts.FILE_BOOKLETS,
    'books': txts.FILE_BOOKS,
    'formats': txts.FILE_FORMATS,
    'extras': txts.FILE_EXTRAS,
    'schedule': txts.FILE_SCHEDULE,
    'pics': txts.FILE_BOT_PICS,
}


@router.callback_query(F.data.startswith('public_file_'))
@handle_errors
async def view_file_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a list of entries of chosen file category."""
    if not callback.data or not callback.message or not callback.from_user:
        logger.warning('Callback missing required attributes in view_file_cat')
        return
    sure_name = callback.data.split('_')[2]
    category = category_map.get(sure_name, '')
    await callback.message.answer(f'{category}:', reply_markup=await kb.files_by_cat(category))
    await callback.answer()


@router.callback_query(F.data.startswith('file_'))
@handle_errors
async def view_file(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a chosen file."""
    if not callback.data or not callback.message or not callback.from_user:
        logger.warning('Callback missing required attributes in view_file')
        return
    file_id = int(callback.data.split('_')[1])
    async with UnitOfWork(auto_commit=False) as uow:
        file = await uow.files.get_by_id(file_id)
    if file:
        await callback.message.answer_document(file.tg_id)
    await callback.answer()


@router.message(Command('delfile'), MessageFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def del_file(message: Message, user_data: UserData) -> None:
    """Send a list of categories for deleting files."""
    if not message.from_user:
        logger.warning('Message missing required attributes in del_file')
        return
    await update_user_state(message.from_user.id, UserState.DELETE_FILE_CAT)
    await message.answer(txts.DEL_FILE_CATEGORY[0], txts.DEL_FILE_CATEGORY[1],
                        reply_markup=kb.del_file_categories_value)


@router.callback_query(CallbackFilter(role=UserRole.SUPERADMIN, state=UserState.DELETE_FILE_CAT))
@handle_errors
async def del_file_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a list of files of chosen category to delete one."""
    if not callback.data or not callback.from_user or not callback.message:
        logger.warning('Callback missing required attributes in del_file_cat')
        return
    sure_name = callback.data.split('_')[3]
    category = category_map.get(sure_name, '')
    await update_user_state(callback.from_user.id, UserState.DELETE_FILE_MES)
    await callback.message.answer(txts.CHOOSE_MESSAGE[0], txts.CHOOSE_MESSAGE[1],
        reply_markup=await kb.delete_file_entry_value(category))
    await callback.answer()


@router.callback_query(CallbackFilter(role=UserRole.SUPERADMIN, state=UserState.DELETE_FILE_MES))
@handle_errors
async def delete_file_mes(callback: CallbackQuery, user_data: UserData) -> None:
    """Delete a chosen a file."""
    if not callback.data or not callback.from_user or not callback.message:
        logger.warning('Callback missing required attributes in delete_file_mes')
        return
    mes_id = int(callback.data.split('_')[3])
    async with UnitOfWork(auto_commit=True) as uow:
        mes = await uow.files.get_by_id(mes_id)
        if mes:
            await uow.files.delete(mes)
    await update_user_state(callback.from_user.id, UserState.DEFAULT)
    await callback.message.answer(txts.ENTRY_DELETED[0], txts.ENTRY_DELETED[1])
    await callback.answer()


@router.message(Command('addfile'), MessageFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def cmd_add_file(message: Message, user_data: UserData) -> None:
    """Send a list of categories for adding files."""
    if not message.from_user:
        logger.warning('Message missing required attributes in addfile')
        return
    await message.answer(txts.ADD_FILE_CATEGORY[0], txts.ADD_FILE_CATEGORY[1],
                            reply_markup=kb.add_file_categories)


@router.callback_query(F.data.startswith('add_file_'), CallbackFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def addfile_cat(callback: CallbackQuery, user_data: UserData) -> None:
    """Ask user to send a file or a picture after selecting category."""
    if not callback.data or not callback.from_user or not callback.message:
        logger.warning('Callback missing required attributes in addfile_cat')
        return
    sure_name = callback.data.split('_')[2]
    async with UnitOfWork(auto_commit=True) as uow:
        file = await uow.files.add(File(category=category_map.get(sure_name), status=UploadState.UNFINISHED))

    if sure_name == 'pics':
        await update_user_state(callback.from_user.id, f'{UserState.PICS_UPLOAD}:{file.id}')
        await callback.message.answer(txts.ADD_PIC[0], txts.ADD_PIC[1])
    else:
        await update_user_state(callback.from_user.id, f'{UserState.FILE_UPLOAD}:{file.id}')
        await callback.message.answer(txts.ADD_FILE[0], txts.ADD_FILE[1])
    await callback.answer()


@router.message(MessageFilter(role=UserRole.SUPERADMIN, state=UserState.FILE_UPLOAD))
@handle_errors
async def upload_document(message: Message, user_data: UserData) -> None:
    """Parse file upload and save an entry for File."""
    if not message.from_user or not message.document:
        logger.warning('Message missing required attributes in upload_document')
        return

    file_id = int(user_data.state.split(':')[1])

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.files.update_fields(
            filters={'id': file_id},
            update_values={
                'tg_id': message.document.file_id,
                'name': message.document.file_name,
                'status': UploadState.UPLOADED,
            },
        )

    await update_user_state(message.from_user.id, UserState.DEFAULT)
    await message.answer(txts.FILE_ADDED[0], txts.FILE_ADDED[1])


@router.message(MessageFilter(role=UserRole.SUPERADMIN, state=UserState.PICS_UPLOAD))
@handle_errors
async def upload_picture(message: Message, user_data: UserData) -> None:
    """Parse picture upload and save an entry for File."""
    if not message.from_user or not message.photo:
        logger.warning('Message missing required attributes in upload_picture')
        return
    tg_id = message.photo[-1].file_id
    name = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    file_id = int(user_data.state.split(':')[1])

    async with UnitOfWork(auto_commit=True) as uow:
        await uow.files.update_fields(
            filters={'id': file_id},
            update_values={
                'tg_id': tg_id,
                'name': name,
                'status': UploadState.UPLOADED,
            },
        )

    await update_user_state(message.from_user.id, UserState.DEFAULT)
    await message.answer(txts.PIC_ADDED[0], txts.PIC_ADDED[1])
