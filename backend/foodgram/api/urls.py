from django.urls import path, include
from rest_framework import routers
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls))
]
