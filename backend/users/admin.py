from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class UsersAdmin(UserAdmin):
    """Админ панель пользователей"""
    list_display = ("id", "username", "first_name", "last_name", "email")
    list_display_links = ("username",)
