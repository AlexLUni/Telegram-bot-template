import logging
from datetime import datetime, timedelta

import app.constants as cnst
import pytz
from app.cache.code_entry_cache import code_entry_cache
from app.cache.user_cache import user_cache
from app.database.models import AdminInvite, User
from app.database.models.enums import UserRole
from app.database.models.user_states import UserState
from app.database.uow import UnitOfWork
from app.exceptions import NotFoundError, NotUsableCodeError
from app.helpers import create_random_code


logger = logging.getLogger(__name__)


class InviteManager:
    """Handle invitation creation and redemption for admin roles."""

    def __init__(self, uow: UnitOfWork | None = None):
        """Initiliaze manager with uow."""
        self.uow = uow or UnitOfWork(auto_commit=False)

    async def generate_invite(self, *, creator: dict[str, int | str | None], role: UserRole) -> str:
        """Generate a new invitation code for admin role."""
        code = f'AD_{create_random_code(cnst.CODE_LENGTH)}'
        creator_name = self._format_user_name(creator)

        async with self.uow:
            invite = AdminInvite(
                code=code,
                was_used=False,
                role=role,
                made_by_id=creator['user_id'],
                made_by_name=creator_name,
            )
            await self.uow.invites.add(invite)
            await self.uow.commit()

        return code

    async def use_invite(self, code: str, user_id: int, *, user: dict[str, int | str | None]) -> UserRole:
        """Redeem an invitation code and grant an admin role."""
        self._check_attempts(user_id)

        async with self.uow:
            try:
                invite = await self._get_valid_invite(code, user_id)
                user_name = self._format_user_name(user)
                current_user = await self.uow.users.get_by_filter(filters={'user_id': user_id})

                self._validate_invite_usage(invite, current_user)

                await self._update_user_role(user_id, user, invite.role)
                await self._mark_invite_used(code, user_id, user_name)

                user_cache.clear(user_id)
                return invite.role

            except Exception as e:
                if not isinstance(e, NotFoundError):
                    code_entry_cache.record_attempt(user_id)
                raise

    @staticmethod
    def _format_user_name(user_data: dict[str, int | str | None]) -> str:
        """Format user name from available data."""
        parts = []
        if user_data.get('first_name'):
            parts.append(str(user_data['first_name']))
        if user_data.get('last_name'):
            parts.append(str(user_data['last_name']))
        if user_data.get('username'):
            parts.append(f"@{user_data['username']}")
        return ' '.join(parts) if parts else 'Unknown'

    @staticmethod
    def _check_attempts(user_id: int) -> None:
        """Validate user attempt to use codes."""
        attempts, last_attempt = code_entry_cache.get_attempts(user_id)
        if attempts >= cnst.MAX_ATTEMPTS:
            if datetime.now(pytz.timezone('Europe/Moscow')) - last_attempt < timedelta(seconds=cnst.BLOCK_TIME):
                raise NotUsableCodeError('too_many_attempts')
            code_entry_cache.reset_attempts(user_id)

    async def _get_valid_invite(self, code: str, user_id: int) -> AdminInvite:
        """Retrieve and validate invitation."""
        invite = await self.uow.invites.get_by_filter(filters={'code': code})
        if not invite:
            logger.warning('Invalid code attempt')
            code_entry_cache.record_attempt(user_id)
            raise NotFoundError
        return invite

    @staticmethod
    def _validate_invite_usage(invite: AdminInvite, user: User | None) -> None:
        """Check if the invite can be used."""
        if invite.was_used:
            raise NotUsableCodeError('already_used')
        if user and user.role in (UserRole.SUPERADMIN, UserRole.OWNER):
            raise NotUsableCodeError('already_superadmin')
        if user and user.role == UserRole.ADMIN and invite.role == UserRole.ADMIN:
            raise NotUsableCodeError('already_admin')

    async def _update_user_role(self, user_id: int, user_data: dict[str, int | str | None], role: UserRole) -> None:
        """Update or create a user entry with new role."""
        await self.uow.users.upsert(
            conflict_columns=['user_id'],
            insert_values={
                'user_id': user_id,
                'first_name': user_data['first_name'],
                'last_name': user_data.get('last_name'),
                'username': user_data.get('username'),
                'state': UserState.DEFAULT,
                'role': role,
            },
            update_values={'role': role},
        )

    async def _mark_invite_used(self, code: str, user_id: int, user_name: str) -> None:
        """Mark invitation as used."""
        await self.uow.invites.update_fields(
            filters={'code': code},
            update_values={
                'was_used': True,
                'used_by_id': user_id,
                'used_by_name': user_name,
            },
        )
        await self.uow.commit()
