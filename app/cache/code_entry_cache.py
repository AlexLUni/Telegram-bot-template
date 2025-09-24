from datetime import datetime, timedelta
from typing import Optional

import app.constants as cnst
import pytz
from cachetools import TTLCache


class CodeEntryCache:
    """Tracks and manages code attempt limits with TTL caching."""

    _instance: Optional['CodeEntryCache'] = None
    _attempts: TTLCache[int, tuple[int, datetime]]

    def __init__(self) -> None:
        """Cache initialization."""
        self._attempts = TTLCache(maxsize=cnst.MAX_CACHE_SIZE, ttl=cnst.ATTEMPTS_TTL)

    @classmethod
    def get(cls) -> 'CodeEntryCache':
        """Get singleton cache instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def record_attempt(self, user_id: int) -> tuple[int, datetime]:
        """Record new attempt and return current attempt count."""
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        current_attempts, last_attempt = self._attempts.get(user_id, (0, now))

        if now - last_attempt > timedelta(seconds=cnst.ATTEMPTS_RESET_TIME):
            current_attempts = 0

        current_attempts += 1
        self._attempts[user_id] = (current_attempts, now)
        return current_attempts, last_attempt

    def get_attempts(self, user_id: int) -> tuple[int, datetime]:
        """Get current attempt count and last attempt time."""
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        return self._attempts.get(user_id, (0, now))

    def reset_attempts(self, user_id: int) -> None:
        """Clear attempt counter for user."""
        self._attempts.pop(user_id, None)


code_entry_cache = CodeEntryCache.get()
