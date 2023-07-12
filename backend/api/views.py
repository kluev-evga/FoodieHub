from api.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    ShoppingCartDestroySerializer
)
from django.db.models import F, Sum
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.utils.translation import gettext_lazy as translate


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
        arguments = {"data": {"recipe": pk}, "context": {"request": request}}

        if request.method == "POST":
            serializer = ShoppingCartSerializer(**arguments)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = ShoppingCartDestroySerializer(**arguments)
        serializer.is_valid(raise_exception=True)
        instance = ShoppingCart.objects.filter(user=request.user, recipe_id=pk)
        if not instance:
            return Response({"message": translate("not exist")}, status=400)
        instance.delete()
        return Response(status=204)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        serializer = FavoriteSerializer(data={"recipe": pk}, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            if request.method == "POST":
                serializer.save()
                return Response(serializer.data)

            Favorite.objects.get(user=request.user, recipe_id=pk).delete()
            return Response(status=204)


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
