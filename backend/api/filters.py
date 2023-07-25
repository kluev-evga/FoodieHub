from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр ингредиентов оп query параметру name"""
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilter(filters.FilterSet):
    """Фильтр рецептов оп query параметрам"""
    author = filters.NumberFilter(
        field_name="author")
    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug")
    is_favorited = filters.BooleanFilter(
        field_name="is_favorited",
        method="filter_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        field_name="is_in_shopping_cart",
        method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, _, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset
