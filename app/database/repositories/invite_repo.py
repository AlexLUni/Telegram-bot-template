from app.database.models.admin_invite import AdminInvite

from .base import GenericSqlRepository


class InviteRepository(GenericSqlRepository[AdminInvite]):
    """"Repository for Invite."""

    model = AdminInvite
