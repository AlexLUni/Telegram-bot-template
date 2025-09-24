import logging

from aiogram.filters import Filter
from aiogram.types import CallbackQuery, ContentType, Message

import app.const_texts as txts
from app.cache.user_cache import UserCache
from app.database.models.enums import UserRole
from app.database.models.user_states import UserState


logger = logging.getLogger(__name__)


class MessageFilter(Filter):
    """Filter that checks both user role and state for Message updates."""

    def __init__(self, role: UserRole | None = None, state: str | None = None) -> None:
        """Initiliaze MessageFilter."""
        self.required_role = role
        self.required_state = state

    async def __call__(self, message: Message) -> bool:
        """Check if user meets role and state requirements."""
        if not message.from_user:
            return False

        user_cache = UserCache.instance()
        user_data = user_cache.get_user(message.from_user.id)

        if not user_data:
            return False

        if self.required_role and not self._check_role_permission(user_data.role, self.required_role):
            return False

        if self.required_state and not user_data.state.startswith(self.required_state):
            return False

        if self.required_state:
            return self._check_content_type(message, user_data.state)

        return True

    @staticmethod
    def _check_role_permission(user_role: UserRole, required: UserRole) -> bool:
        """Check if user role meets or exceeds required level."""
        match required:
            case UserRole.OWNER:
                return user_role == UserRole.OWNER
            case UserRole.SUPERADMIN:
                return user_role in (UserRole.OWNER, UserRole.SUPERADMIN)
            case UserRole.ADMIN:
                return user_role in (UserRole.OWNER, UserRole.SUPERADMIN, UserRole.ADMIN)
            case _:
                return False

    @staticmethod
    def _check_content_type(message: Message, user_state: str) -> bool:
        """Check content type based on user state."""
        values_set = {
            txts.CMD_HELP[0], txts.CMD_FILES[0], txts.CMD_SPEAKERS[0], txts.CMD_SESSIONS[0], txts.CMD_NEWCOMER[0],
            txts.CMD_LINKS[0],
        }

        if user_state.startswith(UserState.FILE_UPLOAD) and message.content_type == ContentType.DOCUMENT:
            return True
        if user_state.startswith(UserState.PICS_UPLOAD) and message.content_type == ContentType.PHOTO:
            return True

        return bool(
            message.text
            and message.content_type == ContentType.TEXT
            and message.text not in values_set
            and not message.text.startswith('/'),
        )


class CallbackFilter(Filter):
    """Filter that checks both user role and state for CallbackQuery updates."""

    def __init__(self, role: UserRole | None = None, state: str | None = None) -> None:
        """Initiliaze CallbackFilter."""
        self.required_role = role
        self.required_state = state

    async def __call__(self, callback: CallbackQuery) -> bool:
        """Check if user meets role and state requirements."""
        if not callback.data or not callback.from_user:
            return False

        user_cache = UserCache.instance()
        user_data = user_cache.get_user(callback.from_user.id)

        if not user_data:
            return False

        if self.required_role and not self._check_role_permission(user_data.role, self.required_role):
            return False

        if self.required_state and not user_data.state.startswith(self.required_state):
            return False

        if self.required_state and callback.data:
            return self._check_callback_data(callback.data, user_data.state)

        return True

    @staticmethod
    def _check_role_permission(user_role: UserRole, required: UserRole) -> bool:
        """Check if user role meets or exceeds required level."""
        match required:
            case UserRole.OWNER:
                return user_role == UserRole.OWNER
            case UserRole.SUPERADMIN:
                return user_role in (UserRole.OWNER, UserRole.SUPERADMIN)
            case UserRole.ADMIN:
                return user_role in (UserRole.OWNER, UserRole.SUPERADMIN, UserRole.ADMIN)
            case _:
                return False

    @staticmethod
    def _check_callback_data(callback_data: str, state: str) -> bool:
        """Check if callback data matches the user state."""
        prefix_checks = {
            UserState.DELETE_CONST_CAT: 'del_const_cat_',
            UserState.DELETE_CONST_MES: 'del_const_entry_',
            UserState.DELETE_FILE_CAT: 'del_file_cat_',
            UserState.DELETE_FILE_MES: 'del_file_entry_',
            UserState.DELETE_TEMP_CAT: 'del_temp_cat_',
            UserState.DELETE_TEMP_MES: 'del_temp_entry_',
        }

        for state_prefix, callback_prefix in prefix_checks.items():
            if state.startswith(state_prefix):
                return callback_data.startswith(callback_prefix)
        return False
