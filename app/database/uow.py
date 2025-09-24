from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.const_repo import ConstantMessageRepository
from app.database.repositories.file_repo import FileRepository
from app.database.repositories.invite_repo import InviteRepository
from app.database.repositories.temp_repo import TemporaryMessageRepository
from app.database.repositories.user_repo import UserRepository
from app.database.session import session_factory


class UnitOfWork:
    """Async Unit of Work pattern for transaction and repository management."""

    def __init__(self, *, auto_commit: bool = False) -> None:
        """Initialize UoW with session, repositories and auto-commit flag."""
        self.session: AsyncSession = session_factory()
        self.const: ConstantMessageRepository = ConstantMessageRepository(self.session)
        self.temp: TemporaryMessageRepository = TemporaryMessageRepository(self.session)
        self.invites: InviteRepository = InviteRepository(self.session)
        self.users: UserRepository = UserRepository(self.session)
        self.files: FileRepository = FileRepository(self.session)
        self.auto_commit = auto_commit

    async def __aenter__(self) -> 'UnitOfWork':
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager with exception handling."""
        if exc_type:
            await self.rollback()
        elif self.auto_commit:
            await self.commit()
        await self.session.close()

    async def commit(self) -> None:
        """Commit all pending changes to database."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback all uncommitted changes."""
        await self.session.rollback()
