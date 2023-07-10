from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib import admin

User = get_user_model()


@admin.register(User)
class UsersAdmin(UserAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    save_on_top = True
    save_as = True
    readonly_fields = ('id',)
