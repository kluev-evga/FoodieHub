from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib import admin
from users.models import Subscribe

User = get_user_model()


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админ панель пользователей"""
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    list_display_links = ("username",)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Админ панель подписок на пользователей"""
    list_display = ('id', "subscriber", "subscription")
    list_display_links = ("id",)
    save_on_top = True
    save_as = True
