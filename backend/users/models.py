from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as translate


class User(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(
        translate('email address'),
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': translate('A user with that email already exists.')
        }
    )
    username = models.CharField(
        translate('username'),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': translate('A user with that username already exists.')
        },
        help_text=translate('Username should have 254 symbols at the most.'
                            'Allowed symbols: letters, numbers, @/./+/-/_ only')
    )
    first_name = models.CharField(
        translate('first name'),
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        translate('last name'),
        max_length=150,
        blank=False,
        null=False
    )

    class Meta:
        db_table = "auth_user"


class Subscribe(models.Model):
    """Модель подписки пользователей на других пользователей"""
    subscriber = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    subscription = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="subscription"  # USERS - @action subscriptions - GET
    )

    class Meta:
        db_table = "api_subscribe"
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscription'],
                name='unique user subscription'),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscription')),
                name='self subscription'
            )
        ]
