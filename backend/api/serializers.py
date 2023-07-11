from api.models import Amount, Favorite, Ingredient, Recipe, ShoppingCart, Tag
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializer


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
        fields = ("id", "name", "color", "slug")


class RecipeViewSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, required=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientsSerializer(many=True, required=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = "__all__"

    def to_representation(self, instance):
        context = self.context.get("request")
        return RecipeViewSerializer(instance, context={"request": context}).data

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        author = self.context.get("request").user
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data, author=author)
        recipe.tags.set(tags)
        ingredients_list = []
        for item in ingredients:
            ingredients_list.append(item.get("ingredient").pk)
            Amount.objects.create(**item)
        recipe.ingredients.set(ingredients_list)
        return recipe


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
