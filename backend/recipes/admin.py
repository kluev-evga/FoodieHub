from django.contrib import admin
from django.contrib.auth import get_user_model

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Subscribe, Tag)

User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ панель рецептов"""
    list_display = ("id", "author", "name", "image",
                    "text", "cooking_time", "pub_date")
    list_display_links = ("name",)
    inlines = (RecipeIngredientInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit",)
    list_filter = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ панель тегов"""
    list_display = ("id", "name", "color", "slug")
    list_display_links = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ панель покупок"""
    list_display = ("user", "recipe",)
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель избранное"""
    list_display = ("user", "recipe",)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админ панель подписок на пользователей"""
    list_display = ("id", "subscriber", "subscription")
    list_display_links = ("subscriber",)
