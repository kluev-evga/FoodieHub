from api.models import Amount, Favorite, Ingredient, Recipe, ShoppingCart, Tag
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers


class IngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True,
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = Amount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        # read_only_fields = ("name", "color", "slug")


class RecipeSerializer(WritableNestedModelSerializer):
    # tags = TagSerializer(many=True) # ломается post & patch ...
    ingredients = IngredientsSerializer(many=True, required=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = '__all__'


class AbstractSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Recipe.objects.all())

    id = serializers.PrimaryKeyRelatedField(source="recipe", read_only=True)
    name = serializers.SlugRelatedField(
        source="recipe", slug_field="name", read_only=True)
    image = serializers.SlugRelatedField(
        source="recipe", slug_field="image", read_only=True)
    cooking_time = serializers.SlugRelatedField(
        source="recipe", slug_field="cooking_time", read_only=True)


ABSTRACT_FIELDS = ("id", "name", "image", "cooking_time", "user", "recipe")


class ShoppingCartSerializer(AbstractSerializer):
    class Meta:
        model = ShoppingCart
        fields = ABSTRACT_FIELDS


class FavoriteSerializer(AbstractSerializer):
    class Meta:
        model = Favorite
        fields = ABSTRACT_FIELDS


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"
