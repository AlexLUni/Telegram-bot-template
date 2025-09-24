from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base
from app.database.models.enums import UploadState


class File(Base):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(String(128), nullable=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    category: Mapped[str] = mapped_column(String(40))
    status: Mapped[UploadState] = mapped_column(Enum(UploadState, name='upload_state'), index=True)
