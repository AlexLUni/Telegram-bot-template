from app.services.text_manager import text_manager


def _get_data(category: str, key: str) -> tuple[str, str | None]:
    return text_manager.get(category, key)


def _get_text(category: str, key: str) -> str:
    return text_manager.get(category, key)[0]

# Public commands (no placeholders)


CMD_FILE_CATEGORIES = _get_data('PUBLIC_COMMANDS', 'FILE_CATEGORIES')
CMD_HELP = _get_data('PUBLIC_COMMANDS', 'HELP')
CMD_OTHER_ITEMS = _get_data('PUBLIC_COMMANDS', 'OTHER_ITEMS')
CMD_UPCOMING_EVENTS = _get_data('PUBLIC_COMMANDS', 'UPCOMING_EVENTS')
CMD_UPCOMING_SESSIONS = _get_data('PUBLIC_COMMANDS', 'UPCOMING_SESSIONS')
CMD_UPCOMING_SPEAKERS = _get_data('PUBLIC_COMMANDS', 'UPCOMING_SPEAKERS')

# Adding or deleting any of the entries (no placeholders)
ADD_CONST_CATEGORY = _get_data('ADD_DEL_ENTRY', 'ADD_CONST_CATEGORY')
ADD_CONST_MESSAGE = _get_data('ADD_DEL_ENTRY', 'ADD_CONST_MESSAGE')
ADD_CONST_NAME = _get_data('ADD_DEL_ENTRY', 'ADD_CONST_NAME')
ADD_FILE = _get_data('ADD_DEL_ENTRY', 'ADD_FILE')
ADD_FILE_CATEGORY = _get_data('ADD_DEL_ENTRY', 'ADD_FILE_CATEGORY')
ADD_PIC = _get_data('ADD_DEL_ENTRY', 'ADD_PIC')
ADD_TEMP_CATEGORY = _get_data('ADD_DEL_ENTRY', 'ADD_TEMP_CATEGORY')
ADD_TEMP_DATE = _get_data('ADD_DEL_ENTRY', 'ADD_TEMP_DATE')
ADD_TEMP_MESSAGE = _get_data('ADD_DEL_ENTRY', 'ADD_TEMP_MESSAGE')
ADD_TEMP_NAME = _get_data('ADD_DEL_ENTRY', 'ADD_TEMP_NAME')
CHOOSE_MESSAGE = _get_data('ADD_DEL_ENTRY', 'CHOOSE_MESSAGE')
CONST_ADDED = _get_data('ADD_DEL_ENTRY', 'CONST_ADDED')
DEL_CONST_CATEGORY = _get_data('ADD_DEL_ENTRY', 'DEL_CONST_CATEGORY')
DEL_FILE_CATEGORY = _get_data('ADD_DEL_ENTRY', 'DEL_FILE_CATEGORY')
DEL_TEMP_CATEGORY = _get_data('ADD_DEL_ENTRY', 'DEL_TEMP_CATEGORY')
ENTRY_DELETED = _get_data('ADD_DEL_ENTRY', 'ENTRY_DELETED')
FILE_ADDED = _get_data('ADD_DEL_ENTRY', 'FILE_ADDED')
PIC_ADDED = _get_data('ADD_DEL_ENTRY', 'PIC_ADDED')
TEMP_ADDED = _get_data('ADD_DEL_ENTRY', 'TEMP_ADDED')

# Admin related (no placeholders)
ADMIN_HELP = _get_data('ADMIN', 'ADMIN_HELP')
CALLBACK_INVITE_ALREADY_ADMIN = _get_data('ADMIN', 'CALLBACK_INVITE_ALREADY_ADMIN')
CALLBACK_INVITE_ALREADY_SUPERADMIN = _get_data('ADMIN', 'CALLBACK_INVITE_ALREADY_SUPERADMIN')
CALLBACK_INVITE_ALREADY_USED = _get_data('ADMIN', 'CALLBACK_INVITE_ALREADY_USED')
CANCEL = _get_data('ADMIN', 'CANCEL')
CHOOSE_ROLE = _get_data('ADMIN', 'CHOOSE_ROLE')
ROLE_ADMIN = _get_data('ADMIN', 'ROLE_ADMIN')
ROLE_SUPERADMIN = _get_data('ADMIN', 'ROLE_SUPERADMIN')
SUPERADMIN_HELP = _get_data('ADMIN', 'SUPERADMIN_HELP')

# Menu and commands (no placeholders)
HELLO = _get_data('MENU_AND_COMMANDS', 'HELLO')
CMD_HELP_KB = _get_data('MENU_AND_COMMANDS', 'CMD_HELP')
CMD_FILES = _get_data('MENU_AND_COMMANDS', 'CMD_FILES')
CMD_SPEAKERS = _get_data('MENU_AND_COMMANDS', 'CMD_SPEAKERS')
CMD_SESSIONS = _get_data('MENU_AND_COMMANDS', 'CMD_SESSIONS')
CMD_NEWCOMER = _get_data('MENU_AND_COMMANDS', 'CMD_NEWCOMER')
CMD_LINKS = _get_data('MENU_AND_COMMANDS', 'CMD_LINKS')

# Errors (no placeholders)
ERR_INVALID_DATE = _get_data('ERRORS', 'INVALID_DATE')
ERR_INVALID_TIME = _get_data('ERRORS', 'INVALID_TIME')
ERR_FILE_EXISTS = _get_data('ERRORS', 'FILE_EXISTS')
ERR_NOT_FOUND = _get_data('ERRORS', 'NOT_FOUND')

# Categories
FILE_BOOKLETS = _get_text('FILES', 'BOOKLETS')
FILE_BOOKS = _get_text('FILES', 'BOOKS')
FILE_BOT_PICS = _get_text('FILES', 'BOT_PICS')
FILE_FORMATS = _get_text('FILES', 'FORMATS')
FILE_EXTRAS = _get_text('FILES', 'EXTRAS')
FILE_SCHEDULE = _get_text('FILES', 'SCHEDULE')

DAY_MONDAY = _get_text('DAYS', 'MONDAY')
DAY_TUESDAY = _get_text('DAYS', 'TUESDAY')
DAY_WEDNESDAY = _get_text('DAYS', 'WEDNESDAY')
DAY_THURSDAY = _get_text('DAYS', 'THURSDAY')
DAY_FRIDAY = _get_text('DAYS', 'FRIDAY')
DAY_SATURDAY = _get_text('DAYS', 'SATURDAY')
DAY_SUNDAY = _get_text('DAYS', 'SUNDAY')
DAY_DAILY = _get_text('DAYS', 'DAILY')

CONST_LINKS = _get_text('CONST', 'LINKS')
CONST_NEWCOMER = _get_text('CONST', 'NEWCOMER')
CONST_CONTACTS = _get_text('CONST', 'CONTACTS')

TEMP_SPEAKERS = _get_text('TEMP', 'SPEAKERS')
TEMP_SESSIONS = _get_text('TEMP', 'SESSIONS')
TEMP_EVENTS = _get_text('TEMP', 'EVENTS')
TEMP_MISC = _get_text('TEMP', 'MISC')

KB_ROLE_ADMIN = _get_text('ROLES', 'ADMIN')
KB_ROLE_SUPERADMIN = _get_text('ROLES', 'SUPERADMIN')

# Keyboard
KB_CANCEL = _get_text('KEYBOARD', 'CANCEL')
KB_NO_CONST = _get_text('KEYBOARD', 'NO_CONST')
KB_NO_FILES = _get_text('KEYBOARD', 'NO_FILES')
KB_NO_INFO = _get_text('KEYBOARD', 'NO_INFO')
KB_NO_TEMP = _get_text('KEYBOARD', 'NO_TEMP')
KB_PLACEHOLDER = _get_text('KEYBOARD', 'PLACEHOLDER')
