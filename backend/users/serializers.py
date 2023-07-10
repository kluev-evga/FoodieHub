from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscribe

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


class SubscriptionsSerializer(serializers.ModelSerializer):
    email = serializers.SlugRelatedField(source="subscription", slug_field="email", read_only=True)
    id = serializers.PrimaryKeyRelatedField(source="subscription", read_only=True)
    username = serializers.SlugRelatedField(source="subscription", slug_field="username", read_only=True)
    first_name = serializers.SlugRelatedField(source="subscription", slug_field="first_name", read_only=True)
    last_name = serializers.SlugRelatedField(source="subscription", slug_field="last_name", read_only=True)

    class Meta:
        model = Subscribe
        fields = ("email", "id", "username", "first_name", "last_name")


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

    def validate(self, data):
        if self.context.get('request').user == data.get("subscription"):
            raise ValidationError("Нельзя подписаться на себя")
        return data
