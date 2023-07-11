from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as translate
import re

User = get_user_model()


def validate_not_zero(value):
    if value == 0:
        raise ValidationError(translate("value can not be zero"))


def validate_hex_color(value):
    pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    if not pattern.match(value):
        raise ValidationError(translate("value is not valid color"))


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_hex_color]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="tags"
    )
    image = models.ImageField(
        upload_to="recipe/"
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )
    text = models.TextField(
        max_length=5000,
        blank=False,
        null=False
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(
                1,
                "cooking time should be not less than one minute")
        ]
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )


class Amount(models.Model):
    amount = models.PositiveIntegerField(
        validators=[
            validate_not_zero,
            validators.MaxValueValidator(
                10000,
                translate("Not more than 10000"))
        ]
    )
    recipe = models.ManyToManyField(
        Recipe,
        related_name="ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
