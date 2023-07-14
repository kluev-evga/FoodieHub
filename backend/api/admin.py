from django.contrib.auth import get_user_model
from django.contrib import admin
from api.models import Recipe, Tag, ShoppingCart, Favorite

User = get_user_model()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ панель рецептов"""
    list_display = ('id', "author", "name", "image", "text", "cooking_time")
    list_display_links = ("author",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ панель тегов"""
    list_display = ('id', "name", "color", "slug")
    list_display_links = ("name",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ панель покупок"""
    list_display = ('user', 'recipe',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель избранное"""
    list_display = ('user', 'recipe',)
