from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    author = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    tags = models.ManyToManyField('Tag')


class Amount(models.Model):
    amount = models.PositiveIntegerField()
    recipe = models.ManyToManyField('Recipe', related_name='ingredients')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
