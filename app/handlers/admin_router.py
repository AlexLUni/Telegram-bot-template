import locale
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

import app.const_texts as txts
import app.constants as cnst
import app.keyboards as kb
from app.cache.code_entry_cache import code_entry_cache
from app.cache.user_cache import UserData
from app.database.models.enums import UserRole
from app.database.uow import UnitOfWork
from app.exceptions import NotFoundError, NotUsableCodeError
from app.filters import CallbackFilter, MessageFilter
from app.helpers import handle_errors
from app.metrics import get_metrics
from app.services.invite_manager import InviteManager
from app.services.text_manager import text_manager


logger = logging.getLogger(__name__)

router = Router()
router.message.filter(F.chat.type.in_({'private'}))


@router.message(Command('adminhelp'), MessageFilter(role=UserRole.ADMIN))
@handle_errors
async def admin_help(message: Message, user_data: UserData) -> None:
    """Send a list of admin commands for different roles."""
    if user_data.role in (UserRole.SUPERADMIN, UserRole.OWNER):
        await message.answer(txts.SUPERADMIN_HELP[0] + txts.ADMIN_HELP[0], txts.SUPERADMIN_HELP[1])
    else:
        await message.answer(txts.ADMIN_HELP[0], parse_mode=txts.ADMIN_HELP[1])


@router.message(Command('adminlist'), MessageFilter(role=UserRole.ADMIN))
@handle_errors
async def admin_list(message: Message, user_data: UserData) -> None:
    """Send a list of current admins."""
    async with UnitOfWork(auto_commit=False) as uow:
        owner = list(await uow.users.find(filters={'role': UserRole.OWNER}))
        admins = list(await uow.users.find(filters={'role': UserRole.ADMIN}))
        superadmins = list(await uow.users.find(filters={'role': UserRole.SUPERADMIN}))
        all_admins = owner + admins + superadmins
        for admin in all_admins:
            name = f"{admin.last_name or ''} {admin.first_name or ''} {admin.username or ''}".strip()
            text, parse_mode = text_manager.get('ADMIN', 'ADMIN_LIST', role=admin.role, name=name)
            await message.answer(text, parse_mode=parse_mode)


@router.message(Command('addadmin'), MessageFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def cmd_addadmin(message: Message, user_data: UserData) -> None:
    """Send two choices for adding: admin or superadmin."""
    if not message.from_user:
        logger.warning('Message missing required attributes in cmd_addadmin')
        return
    if user_data.role == UserRole.OWNER:
        await message.answer(txts.CHOOSE_ROLE[0], reply_markup=kb.choose_role_owner, parse_mode=txts.CHOOSE_ROLE[1])
    else:
        await message.answer(txts.CHOOSE_ROLE[0], reply_markup=kb.choose_role_superadmin,
                            parse_mode=txts.CHOOSE_ROLE[1])


@router.callback_query(F.data.startswith('choose_role_'), CallbackFilter(role=UserRole.SUPERADMIN))
@handle_errors
async def create_new_invite(callback: CallbackQuery, user_data: UserData) -> None:
    """Send a new admin/superadmin invitation code."""
    if not callback.message or not callback.data or not callback.from_user:
        logger.warning('Callback missing required attributes in new_invite')
        return
    if len(callback.data.split('_')) < cnst.CHOOSE_ROLE:
        logger.error('Invalid callback data format in new_invite: %s', callback.data)
        return
    role_type = callback.data.split('_')[2]
    match role_type:
        case 'admin':
            role = UserRole.ADMIN
            role_str = txts.ROLE_ADMIN[0]
        case 'superadmin':
            role = UserRole.SUPERADMIN
            role_str = txts.ROLE_SUPERADMIN[0]
    invite_manager = InviteManager()
    creator_data: dict[str, int | str | None] = {
        'user_id': int(callback.from_user.id),
        'first_name': str(callback.from_user.first_name),
        'last_name': str(callback.from_user.last_name) if callback.from_user.last_name else None,
        'username': str(callback.from_user.username) if callback.from_user.username else None,
    }
    invite_code = await invite_manager.generate_invite(creator=creator_data, role=role)
    text, parse_mode = text_manager.get('ADMIN', 'CALLBACK_INVITE', role=role_str, code=invite_code)
    await callback.message.answer(text=text, parse_mode=parse_mode)
    await callback.answer()


@router.message(F.text.startswith('AD_'))
@handle_errors
async def enter_invite(message: Message, user_data: UserData) -> None:
    """Use code and add admin."""
    if not message.from_user or not message.text:
        logger.warning('Message missing required attributes in enter_invite')
        return
    invite_manager = InviteManager()
    try:
        user_data_dict: dict[str, int | str | None] = {
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name or None,
            'username': message.from_user.username or None,
        }
        role = await invite_manager.use_invite(code=message.text, user_id=message.from_user.id, user=user_data_dict)
        match role:
            case UserRole.ADMIN:
                role_str = txts.ROLE_ADMIN[0]
            case UserRole.SUPERADMIN:
                role_str = txts.ROLE_SUPERADMIN[0]
        text, parse_mode = text_manager.get('ADMIN', 'SUCCESS_ADMIN_ADDED', role=role_str)
        await message.answer(text=text, reply_markup=kb.main, parse_mode=parse_mode)
    except NotFoundError:
        attempts, _ = code_entry_cache.get_attempts(message.from_user.id)
        text, parse_mode = text_manager.get('ADMIN', 'CALLBACK_CODE_INVALID',
                                        number=cnst.MAX_ATTEMPTS - attempts)
        await message.answer(text, parse_mode)
        if cnst.MAX_ATTEMPTS - attempts == 0:
            text, parse_mode = text_manager.get('ADMIN', 'TOO_MANY_ATTEMPTS', block_time=cnst.BLOCK_TIME)
            await message.answer(text, parse_mode)
        return
    except NotUsableCodeError as e:
        await _admin_invite_error_parser(str(e), message)


async def _admin_invite_error_parser(err: str, message: Message) -> None:
    """Parse admin inviting errors."""
    match err:
        case 'too_many_attempts':
            text, parse_mode = text_manager.get('ADMIN', 'TOO_MANY_ATTEMPTS', block_time=cnst.BLOCK_TIME)
            await message.answer(text, parse_mode)
        case 'already_used':
            await message.answer(txts.CALLBACK_INVITE_ALREADY_USED[0],
                                parse_mode=txts.CALLBACK_INVITE_ALREADY_USED[1])
        case 'already_superadmin':
            await message.answer(txts.CALLBACK_INVITE_ALREADY_SUPERADMIN[0],
                                parse_mode=txts.CALLBACK_INVITE_ALREADY_SUPERADMIN[1])
        case 'already_admin':
            await message.answer(txts.CALLBACK_INVITE_ALREADY_ADMIN[0],
                parse_mode=txts.CALLBACK_INVITE_ALREADY_ADMIN[1])


@router.message(Command('metrics'), MessageFilter(role=UserRole.OWNER))
@handle_errors
async def handle_metrics_command(message: Message, user_data: UserData) -> None:
    """Send metrics in a txt format via telegram."""
    try:
        metrics_text = get_metrics()
        with NamedTemporaryFile(mode='w', encoding=locale.getpreferredencoding(do_setlocale=False), suffix='.txt',
                                delete=False) as temp_file:
            temp_file.write(metrics_text)
            temp_file_path = temp_file.name
        await message.reply_document(document=FSInputFile(temp_file_path), caption='Current metrics')
        Path(temp_file_path).unlink()
    except OSError:
        logger.exception('Error while deleting metrics tempfile')
    except Exception as e:
        await message.answer(f'Error getting metrics: {e!s}')
