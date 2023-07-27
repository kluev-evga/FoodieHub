from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from backend import const


class User(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(
        "адрес электронной почты",
        max_length=const.MAX_CHAR_EMAIL,
        unique=True,
        blank=False,
        null=False,
        error_messages={"unique": const.ERR_MSG_EMAIL})
    username = models.CharField(
        "имя пользователя",
        max_length=const.MAX_CHAR_USER,
        unique=True,
        blank=False,
        null=False,
        validators=[UnicodeUsernameValidator()],
        error_messages={"unique": const.ERR_MSG_USERNAME},
        help_text=const.HELP_USERNAME)
    first_name = models.CharField(
        "имя",
        max_length=const.MAX_CHAR_USER,
        blank=False,
        null=False)
    last_name = models.CharField(
        "фамилия",
        max_length=const.MAX_CHAR_USER,
        blank=False,
        null=False)

    class Meta:
        db_table = "auth_user"
        ordering = ("username",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
