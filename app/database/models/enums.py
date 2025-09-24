from enum import Enum


class UserRole(str, Enum):
    DEFAULT = 'default'
    ADMIN = 'admin'
    SUPERADMIN = 'superadmin'
    OWNER = 'owner'


class UploadState(str, Enum):
    UPLOADED = 'uploaded'
    UNFINISHED = 'unfinished'
    DELETED = 'deleted'
