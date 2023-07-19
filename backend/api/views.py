from api.filters import IngredientFilter, RecipeFilter
from api.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from api.serializers import (
    SubscribeSerializer,
    SubscriptionsSerializer,
    FavoriteDestroySerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartDestroySerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from api.utils import perform_create_or_delte, validate_limit
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscribe

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    activation = None
    resend_activation = None
    reset_password = None
    reset_password_confirm = None
    set_username = None
    reset_username = None
    reset_username_confirm = None

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        limit = request.query_params.get("recipes_limit")
        validate_limit(limit)
        queryset = User.objects.filter(subscription__subscriber=request.user)
        serializer = SubscriptionsSerializer(
            context={"request": request, "limit": limit},
            instance=self.paginate_queryset(queryset),
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=["post", "delete"], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        get_object_or_404(User, pk=id)
        data = {"subscriber": request.user.pk, "subscription": id}

        if request.method == "POST":
            limit = request.query_params.get("recipes_limit")
            validate_limit(limit)
            serializer = SubscribeSerializer(
                context={"request": request, "limit": limit},
                data=data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        instance = Subscribe.objects.filter(**data)
        if instance:
            instance.delete()
            return Response(status=204)

        return Response({"message": "Подписки не существует"}, status=400)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('head', 'options', 'get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_destroy(self, instance):
        for ingredient in instance.ingredients.all():
            ingredient.delete()
        instance.delete()

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        queryset = ShoppingCart.objects.filter(
            user=request.user
        ).values(
            name=F("recipe__ingredients__ingredient__name")
        ).annotate(
            amount=Sum("recipe__ingredients__amount")
        )
        return Response(queryset)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        arguments = {
            "pk": pk,
            "request": request,
            "model": ShoppingCart,
            "post_serializer": ShoppingCartSerializer,
            "destroy_serializer": ShoppingCartDestroySerializer
        }
        return perform_create_or_delte(**arguments)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        arguments = {
            "pk": pk,
            "request": request,
            "model": Favorite,
            "post_serializer": FavoriteSerializer,
            "destroy_serializer": FavoriteDestroySerializer
        }
        return perform_create_or_delte(**arguments)


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
