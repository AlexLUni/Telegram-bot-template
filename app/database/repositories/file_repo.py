from app.database.models.file import File

from .base import GenericSqlRepository


class FileRepository(GenericSqlRepository[File]):
    """"Repository for File."""

    model = File
