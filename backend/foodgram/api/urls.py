from django.urls import path, include
from rest_framework import routers
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet, UserViewSet, UserDeleteTokenViewSet, UserReceiveTokenViewSet, SetPasswordView, UserSubscriptionsView

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

user_urls = [path('set_password/', SetPasswordView.as_view(), name='set_password'),
             path('subscriptions/', UserSubscriptionsView.as_view(), name='subscriptions'),
             path('<int:user_id>/subscribe/', UserSubscriptionsView.as_view(), name='user_subscribe')]

auth_urls = [path('login/', UserReceiveTokenViewSet.as_view(), name='login'),
             path('logout/', UserDeleteTokenViewSet.as_view(), name='logout')]

urlpatterns = [path('users/', include(user_urls)),
               path('auth/token/', include(auth_urls)),
               path('', include(router.urls))]
