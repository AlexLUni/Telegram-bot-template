from config import config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class AsyncSessionFactory:
    """Factory for creating async database sessions for UoW."""

    def __init__(self) -> None:
        """Initialize with database configuration."""
        self.engine = create_async_engine(url=config['database']['url'])
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
        )

    def __call__(self) -> AsyncSession:
        """Create and return new async session."""
        return self.session_factory()


session_factory = AsyncSessionFactory()
