from django import forms

from api.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


class ShoppingCartForm(forms.ModelForm):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = '__all__'


class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = '__all__'


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
