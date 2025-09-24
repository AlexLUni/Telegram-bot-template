from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base
from app.database.models.enums import UploadState


class ConstantMessage(Base):
    __tablename__ = 'constant_messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id = mapped_column(BigInteger, ForeignKey('users.user_id'))
    chat_id = mapped_column(BigInteger)
    message_id = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    category: Mapped[str] = mapped_column(String(40))
    status: Mapped[UploadState] = mapped_column(Enum(UploadState, name='upload_state'), index=True)
