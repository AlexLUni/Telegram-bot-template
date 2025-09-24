class DatabaseError(Exception):
    """Base exception for all database-related errors."""


class NotUsableCodeError(DatabaseError):
    """Invite code cannot be used (already redeemed or invalid)."""


class NotFoundError(DatabaseError):
    """Requested database record was not found."""
