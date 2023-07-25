import re

from django.core.exceptions import ValidationError
from django.core import validators
from django.utils.translation import gettext_lazy as translate


def validate_small_integer():
    """Валидирует число в диапазоне 1...32000"""
    message = translate("Accept values in between 1 and 32000")
    return [validators.MinValueValidator(1, message),
            validators.MaxValueValidator(32000, message)]


def validate_hex_color(value):
    """Валидирует цветовой код, допустимый формат: # + 6 знаков"""
    pattern = re.compile(r"^#([A-Fa-f0-9]{6})$")
    if not pattern.match(value):
        message = "Невалидный  hex код, ожидаемый формат: # + 6 знаков"
        raise ValidationError(message)
