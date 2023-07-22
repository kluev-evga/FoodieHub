from django.contrib import admin
from django.contrib.auth import get_user_model
from recipies.models import Favorite, Recipe, ShoppingCart, Subscribe, Tag

User = get_user_model()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ панель рецептов"""
    list_display = ("id", "author", "name", "image", "text", "cooking_time")
    list_display_links = ("author",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ панель тегов"""
    list_display = ("id", "name", "color", "slug")
    list_display_links = ("name",)


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
    list_display_links = ("id",)
    save_on_top = True
    save_as = True
