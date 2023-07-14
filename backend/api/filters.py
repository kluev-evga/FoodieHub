from api.models import Ingredient
from django_filters import rest_framework as filters


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="startswith")

    class Meta:
        model = Ingredient
        fields = ["name"]
