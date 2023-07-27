from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.serializers_user import UserSerializer
from api.utils import AbstractSerializer, create_ingredients
from backend import const
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт"""
    id = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        required=True,
        write_only=True,
        min_value=const.MIN_INT,
        max_value=const.MAX_INT)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class IngredientsReadSerializer(serializers.ModelSerializer):
    """Сериализатор отображения одного или списка ингредиентов"""
    amount = serializers.IntegerField(read_only=True)
    name = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="name",
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient",
        read_only=True)
    measurement_unit = serializers.SlugRelatedField(
        source="ingredient",
        slug_field="measurement_unit",
        read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для ответа на запросы
       используется в сериализаторе RecipeSerializer """
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsReadSerializer(
        source="recipe_ingredients",
        many=True,
        read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=const.MIN_INT,
        max_value=const.MAX_INT)

    class Meta:
        model = Recipe
        fields = (
            "id", "tags", "ingredients", "author", "image", "is_favorited",
            "is_in_shopping_cart", "name", "text", "cooking_time")

    def get_is_favorited(self, instance):
        request = self.context.get("request")
        return (request.user.is_authenticated
                and request.user.favorite.filter(recipe=instance).exists())

    def get_is_in_shopping_cart(self, instance):
        request = self.context.get("request")
        return (request.user.is_authenticated
                and request.user.shopping_cart.filter(
                    recipe=instance).exists())


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов, используется в recipe viewSet"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Tag.objects.all())
    ingredients = IngredientsSerializer(
        many=True,
        required=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = "__all__"

    def to_representation(self, instance):
        """Сериализует ответ на запросы GET & GET(list) & POST & PATCH"""
        context = self.context.get("request")
        serializer = RecipeReadSerializer(
            instance,
            context={"request": context}
        )
        return serializer.data

    def create(self, validated_data):
        """Сохраняет теги и ингредиенты рецепта и теги в базу данных"""
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Очищает ингредиенты рецепта и создает новые экземпляры,
           после чего передает данные в базовый метод update"""
        instance.recipe_ingredients.all().delete()
        ingredients = validated_data.pop("ingredients")
        create_ingredients(ingredients, recipe=instance)
        return super().update(instance, validated_data)


class ShoppingCartSerializer(AbstractSerializer):
    class Meta(AbstractSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=["user", "recipe"],
                message=const.ERR_SELF_SUBSCRIBE)]


class ShoppingCartDestroySerializer(AbstractSerializer):
    """Сериализатор для удаления из shopping_cart(без валидации)"""

    class Meta(AbstractSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(AbstractSerializer):
    """Сериализатор для добавления в избранное"""

    class Meta(AbstractSerializer.Meta):
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=["user", "recipe"],
                message=const.ERR_FAVOURITE)]


class FavoriteDestroySerializer(AbstractSerializer):
    """Сериализатор для удаления из избранного(без валидации)"""

    class Meta(AbstractSerializer.Meta):
        model = Favorite


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = "__all__"
