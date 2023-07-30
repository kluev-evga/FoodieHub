from django.apps import AppConfig


class RecipiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recipes"
    verbose_name = "рецепт"
    verbose_name_plural = "рецепты"
