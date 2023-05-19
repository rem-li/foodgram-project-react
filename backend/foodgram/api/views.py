from django.core.cache import cache
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import RecipeFilter
from api.permissions import IsRecipeAuthor
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, ShoppingListSerializer,
                             TagSerializer, UserCreateSerializer,
                             UserRecieveTokenSerializer, UserSerializer,
                             SetPasswordSerializer)
from recepies.models import Ingredient, Recipe, ShoppingList, Tag
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    ordering_fields = ('pub_date',)
    queryset = Recipe.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsRecipeAuthor]

    def retrieve(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeSerializer(
            instance=recipe,
            context={'request': request}
        )
        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    self.request.user.favorite_recipes.filter(
                        pk=OuterRef('pk')
                    )
                )
            )
        return queryset.order_by('-pub_date')

    @action(
            detail=True, methods=['POST', 'DELETE'],
            url_path='favorite', url_name='recipe_favorite'
            )
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            user.favorite_recipes.add(recipe)
            is_favorited = True
        elif request.method == 'DELETE':
            user.favorite_recipes.remove(recipe)
            is_favorited = False
        cache.delete(f'user:{user.pk}:favorite_recipes')
        cache.delete(f'recipe:{recipe.pk}:is_favorited')
        data = {'is_favorited': is_favorited}
        serializer = RecipeSerializer(
            instance=recipe,
            data=data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if is_favorited:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                serializer.data, status=status.HTTP_204_NO_CONTENT
                )


class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    http_method_names = ['post', 'delete']

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        shopping_list, created = ShoppingList.objects.get_or_create(user=request.user)
        shopping_list.recipes.add(recipe)
        serializer = self.serializer_class(shopping_list, context={"request": request})
        recipe_serializer = RecipeSerializer(recipe, context={"request": request})
        response_data = {
            'recipe': recipe_serializer.data,
            'shopping_list': serializer.data
        }
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        shopping_list = get_object_or_404(ShoppingList, user=request.user)
        shopping_list.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadView(APIView):

    def get(self, request):
        user = request.user
        shopping_list = (
            ShoppingList.objects
            .select_related('user')
            .prefetch_related('recipes__ingredients')
            .annotate(total_amount=Sum('recipes__recipeingredient__amount'))
            .get(user=user)
        )
        ingredients = []
        for recipe in shopping_list.recipes.all():
            recipe_ingredients = recipe.recipeingredient_set.all()
            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredients
                amount = recipe_ingredient.amount * shopping_list.total_amount
                ingredients.append(
                    {
                        'name': ingredient.name,
                        'units': ingredient.units,
                        'amount': amount
                    }
                )
        ingredients_str = ''
        for ingredient in ingredients:
            name = ingredient['name']
            measurement_unit = ingredient['units']
            amount = ingredient['amount']
            ingredients_str += f"{name} ({measurement_unit}) — {amount}\n"
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        response.write(ingredients_str)
        return response


class UserReceiveTokenViewSet(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            message = {'email': 'Пользователь с таким email не найден'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            message = {'password': 'Неверный пароль'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    search_fields = ('username',)
    http_method_names = ['get', 'patch', 'post', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        else:
            return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me_data(self, request):
        """Getting user data."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"status": "success", "data": serializer.data},
            status=HTTP_201_CREATED
            )


class UserDeleteTokenViewSet(APIView):

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_200_OK
            )


class SetPasswordView(APIView): 
    permission_classes = (IsAuthenticated,) 
    serializer_class = SetPasswordSerializer

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not user.check_password(current_password):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_400_BAD_REQUEST
                )
        user.set_password(new_password)
        user.save()
        return Response(
            {'message': 'Password updated successfully'},
            status=status.HTTP_200_OK
            ) 


class UserSubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        subscriptions = user.subscriptions.all()
        if not subscriptions:
            return Response([])
        recipes = Recipe.objects.filter(
            author__in=subscriptions
        ).prefetch_related('tags')
        serializer = RecipeSerializer(recipes, many=True)
        recipes_data = serializer.data
        serializer = UserSerializer(
            subscriptions, many=True, context={'request': request}
        )
        response_data = {'users': serializer.data, 'recipes': recipes_data}
        return Response(response_data)

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        user = request.user
        if target_user == user:
            return Response({'error': 'Invalid target user'}, status=400)
        serializer = UserSerializer(user, context={'target_user': target_user})
        user.subscribe_to_user(target_user)
        serializer_data = serializer.data
        serializer_data['is_subscribed'] = True
        return Response({'success': True, 'data': serializer_data})

    def delete(self, request, user_id):
        user = request.user
        target_user = get_object_or_404(User, id=user_id)
        if not user.is_subscribed_to(target_user):
            return Response({'error': 'User is not subscribed'}, status=400)
        user.unsubscribe_from_user(target_user)
        serializer = UserSerializer(user, context={'target_user': target_user})
        serializer_data = serializer.data
        serializer_data['is_subscribed'] = False
        return Response({'success': True, 'data': serializer_data})
