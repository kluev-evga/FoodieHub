from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscribe
from api.models import Recipe

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed")

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return request.user.is_authenticated and request.user.subscriptions.filter(subscription=user).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):
    password = serializers.CharField(max_length=150, write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class RelatedRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsSerializer(serializers.ModelSerializer):
    email = serializers.SlugRelatedField(source="subscription", slug_field="email", read_only=True)
    id = serializers.PrimaryKeyRelatedField(source="subscription", read_only=True)
    username = serializers.SlugRelatedField(source="subscription", slug_field="username", read_only=True)
    first_name = serializers.SlugRelatedField(source="subscription", slug_field="first_name", read_only=True)
    last_name = serializers.SlugRelatedField(source="subscription", slug_field="last_name", read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipies = RelatedRecipesSerializer(source="subscription.recipes", many=True)
    recipes_count = serializers.SerializerMethodField(source="subscription")

    class Meta:
        model = Subscribe
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed", "recipies", "recipes_count")

    # def to_representation(self, instance):
    #     asdf = instance
    #     return super().to_representation(instance)

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, value):
        return value.subscription.recipes.count()


class QueryParamsSerializer(serializers.Serializer):
    recipes_limit = serializers.IntegerField(min_value=0)


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=['subscriber', 'subscription'],
                message='Вы уже подписаны на данного пользователя')
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        serializer = UserSerializer(instance.subscription, context={"request": request})

        recipes = instance.subscription.recipes
        limit = request.query_params.get("recipes_limit", None)
        if limit:
            recipes_limit = QueryParamsSerializer(data={"recipes_limit": limit})
            recipes_limit.is_valid(raise_exception=True)
            recipes_limit = recipes_limit.data.get("recipes_limit")
            recipes = recipes.all()[:recipes_limit]
        recipes = RelatedRecipesSerializer(recipes, many=True).data
        return {**serializer.data, "recipes": recipes}

    def validate(self, data):
        if self.context.get('request').user == data.get("subscription"):
            raise ValidationError("Нельзя подписаться на себя")
        return data
