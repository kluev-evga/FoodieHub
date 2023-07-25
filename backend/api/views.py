from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageCountPagination
from api.permissions import IsOwnerOnly
from api.serializers import (
    FavoriteDestroySerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartDestroySerializer,
    ShoppingCartSerializer,
    TagSerializer)
from api.serializers_user import SubscribeSerializer, SubscriptionsSerializer
from api.utils import (
    perform_create_or_delete,
    validate_limit,
    UserViewSetMixin,
    make_ingredients_txt_response)
from recipes.models import (
    Favorite, Ingredient, Recipe, ShoppingCart, Subscribe, Tag)

User = get_user_model()


class UserViewSet(UserViewSetMixin, DjoserUserViewSet):
    pagination_class = PageCountPagination

    @action(["get"],
            detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=["get"],
            detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        limit = request.query_params.get("recipes_limit")
        validate_limit(limit)
        queryset = User.objects.filter(subscription__subscriber=request.user)
        serializer = SubscriptionsSerializer(
            context={"request": request, "limit": limit},
            instance=self.paginate_queryset(queryset),
            many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["post", "delete"],
            detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        get_object_or_404(User, pk=kwargs.get("id"))
        data = {"subscriber": request.user.pk,
                "subscription": kwargs.get("id")}

        if request.method == "POST":
            limit = request.query_params.get("recipes_limit")
            validate_limit(limit)
            serializer = SubscribeSerializer(
                context={"request": request, "limit": limit},
                data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        instance = Subscribe.objects.filter(**data)
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "Подписки не существует"},
                        status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = PageCountPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    http_method_names = ("head", "options", "get", "post", "patch", "delete")

    def get_permissions(self):
        if self.action in ("destroy",
                           "partial_update",
                           "download_shopping_cart"):
            return (IsOwnerOnly(),)
        return (IsAuthenticatedOrReadOnly(),)

    def perform_destroy(self, instance):
        instance.recipe_ingredients.all().delete()
        instance.delete()

    @action(methods=["get"],
            detail=False)
    def download_shopping_cart(self, request):
        return make_ingredients_txt_response(request)

    @action(methods=["post", "delete"],
            detail=True)
    def shopping_cart(self, request, pk):
        arguments = {
            "pk": pk,
            "request": request,
            "model": ShoppingCart,
            "post_serializer": ShoppingCartSerializer,
            "destroy_serializer": ShoppingCartDestroySerializer}
        return perform_create_or_delete(**arguments)

    @action(methods=["post", "delete"],
            detail=True)
    def favorite(self, request, pk):
        arguments = {
            "pk": pk,
            "request": request,
            "model": Favorite,
            "post_serializer": FavoriteSerializer,
            "destroy_serializer": FavoriteDestroySerializer}
        return perform_create_or_delete(**arguments)


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
