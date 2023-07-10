from api.views import RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = router.urls