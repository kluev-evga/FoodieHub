"""константы"""
from django.utils.translation import gettext_lazy as translate

# --- DATABASE:
MIN_INT = 1
MAX_INT = 32000
MAX_CHAR = 200
MAX_TEXT = 5000
HEX_LENGTH = 7
MAX_CHAR_USER = 150
MAX_CHAR_EMAIL = 254
MAX_PASSWORD_LENGTH = 150
# --- QUERY PARAM:
MIN_INT_QUERY = 0
# --- ERR MESSAGE:
ERR_MSG_EMAIL = translate("A user with that email already exists")
ERR_MSG_USERNAME = translate("A user with that username already exists")
ERR_MSG_INT = translate("Accept values in between 1 and 32000"),
ERR_HEX = translate("invalid hex color, expected pattern: # + 6 hex digits")
ERR_NOT_EXIST = translate("not exist")
ERR_SELF_SUBSCRIBE = translate("you already subscribed on that user")
ERR_FAVOURITE = translate("already favorited")
# --- FILED HELP TEXT:
HELP_USERNAME = translate(("Username should have 254 symbols at the most"
                           " Allowed: letters, numbers, @/./+/-/_ only"))
