from typing import Optional

from app.cache.user_cache import UserCache, UserData
from app.database.models import User
from app.database.models.enums import UserRole
from app.database.models.user_states import UserState
from app.database.uow import UnitOfWork
from app.exceptions import NotFoundError


async def get_user_with_cache(user_id: int) -> UserData | None:
    """Get complete user data with cache."""
    cache = UserCache.instance()
    if cached_user := cache.get_user(user_id):
        if cached_user.role != UserRole.DEFAULT:
            async with UnitOfWork() as uow:
                try:
                    db_user = await uow.users.get_by_filter(filters={'user_id': user_id})
                    if db_user and db_user.state != cached_user.state:
                        user_data = UserData(
                            user_id=db_user.user_id,
                            first_name=db_user.first_name or None,
                            last_name=db_user.last_name or None,
                            username=db_user.username or None,
                            state=db_user.state,
                            role=db_user.role,
                        )
                        cache.set_user(user_data)
                        return user_data
                except NotFoundError:
                    cache.clear(user_id)
                    return None
        return cached_user

    async with UnitOfWork() as uow:
        try:
            db_user = await uow.users.get_by_filter(filters={'user_id': user_id})
            if db_user:
                user_data = UserData(
                    user_id=db_user.user_id,
                    first_name=db_user.first_name or None,
                    last_name=db_user.last_name or None,
                    username=db_user.username or None,
                    state=db_user.state,
                    role=db_user.role,
                )
                cache.set_user(user_data)
                return user_data
        except NotFoundError:
            return None

    return None


async def update_user_state(user_id: int, new_state: str) -> None:
    """Update user state in both DB and cache."""
    async with UnitOfWork(auto_commit=True) as uow:
        await uow.users.update_fields(
            filters={'user_id': user_id},
            update_values={'state': new_state},
        )

    cache = UserCache.instance()
    cache.update_state(user_id, new_state)


async def create_user_if_not_exists(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
) -> UserData:
    """Create user if doesn't exist and return user data."""
    cache = UserCache.instance()

    if existing := cache.get_user(user_id):
        return existing

    async with UnitOfWork(auto_commit=True) as uow:
        try:
            user = await uow.users.get_by_filter(filters={'user_id': user_id})
        except NotFoundError:
            user = User(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                state=UserState.DEFAULT,
                role=UserRole.DEFAULT,
            )
            await uow.users.add(user)

        if user is None:
            user = User(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                state=UserState.DEFAULT,
                role=UserRole.DEFAULT,
            )
            await uow.users.add(user)

        user_data = UserData(
            user_id=user.user_id,
            first_name=user.first_name or None,
            last_name=user.last_name or None,
            username=user.username or None,
            state=user.state,
            role=user.role,
        )
        cache.set_user(user_data)
        return user_data
