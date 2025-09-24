from app.database.models.temp_message import TemporaryMessage

from .base import GenericSqlRepository


class TemporaryMessageRepository(GenericSqlRepository[TemporaryMessage]):
    """"Repository for TemporaryMessage."""

    model = TemporaryMessage
