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
    """Сериализатор для создания пользователя, ограничивает длину пароля,
       для защиты от DDOS атак)))"""
    password = serializers.CharField(max_length=150, write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class SubscriptionsListSerializer(serializers.ListSerializer):
    """Ограничивает выборку отдаваемых рецептов по QUERY
       параметру recipes_limit для endpoints:
       users/subscribe[subscriptions]"""

    def to_representation(self, data):
        limit = self.context.get("limit")
        limit = int(limit) if limit else None
        iterable = data.all()[:limit]
        self.context["recipes_count"] = iterable.count()
        return [self.child.to_representation(item) for item in iterable]


class SubscriptionsRecipieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        list_serializer_class = SubscriptionsListSerializer
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для отображения всех подписок на пользователя &
       отображения одного пользователя при подписке ан пользователя """
    recipies = SubscriptionsRecipieSerializer(source="recipes", many=True)
    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, _):
        return self.context.get("recipes_count")

    class Meta:
        model = User
        fields = ("email", "id", "username", "first_name", "last_name", "is_subscribed", "recipies", "recipes_count")


class QueryParamsSerializer(serializers.Serializer):
    recipes_limit = serializers.IntegerField(min_value=0, required=False, default=None)


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления подписки на пользователя"""

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
        serializer = SubscriptionsSerializer(instance.subscription, context=self.context)
        return serializer.data

    def validate(self, data):
        if self.context.get('request').user == data.get("subscription"):
            raise ValidationError("Нельзя подписаться на себя")
        return data
