from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from recipies.validators import validate_hex_color, validate_small_integer

User = get_user_model()


class Recipe(models.Model):
    """Таблица рецепта"""
    author = models.ForeignKey(
        User,
        verbose_name="автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes")
    tags = models.ManyToManyField(
        "Tag",
        "теги")
    image = models.ImageField(
        "фото рецепта",
        upload_to="recipe/")
    name = models.CharField(
        "название рецепта",
        max_length=200)
    text = models.TextField(
        "описание рецепта",
        max_length=5000)
    cooking_time = models.PositiveSmallIntegerField(
        "время приготовления",
        validators=validate_small_integer())
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="RecipeIngredient")
    pub_date = models.DateTimeField(
        "дата публикации",
        auto_now_add=True,
        editable=False)

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return f'"{self.author}" >>> "{self.name}"'


class RecipeIngredient(models.Model):
    """Промежуточная таблица recipe -> ingredient
       дополнительно содержит amount ингредиента"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="рецепт",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients")
    ingredient = models.ForeignKey(
        "Ingredient",
        verbose_name="ингредиент",
        on_delete=models.CASCADE,
        related_name="ingredients_recipe")
    amount = models.PositiveSmallIntegerField(
        "количество ингредиента",
        validators=validate_small_integer())

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        ordering = ("recipe",)


class Ingredient(models.Model):
    """Таблица ингредиент ингредиентов в рецепте"""
    name = models.CharField(
        "название ингредиента",
        max_length=200,
        unique=True)
    measurement_unit = models.CharField(
        "единица измерения",
        max_length=200)

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Таблица тегов"""
    name = models.CharField(
        "имя тега",
        max_length=200,
        unique=True)
    color = models.CharField(
        "цветовой код",
        max_length=7,
        unique=True,
        validators=[validate_hex_color])
    slug = models.SlugField(
        "http link",
        max_length=200,
        unique=True,
        validators=[validators.validate_slug])

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="пользователь",
        on_delete=models.CASCADE,
        related_name="shopping_cart")
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="рецепт",
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = "корзина пользователя"
        verbose_name_plural = "корзины пользователей"
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="shopping_cart_user_recipe_constraint")]


class Favorite(models.Model):
    """Модель избранных рецептов"""
    user = models.ForeignKey(
        User,
        verbose_name="пользователь",
        on_delete=models.CASCADE,
        related_name="favorite")
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="избранный рецепт",
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = "избранный рецепт"
        verbose_name_plural = "избранные рецепты"
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="favorite_user_recipe_constraint")]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class Subscribe(models.Model):
    """Модель подписки пользователей на других пользователей"""
    subscriber = models.ForeignKey(
        User,
        verbose_name="подписчик",
        on_delete=models.CASCADE,
        related_name="subscriptions")
    subscription = models.ForeignKey(
        User,
        verbose_name="подписан на",
        on_delete=models.CASCADE,
        related_name="subscription")

    class Meta:
        verbose_name = "подписка на пользователя"
        verbose_name_plural = "подписки на пользователей"
        ordering = ("subscriber",)
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "subscription"],
                name="unique user subscription"),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F("subscription")),
                name="self subscription")
        ]
