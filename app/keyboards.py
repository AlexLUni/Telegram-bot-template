import logging
from typing import cast

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.const_texts as txts
from app.database.models.enums import UploadState, UserRole
from app.database.uow import UnitOfWork
from app.services.text_manager import text_manager


logger = logging.getLogger(__name__)

# main and adding admin menus
choose_role_owner = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text=txts.KB_ROLE_ADMIN, callback_data='choose_role_admin')],
    [InlineKeyboardButton(text=txts.KB_ROLE_SUPERADMIN, callback_data='choose_role_superadmin')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])

choose_role_superadmin = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text=txts.KB_ROLE_ADMIN, callback_data='choose_role_admin')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=txts.CMD_HELP_KB[0]),
         KeyboardButton(text=txts.CMD_FILES[0])],
        [KeyboardButton(text=txts.CMD_SPEAKERS[0]),
         KeyboardButton(text=txts.CMD_SESSIONS[0])],
        [KeyboardButton(text=txts.CMD_NEWCOMER[0]),
         KeyboardButton(text=txts.CMD_LINKS[0])],
    ],
    resize_keyboard=True,
    input_field_placeholder=txts.KB_PLACEHOLDER,
)

# public categories of entries
public_file_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.FILE_BOOKLETS, callback_data='public_file_booklets')],
    [InlineKeyboardButton(text=txts.FILE_BOOKS, callback_data='public_file_books')],
    [InlineKeyboardButton(text=txts.FILE_FORMATS, callback_data='public_file_formats')],
    [InlineKeyboardButton(text=txts.FILE_EXTRAS, callback_data='public_file_extras')],
    [InlineKeyboardButton(text=txts.FILE_SCHEDULE, callback_data='public_file_schedule')],
])

# add categories
add_file_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.FILE_BOOKLETS, callback_data='add_file_booklets')],
    [InlineKeyboardButton(text=txts.FILE_BOOKS, callback_data='add_file_books')],
    [InlineKeyboardButton(text=txts.FILE_BOT_PICS, callback_data='add_file_pics')],
    [InlineKeyboardButton(text=txts.FILE_FORMATS, callback_data='add_file_formats')],
    [InlineKeyboardButton(text=txts.FILE_EXTRAS, callback_data='add_file_extras')],
    [InlineKeyboardButton(text=txts.FILE_SCHEDULE, callback_data='add_file_schedule')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])

add_const_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.CONST_LINKS, callback_data='add_const_links')],
    [InlineKeyboardButton(text=txts.CONST_NEWCOMER, callback_data='add_const_newcomer')],
    [InlineKeyboardButton(text=txts.CONST_CONTACTS, callback_data='add_const_contacts')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])

add_temp_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.TEMP_SPEAKERS, callback_data='add_temp_speakers')],
    [InlineKeyboardButton(text=txts.TEMP_SESSIONS, callback_data='add_temp_sessions')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])


# del

del_file_categories_value = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.FILE_BOOKLETS, callback_data='del_file_cat_booklets')],
    [InlineKeyboardButton(text=txts.FILE_BOOKS, callback_data='del_file_cat_books')],
    [InlineKeyboardButton(text=txts.FILE_BOT_PICS, callback_data='del_file_cat_pics')],
    [InlineKeyboardButton(text=txts.FILE_FORMATS, callback_data='del_file_cat_formats')],
    [InlineKeyboardButton(text=txts.FILE_EXTRAS, callback_data='del_file_cat_extras')],
    [InlineKeyboardButton(text=txts.FILE_SCHEDULE, callback_data='del_file_cat_schedule')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])


del_const_categories_value = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.CONST_LINKS, callback_data='del_const_cat_links')],
    [InlineKeyboardButton(text=txts.CONST_NEWCOMER, callback_data='del_const_cat_newcomer')],
    [InlineKeyboardButton(text=txts.CONST_CONTACTS, callback_data='del_const_cat_contacts')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])

del_temp_categories_value = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=txts.TEMP_SPEAKERS, callback_data='del_temp_cat_speakers')],
    [InlineKeyboardButton(text=txts.TEMP_SESSIONS, callback_data='del_temp_cat_sessions')],
    [InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')],
])

# cancel
cancel = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel')]])


# entry categories before delte
async def files_by_cat(category: str) -> InlineKeyboardMarkup:
    """Send a list of files of chosen category."""
    async with UnitOfWork(auto_commit=False) as uow:
        files = await uow.files.find(filters={'category': category, 'status': UploadState.UPLOADED})
    keyboard = InlineKeyboardBuilder()
    for file in files:
        keyboard.row(InlineKeyboardButton(text=file.name, callback_data=f'file_mes_{file.id}'))
    return cast(InlineKeyboardMarkup, keyboard.adjust(1).as_markup())


async def temp_by_cat(category: str) -> InlineKeyboardMarkup:
    """Send a list of temp messages of chosen category."""
    async with UnitOfWork(auto_commit=False) as uow:
        array = await uow.temp.find(filters={'category': category, 'status': UploadState.UPLOADED})
    keyboard = InlineKeyboardBuilder()
    if not array:
        keyboard.row(InlineKeyboardButton(text=txts.KB_NO_INFO,
                                        callback_data='no_info'))
    else:
        match category:
            case txts.TEMP_SPEAKERS:
                for temp_mes in array:
                    text, _parse = text_manager.get('KEYBOARD', 'TEMP_SPEAKER_ENTRY',
                                date=temp_mes.date, name=temp_mes.name)
                    keyboard.row(InlineKeyboardButton(text=text, callback_data=f'temp_mes_{temp_mes.id}'))

            case txts.TEMP_SESSIONS:
                for temp_mes in array:
                    text, _parse = text_manager.get('KEYBOARD', 'TEMP_SESSION_ENTRY',
                                date=temp_mes.date, name=temp_mes.name)
                    keyboard.row(InlineKeyboardButton(text=text, callback_data=f'temp_mes_{temp_mes.id}'))

    return cast(InlineKeyboardMarkup, keyboard.adjust(1).as_markup())


# delete entry
async def delete_file_entry_value(category: str) -> InlineKeyboardMarkup:
    """Send a list of files of chosen category for deletion."""
    async with UnitOfWork(auto_commit=False) as uow:
        array = await uow.files.find(filters={'category': category, 'status': UploadState.UPLOADED})
    keyboard = InlineKeyboardBuilder()
    if not array:
        keyboard.row(InlineKeyboardButton(text=txts.KB_NO_FILES, callback_data='no_action'))
    else:
        for file in array:
            keyboard.row(InlineKeyboardButton(text=file.name, callback_data=f'del_file_entry_{file.id}'))
        keyboard.row(InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel'))
    return cast(InlineKeyboardMarkup, keyboard.adjust(1).as_markup())


async def delete_temp_entry_value(user_id: int, category: str) -> InlineKeyboardMarkup | None:
    """Send a list of temp messages of chosen category for deletion."""
    async with UnitOfWork(auto_commit=False) as uow:
        user = await uow.users.get_by_filter(filters={'user_id': user_id})
        if not user:
            logger.warning('User missing in delete_temp_entry_value')
            return None
        if user.role in (UserRole.OWNER, UserRole.SUPERADMIN):
            all_temp = await uow.temp.find(filters={'category': category, 'status': UploadState.UPLOADED})
        else:
            all_temp = await uow.temp.find(filters={'category': category, 'admin_id': user_id,
                                                'status': UploadState.UPLOADED})
    keyboard = InlineKeyboardBuilder()
    array = list(all_temp)
    if not array:
        keyboard.row(InlineKeyboardButton(text=txts.KB_NO_TEMP, callback_data='no_action'))
    else:
        match category:
            case txts.TEMP_SPEAKERS:
                for temp_mes in array:
                    text, _parse = text_manager.get('KEYBOARD', 'TEMP_SPEAKER_ENTRY',
                                                    date=temp_mes.date, name=temp_mes.name)
                    keyboard.row(InlineKeyboardButton(text=text, callback_data=f'del_temp_entry_{temp_mes.id}'))

            case txts.TEMP_SESSIONS:
                for temp_mes in array:
                    text, _parse = text_manager.get('KEYBOARD', 'TEMP_SESSION_ENTRY', date=temp_mes.date,
                                                    name=temp_mes.name)
                    keyboard.row(InlineKeyboardButton(text=text, callback_data=f'del_temp_entry_{temp_mes.id}'))
        keyboard.row(InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel'))
    return cast(InlineKeyboardMarkup, keyboard.adjust(1).as_markup())


async def delete_const_entry_value(category: str) -> InlineKeyboardMarkup:
    """Send a list of const messages of chosen category for deletion."""
    async with UnitOfWork(auto_commit=False) as uow:
        array = await uow.const.find(filters={'category': category, 'status': UploadState.UPLOADED})
    keyboard = InlineKeyboardBuilder()
    if not array:
        keyboard.row(InlineKeyboardButton(text=txts.KB_NO_CONST, callback_data='no_action'))
    else:
        for mes in array:
            keyboard.row(InlineKeyboardButton(text=mes.name, callback_data=f'del_const_entry_{mes.id}'))
        keyboard.row(InlineKeyboardButton(text=txts.KB_CANCEL, callback_data='cancel'))
    return cast(InlineKeyboardMarkup, keyboard.adjust(1).as_markup())
