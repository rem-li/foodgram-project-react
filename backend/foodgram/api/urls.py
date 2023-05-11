from django.urls import path, include
from rest_framework import routers
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet, UserDeleteTokenViewSet, UserReceiveTokenViewSet, SetPasswordView

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

user_urls = [path('users/', include('djoser.urls')),
             path('users/', include('djoser.urls.jwt')),
             path('users/set_password/', SetPasswordView.as_view(), name='set_password')]

auth_urls = [path('login/', UserReceiveTokenViewSet.as_view(), name='login'),
             path('logout/', UserDeleteTokenViewSet.as_view(), name='logout')]

urlpatterns = [path('', include(router.urls)),
               path('', include(user_urls)),
               path('auth/token/', include(auth_urls))]
