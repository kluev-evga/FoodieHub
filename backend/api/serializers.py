from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as translate
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_base64.fields import Base64ImageField
from recipies.models import (
    Amount,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscribe,
    Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для отображения одного или списка пользователей"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, user):
        request = self.context.get("request")
        return (request.user.is_authenticated
                and request.user.subscriptions.filter(
                    subscription=user).exists())


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания пользователя,
        ограничивает длину пароля, для защиты от DDOS атак"""
    password = serializers.CharField(
        write_only=True,
        max_length=150,
        required=True)

    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name", "password")


class SubscriptionsListSerializer(serializers.ListSerializer):
    """Сериализатор для end-point - users/subscribe[subscriptions]"""

    def to_representation(self, data):
        """Ограничивает выборку отдаваемых рецептов по параметру recipes_limit,
           передает количество рецептов в родительский класс через контекст"""
        limit = self.context.get("limit")
        limit = int(limit) if limit else None
        iterable = data.all()[:limit]
        self.context["recipes_count"] = iterable.count()
        return [self.child.to_representation(item) for item in iterable]


class SubscriptionsRecipieSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в подписках"""

    class Meta:
        model = Recipe
        list_serializer_class = SubscriptionsListSerializer
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для отображения всех подписок на пользователя &
       отображения одного пользователя при подписке ан пользователя """
    recipies = SubscriptionsRecipieSerializer(
        source="recipes",
        many=True)
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, _):
        return self.context.get("recipes_count")

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name",
                  "is_subscribed", "recipies", "recipes_count")


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления подписки на пользователя"""

    class Meta:
        model = Subscribe
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=["subscriber", "subscription"],
                message="Вы уже подписаны на данного пользователя")]

    def to_representation(self, instance):
        serializer = SubscriptionsSerializer(
            instance.subscription, context=self.context)
        return serializer.data

    def validate(self, data):
        if self.context.get("request").user == data.get("subscription"):
            raise ValidationError("Нельзя подписаться на себя")
        return data


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор отображения одного или списка ингредиентов"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient")
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True)

    class Meta:
        model = Amount
        fields = ("id", "name", "measurement_unit", "amount")


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиента в рецепте"""

    class Meta:
        model = Amount
        fields = ("amount", "ingredient")


class RecipeRepresentationSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов для ответа на запросы
       используется в сериализаторе RecipeSerializer """

    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"

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
    author = UserSerializer(
        read_only=True)
    image = Base64ImageField(
        required=False)

    class Meta:
        model = Recipe
        fields = "__all__"

    def to_representation(self, instance):
        context = self.context.get("request")
        serializer = RecipeRepresentationSerializer(
            instance,
            context={"request": context})
        return serializer.data

    def create(self, validated_data):
        """Сохраняет рецепт в базу данных,
           а так же создает записи для каждого ингредиента"""
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)

        data = [{"ingredient": item.get("ingredient").pk, "amount": item.get(
            "amount")} for item in ingredients]
        serializer = IngredientsInRecipeSerializer(many=True, data=data)
        serializer.is_valid(raise_exception=True)

        ingredient_list = []
        for item in ingredients:
            amount = Amount.objects.create(**item)
            ingredient_list.append(amount)
        recipe.ingredients.set(ingredient_list)
        return recipe

    def update(self, instance, validated_data):
        """Сериализует и валидирует ингредиенты,
           удаляет их все и сохраняет заново,
           после чего передает данные в базовый метод update"""
        ingredients = validated_data.pop("ingredients", None)
        data = [{"ingredient": item.get("ingredient").pk,
                 "amount": item.get("amount")} for item in ingredients]
        serializer = IngredientsInRecipeSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        for ingredient in instance.ingredients.all():
            ingredient.delete()

        ingredient_list = []
        for item in ingredients:
            amount = Amount.objects.create(**item)
            ingredient_list.append(amount)
        instance.ingredients.set(ingredient_list)
        return super().update(instance, validated_data)


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


class ShoppingCartSerializer(AbstractSerializer):
    class Meta(AbstractSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=["user", "recipe"],
                message=translate("already subscribed on that user"))]


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
                message=translate("already favorited"))]


class FavoriteDestroySerializer(AbstractSerializer):
    """Сериализатор для удаления из избранного(без валидации)"""

    class Meta(AbstractSerializer.Meta):
        model = Favorite


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""

    class Meta:
        model = Ingredient
        fields = "__all__"
