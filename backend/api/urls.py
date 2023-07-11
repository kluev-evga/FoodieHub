from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include, path
from users.views import UserViewSet

router = DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
