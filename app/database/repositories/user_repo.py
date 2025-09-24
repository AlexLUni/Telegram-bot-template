from app.database.models.user import User

from .base import GenericSqlRepository


class UserRepository(GenericSqlRepository[User]):
    """"Repository for User."""

    model = User
