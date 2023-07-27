import re

from django.core.exceptions import ValidationError
from django.core import validators

from backend import const


def validate_small_integer():
    """Валидирует число в диапазоне 1...32000"""
    return [validators.MinValueValidator(const.MIN_INT, const.ERR_MSG_INT),
            validators.MaxValueValidator(const.MAX_INT, const.ERR_MSG_INT)]


def validate_hex_color(value):
    """Валидирует цветовой код, допустимый формат: # + 6 знаков"""
    pattern = re.compile(r"^#([A-Fa-f0-9]{6})$")
    if not pattern.match(value):
        raise ValidationError(const.ERR_HEX)
