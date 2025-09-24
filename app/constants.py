from app.database.models.enums import UserRole


# CONSTANTS
ATTEMPTS_RESET_TIME = 300
ATTEMPTS_TTL = 3600
BLOCK_TIME = 3600
CODE_LENGTH = 16
DELETE_HOUR = 8
DELETE_MINUTE = 30
DUMMY_TOKEN = 'dummy_token'  # noqa: S105
MAX_ATTEMPTS = 5
MAX_CACHE_SIZE = 512
MISFIRE_GRACE_TIME = 60 * 60 * 3
POLLING_RELAX = 0.1
POLLING_TIMEOUT = 60
TIME_TO_LIVE = 600

# TEXTS_PATH
TEXTS_PATH = 'app/texts.json'

# CALLBACK_LENGTH
CHOOSE_ROLE = 3

# INITIAL ADMINS
'''ADMIN_IDS = {
    0000000000: {
        'first_name': 'name1',
        'last_name': 'name2',
        'username': 'name3',
        'role': UserRole.OWNER,
    },
}

# MESSAGES VAULT
MSG_VAULT = 0000000000'''
