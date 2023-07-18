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


# ---------------------------------------------------------------CONCEPT:
class CustomListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        limit = self.context.get("limit")
        limit = int(limit) if limit else None
        iterable = data.all()[:limit]
        self.context["recipes_count"] = iterable.count()
        return [self.child.to_representation(item) for item in iterable]


class RecipiesTestSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = CustomListSerializer
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class TestSerializer(UserSerializer):
    recipies = RecipiesTestSerializer(source="recipes", many=True)
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, _):
        return self.context.get("recipes_count")

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed", "recipies", "recipes_count")


# ---------------------------------------------------------------CONCEPT END
class QueryParamsSerializer(serializers.Serializer):
    recipes_limit = serializers.IntegerField(min_value=0, required=False, default=None)


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
        serializer = TestSerializer(instance.subscription, context=self.context)
        return serializer.data

    def validate(self, data):
        if self.context.get('request').user == data.get("subscription"):
            raise ValidationError("Нельзя подписаться на себя")
        return data
