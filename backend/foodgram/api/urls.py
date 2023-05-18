from django.urls import include, path
from djoser.views import SetPasswordViewSet
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet,
                       ShoppingCartDownloadView, ShoppingListViewSet,
                       TagViewSet, UserDeleteTokenViewSet,
                       UserReceiveTokenViewSet, UserSubscriptionsView,
                       UserViewSet)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

shopping_list_router = routers.SimpleRouter()
shopping_list_router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    ShoppingListViewSet, basename='shopping_cart'
    )

user_urls = [path(
    'set_password/', SetPasswordViewSet.as_view(), name='set_password'
    ),
             path(
    'subscriptions/', UserSubscriptionsView.as_view(), name='subscriptions'
    ),
             path(
    '<int:user_id>/subscribe/',
    UserSubscriptionsView.as_view(), name='user_subscribe'
    )]

auth_urls = [path('login/', UserReceiveTokenViewSet.as_view(), name='login'),
             path('logout/', UserDeleteTokenViewSet.as_view(), name='logout')]

urlpatterns = [path('users/', include(user_urls)),
               path('auth/token/', include(auth_urls)),
               path(
    'recipes/download_shopping_cart/',
    ShoppingCartDownloadView.as_view(), name='download_shopping_cart'
    ),
               path(
    'recipes/<int:pk>/favorite/',
    RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}),
    name='recipe_favorite'
    ),
               path('', include(router.urls)),
               path('', include(shopping_list_router.urls))]
