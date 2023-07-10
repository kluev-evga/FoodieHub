from api.models import Recipe, Tag
from api.serializers import RecipeSerializer, TagSerializer
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('head', 'options', 'get', 'post', 'patch', 'delete')


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
