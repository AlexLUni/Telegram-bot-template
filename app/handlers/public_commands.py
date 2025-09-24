import logging
import secrets

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import app.const_texts as txts
import app.constants as cnst
import app.keyboards as kb
from app.cache.user_cache import UserData
from app.database.models.enums import UploadState, UserRole
from app.database.models.user_states import UserState
from app.database.uow import UnitOfWork
from app.helpers import handle_errors
from app.services.text_manager import text_manager


logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.type.in_({'private'}))


@router.message(F.text.lower() == txts.HELLO[0])
@router.message(CommandStart())
@handle_errors
async def cmd_start(message: Message, user_data: UserData) -> None:
    """Handle the /start command, Send a greeting and a random image."""
    if not message.from_user:
        logger.warning('Message missing required attributes in cmd_start')
        return
    async with UnitOfWork(auto_commit=True) as uow:
        files = await uow.files.find(filters={'category': txts.FILE_BOT_PICS, 'status': UploadState.UPLOADED})
        await uow.users.upsert(
            conflict_columns=['user_id'],
            insert_values={
                'user_id': message.from_user.id,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name or None,
                'username': message.from_user.username or None,
                'state': UserState.DEFAULT,
                'role': UserRole.DEFAULT,
            },
            update_values={
                'user_id': message.from_user.id,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name or None,
                'username': message.from_user.username or None,
                'state': UserState.DEFAULT,
            },
        )
    if files:
        file = secrets.choice(files)
        await message.answer_photo(file.tg_id)

    text, parse_mode = text_manager.get('PUBLIC_COMMANDS', 'START', first_name=message.from_user.first_name)
    await message.answer(text, reply_markup=kb.main, parse_mode=parse_mode)


@router.message(F.text.lower() == txts.CMD_HELP_KB[0].lower())
@router.message(Command('help'))
@handle_errors
async def cmd_help(message: Message, user_data: UserData) -> None:
    """Send a list of available bot commands."""
    await message.answer(txts.CMD_HELP[0], txts.CMD_HELP[1])


@router.message(F.text.lower() == txts.CMD_FILES[0].lower())
@router.message(Command('files'))
@handle_errors
async def cmd_files(message: Message, user_data: UserData) -> None:
    """Send a list of categories of available files."""
    await message.answer(txts.CMD_FILE_CATEGORIES[0], txts.CMD_FILE_CATEGORIES[1],
                        reply_markup=kb.public_file_categories)


@router.message(F.text.lower() == txts.CMD_SPEAKERS[0].lower())
@router.message(Command('speakers'))
@handle_errors
async def cmd_speakers(message: Message, user_data: UserData) -> None:
    """Send a list of upcoming speaker meetings."""
    await message.answer(txts.CMD_UPCOMING_SPEAKERS[0], txts.CMD_UPCOMING_SPEAKERS[1],
                        reply_markup=await kb.temp_by_cat(txts.TEMP_SPEAKERS))


@router.message(F.text.lower() == txts.CMD_SESSIONS[0].lower())
@router.message(Command('sessions'))
@handle_errors
async def cmd_sessions(message: Message, user_data: UserData) -> None:
    """Send a list of upcoming sessions."""
    await message.answer(txts.CMD_UPCOMING_SESSIONS[0], txts.CMD_UPCOMING_SESSIONS[1],
                        reply_markup=await kb.temp_by_cat(txts.TEMP_SESSIONS))


@router.message(F.text.lower() == txts.CMD_UPCOMING_EVENTS[0].lower())
@router.message(Command('events'))
@handle_errors
async def cmd_events(message: Message, user_data: UserData) -> None:
    """Send a list of upcoming events which differ from previous categories."""
    await message.answer(txts.CMD_UPCOMING_EVENTS[0], txts.CMD_UPCOMING_EVENTS[1],
                        reply_markup=await kb.temp_by_cat(txts.TEMP_EVENTS))


@router.message(F.text.lower() == txts.CMD_OTHER_ITEMS[0].lower())
@router.message(Command('misc'))
@handle_errors
async def cmd_misc(message: Message, user_data: UserData) -> None:
    """Send a list of other materials which differ from previous categories."""
    await message.answer(txts.CMD_OTHER_ITEMS[0], txts.CMD_OTHER_ITEMS[1],
                        reply_markup=await kb.temp_by_cat(txts.TEMP_MISC))


@router.message(Command('contacts'))
@handle_errors
async def cmd_contacts(message: Message, user_data: UserData) -> None:
    """Send contact information."""
    if not message.bot:
        logger.warning('Message missing required attributes in cmd_contacts')
        return
    async with UnitOfWork(auto_commit=False) as uow:
        all_messages = await uow.const.find(filters={'category': txts.CONST_CONTACTS, 'status': UploadState.UPLOADED})
    for mes in all_messages:
        await message.bot.copy_message(message.chat.id, cnst.MSG_VAULT, mes.message_id)


@router.message(F.text.lower() == txts.CMD_LINKS[0].lower())
@router.message(Command('links'))
@handle_errors
async def cmd_links(message: Message, user_data: UserData) -> None:
    """Send useful links."""
    if not message.bot:
        logger.warning('Message missing required attributes in cmd_links')
        return
    async with UnitOfWork(auto_commit=False) as uow:
        all_messages = await uow.const.find(filters={'category': txts.CONST_LINKS, 'status': UploadState.UPLOADED})
        for mes in all_messages:
            await message.bot.copy_message(message.chat.id, cnst.MSG_VAULT, mes.message_id)


@router.message(F.text.lower() == txts.CMD_NEWCOMER[0].lower())
@router.message(Command('newcomer'))
@handle_errors
async def cmd_newcomer(message: Message, user_data: UserData) -> None:
    """Send information for newcomers."""
    if not message.bot:
        logger.warning('Message missing required attributes in cmd_newcomer')
        return
    async with UnitOfWork(auto_commit=False) as uow:
        all_messages = await uow.const.find(filters={'category': txts.CONST_NEWCOMER, 'status': UploadState.UPLOADED})
    for mes in all_messages:
        await message.bot.copy_message(message.chat.id, cnst.MSG_VAULT, mes.message_id)
