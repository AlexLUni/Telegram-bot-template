from app.database.models.const_message import ConstantMessage

from .base import GenericSqlRepository


class ConstantMessageRepository(GenericSqlRepository[ConstantMessage]):
    """"Repository for ConstantMessage."""

    model = ConstantMessage
