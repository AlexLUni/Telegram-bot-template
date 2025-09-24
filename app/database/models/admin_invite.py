from sqlalchemy import BigInteger, Boolean, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base
from app.database.models.enums import UserRole


class AdminInvite(Base):
    __tablename__ = 'admin_invites'
    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    was_used: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name='user_role', create_type=False))
    made_by_id: Mapped[int] = mapped_column(BigInteger)
    made_by_name: Mapped[str] = mapped_column(String(256))
    used_by_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    used_by_name: Mapped[str] = mapped_column(String(256), nullable=True)

    __table_args__ = (Index('unq_active_invite_code', 'code', unique=True, postgresql_where=(was_used is False)),)
