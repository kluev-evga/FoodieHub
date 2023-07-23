from django.utils.translation import gettext_lazy as translate
from rest_framework import serializers, status
from rest_framework.response import Response

from recipies.models import Amount


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


class RecipeAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для валидации количества ингредиента в рецепте"""

    class Meta:
        model = Amount
        fields = ("amount", "ingredient")


def serialize_ingredients(ingredients):
    """Извлекает ингредиенты и валидирует данные"""
    data = [{"ingredient": item.get("ingredient").pk,
             "amount": item.get("amount")}
            for item in ingredients]
    serializer = RecipeAmountSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)


class UserViewSetMixin:
    """Миксин убирает все не используемые @action"""
    activation = None
    resend_activation = None
    reset_password = None
    reset_password_confirm = None
    set_username = None
    reset_username = None
    reset_username_confirm = None
