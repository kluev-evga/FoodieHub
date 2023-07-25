from pathlib import Path

from django.db.models import F, Sum
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.shortcuts import HttpResponse
from django.utils.translation import gettext_lazy as translate
from drf_base64.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient, ShoppingCart


def perform_create_or_delete(pk, request, model,
                             post_serializer, destroy_serializer):
    """Используется в recipe viewSet в @action: shopping_cart & favorite"""
    arguments = {"data": {"recipe": pk}, "context": {"request": request}}

    if request.method == "POST":
        serializer = post_serializer(**arguments)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    serializer = destroy_serializer(**arguments)
    serializer.is_valid(raise_exception=True)
    instance = model.objects.filter(user=request.user, recipe_id=pk)
    if not instance:
        return Response({"message": translate("not exist")},
                        status=status.HTTP_400_BAD_REQUEST)
    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class QueryParamsSerializer(serializers.Serializer):
    """Валидатор query параметра recipes_limit"""
    recipes_limit = serializers.IntegerField(min_value=0)


def validate_limit(limit):
    """Используется в recipe viewSet в @action: shopping_cart & favorite"""
    if limit:
        serializer = QueryParamsSerializer(data={"recipes_limit": limit})
        serializer.is_valid(raise_exception=True)


def create_ingredients(ingredients, recipe):
    """Создает ингредиенты в рецепте"""
    ingredient_list = [
        RecipeIngredient(
            amount=item.get("amount"),
            recipe=recipe,
            ingredient=item.get("id")
        )
        for item in ingredients
    ]
    RecipeIngredient.objects.bulk_create(ingredient_list)


class UserViewSetMixin:
    """Миксин убирает не используемые @action"""
    activation = None
    resend_activation = None
    reset_password = None
    reset_password_confirm = None
    set_username = None
    reset_username = None
    reset_username_confirm = None


class AbstractSerializer(serializers.ModelSerializer):
    """Общий класс для создания shopping_cart & favorite"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Recipe.objects.all())

    id = serializers.PrimaryKeyRelatedField(
        source="recipe",
        read_only=True)
    name = serializers.SlugRelatedField(
        source="recipe",
        slug_field="name",
        read_only=True)
    image = Base64ImageField(
        source="recipe.image",
        read_only=True)
    cooking_time = serializers.SlugRelatedField(
        source="recipe",
        slug_field="cooking_time",
        read_only=True)

    class Meta:
        fields = ("id", "name", "image", "cooking_time", "user", "recipe")


@receiver(post_delete, sender=Recipe)
def delete_image(sender, instance, *a, **kw):
    """Удаление картинки при удалении рецепта"""
    image = Path(instance.image.path)
    if image.exists():
        image.unlink()


def make_ingredients_txt_response(request):
    ingredients = ShoppingCart.objects.filter(
        user=request.user
    ).values(
        name=F("recipe__recipe_ingredients__ingredient__name"),
        measurement_unit=F(
            "recipe__recipe_ingredients__ingredient__measurement_unit")
    ).annotate(
        amount=Sum("recipe__recipe_ingredients__amount")
    )
    shopping_list = '\n'.join([
        f'- {ingredient["name"]} '
        f'({ingredient["measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    response = HttpResponse(shopping_list,
                            content_type='text.txt; charset=utf-8')
    filename = f'{request.user}_shopping_list.txt'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
