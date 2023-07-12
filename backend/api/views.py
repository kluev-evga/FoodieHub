from api.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    ShoppingCartDestroySerializer,
    FavoriteDestroySerializer
)
from api.filters import IngredientFilter
from api.utils import perform_create_or_delte

from django.db.models import F, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ('head', 'options', 'get', 'post', 'patch', 'delete')

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
