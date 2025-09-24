from typing import NamedTuple, Optional

import app.constants as cnst
from app.database.models.enums import UserRole
from cachetools import TTLCache


class UserData(NamedTuple):
    """Complete user data for caching."""

    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    state: str
    role: UserRole


class UserCache:
    """In-memory user data caching with TTL."""

    _instance: Optional['UserCache'] = None
    _user_cache: TTLCache[int, UserData]

    def __init__(self) -> None:
        """Initialize cache with constants."""
        self._user_cache = TTLCache(maxsize=cnst.MAX_CACHE_SIZE, ttl=cnst.TIME_TO_LIVE)

    @classmethod
    def instance(cls) -> 'UserCache':
        """Singleton instance accessor."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_user(self, user_id: int) -> UserData | None:
        """Retrieve cached user data."""
        return self._user_cache.get(user_id)

    def set_user(self, user_data: UserData) -> None:
        """Cache user data."""
        self._user_cache[user_data.user_id] = user_data

    def clear(self, user_id: int) -> None:
        """Remove user data from cache."""
        self._user_cache.pop(user_id, None)

    def update_state(self, user_id: int, new_state: str) -> None:
        """Update only user state in cache."""
        if existing := self._user_cache.get(user_id):
            updated_user = UserData(
                user_id=existing.user_id,
                first_name=existing.first_name,
                last_name=existing.last_name,
                username=existing.username,
                state=new_state,
                role=existing.role,
            )
            self._user_cache[user_id] = updated_user


user_cache = UserCache.instance()
