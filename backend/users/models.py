from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as translate


class User(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(
        translate("email address"),
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        error_messages={
            "unique": translate("A user with that email already exists.")})
    username = models.CharField(
        translate("username"),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": translate("A user with that username already exists.")},
        help_text=translate("Username should have 254 symbols at the most."
                            "Allowed: letters, numbers, @/./+/-/_ only"))
    first_name = models.CharField(
        translate("first name"),
        max_length=150,
        blank=False,
        null=False)
    last_name = models.CharField(
        translate("last name"),
        max_length=150,
        blank=False,
        null=False)

    class Meta:
        db_table = "auth_user"
        ordering = ("username",)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
