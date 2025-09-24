from collections.abc import Sequence
from datetime import datetime
from typing import Generic, TypeVar

from sqlalchemy import and_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.base import Base
from app.exceptions import NotFoundError


ModelType = TypeVar('ModelType', bound=Base)


class GenericSqlRepository(Generic[ModelType]):
    """Generic repository encapsulating common database operations."""

    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        """"Initialize repository."""
        self.session = session

    async def get_by_id(self, entity_id: int) -> ModelType:
        """Retrieve entity by primary key."""
        entity = await self.session.get(self.model, entity_id)
        if not entity:
            raise NotFoundError(f'{self.model.__name__} {entity_id} not found')
        return entity

    async def get_by_filter(self, filters: dict[str, int | str | None]) -> ModelType | None:
        """Get single entity matching filter criteria."""
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def find(self, filters: dict[str, int | str | None]) -> Sequence[ModelType]:
        """Find all entities matching filter criteria."""
        stmt = select(self.model)
        if filters:
            where_clauses = [getattr(self.model, k) == v for k, v in filters.items()]
            stmt = stmt.where(and_(*where_clauses))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, entity: ModelType) -> ModelType:
        """Add new entity to database."""
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """Update existing entity."""
        merged = await self.session.merge(entity)
        await self.session.flush()
        return merged

    async def update_fields(self,
                           filters: dict[str, int | str | datetime | list[str] | None],
                           update_values: dict[str, int | str | datetime | list[str] | list[int] | None]) -> ModelType:
        """Update entity fields based on filters."""
        if not filters:
            raise ValueError('Filters required for update operation')

        stmt = (
            update(self.model)
            .where(and_(*[getattr(self.model, key) == value for key, value in filters.items()]))
            .values(**update_values)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        updated_entity = result.scalar_one_or_none()

        if updated_entity is None:
            raise NotFoundError(f'{self.model.__name__} not found with filters: {filters}')

        return updated_entity

    async def upsert(self,
                    conflict_columns: list[str],
                    insert_values: dict[str, int | str | None],
                    update_values: dict[str, int | str | None]) -> ModelType | None:
        """Upsert operation - insert or update on conflict."""
        stmt: Insert = (
            pg_insert(self.model)  # type: ignore[no-untyped-call]
            .values(**insert_values)
            .on_conflict_do_update(
                index_elements=conflict_columns,
                set_=update_values,
            )
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_do_nothing(self,
                               conflict_columns: list[str],
                               insert_values: dict[str, int | str | None]) -> ModelType | None:
        """Insert or do nothing on conflict."""
        stmt: Insert = (
            pg_insert(self.model)  # type: ignore[no-untyped-call]
            .values(**insert_values)
            .on_conflict_do_nothing(index_elements=conflict_columns)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, entity: ModelType) -> None:
        """Remove entity from database."""
        await self.session.delete(entity)
        await self.session.flush()
