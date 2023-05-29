from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsCreateOnly, IsRecipeAuthor
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, RecipeShortSerializer,
                             SetPasswordSerializer, ShoppingListSerializer,
                             TagSerializer, UserCreateSerializer,
                             UserRecieveTokenSerializer, UserSerializer,
                             UserSubscriptionSerializer)
from django.db.models import Count, F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recepies.models import (Ingredient, Recipe, RecipeIngredient,
                             ShoppingList, Tag)
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView
from users.models import User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    ordering_fields = ('pub_date',)
    queryset = Recipe.objects.all().order_by('id')
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsRecipeAuthor]

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action == 'favorite':
            return RecipeShortSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_favorited == '1':
            return queryset.filter(
                favorited_by=self.request.user
            )
        if is_in_shopping_cart == '1':
            return queryset.filter(
                shopping_lists__user=self.request.user
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = RecipeSerializer(
            instance=recipe,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
            detail=True, methods=['POST', 'DELETE'],
            url_path='favorite', url_name='recipe_favorite',
            )
    def favorite(self, request, pk=None):
        self.permission_classes = [IsAuthenticated]
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            user.favorite_recipes.add(recipe)
            serializer = RecipeSerializer(
                instance=recipe, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            user.favorite_recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingListViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingListSerializer
    http_method_names = ['post', 'delete']

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        shopping_list, created = ShoppingList.objects.get_or_create(
            user=request.user
        )
        shopping_list.recipes.add(recipe)
        serializer = self.serializer_class(
            shopping_list, context={"request": request}
        )
        recipe_serializer = RecipeSerializer(
            recipe, context={"request": request}
        )
        response_data = {
            'recipe': recipe_serializer.data,
            'shopping_list': serializer.data
        }
        return Response(response_data)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        shopping_list = get_object_or_404(ShoppingList, user=request.user)
        shopping_list.recipes.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadView(APIView):

    def get(self, request):
        ingredients = (
                RecipeIngredient.objects.select_related(
                    'recipe', 'ingredients'
                ).filter(
                    recipe__shopping_lists__user=request.user,
                ).annotate(
                    name=F('ingredients__name'),
                    units=F('ingredients__units'),
                    total=Sum('amount'),
                )
            )
        ingredients_str = ''
        for ingredient in ingredients:
            name = ingredient.ingredients.name
            amount = ingredient.amount
            measurement_unit = ingredient.ingredients.units
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
        token, created = Token.objects.get_or_create(user=user)
        message = {'auth_token': str(token.key)}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    search_fields = ('username',)
    http_method_names = ['get', 'patch', 'post', 'delete']
    permission_classes = [IsCreateOnly]

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            serializer_class = UserCreateSerializer
        else:
            serializer_class = UserSerializer
        kwargs['context'] = {'request': self.request}
        return serializer_class(*args, **kwargs)

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def get_me_data(self, request):
        """Getting user data."""
        serializer = UserSerializer(context={'request': request})
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
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        subscriptions = user.subscriptions.all()
        recipes_count = Recipe.objects.filter(
            author__in=subscriptions
        ).values('author').annotate(count=Count('author'))
        serializer = UserSubscriptionSerializer(
            subscriptions, many=True,
            context={'request': request}
        )
        serializer_data = serializer.data
        for user_data in serializer_data:
            user_id = user_data['id']
            recipe_count = next(
                (item[
                    'count'
                ] for item in recipes_count if item[
                    'author'
                ] == user_id), 0
            )
            user_data['recipes_count'] = recipe_count
        return self.paginate_queryset(serializer_data, request)

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        user = request.user
        if target_user == user:
            return Response({'error': 'Invalid target user'}, status=400)
        serializer = UserSubscriptionSerializer(
            user, context={'request': request}
        )
        recipes_count = Recipe.objects.filter(
            author=target_user
        ).count()
        user.subscribe_to_user(target_user)
        serializer_data = serializer.data
        serializer_data['is_subscribed'] = True
        serializer_data['recipes_count'] = recipes_count
        return Response(serializer_data)

    def delete(self, request, user_id):
        user = request.user
        target_user = get_object_or_404(User, id=user_id)
        if not user.is_subscribed_to(target_user):
            return Response({'error': 'User is not subscribed'}, status=400)
        user.unsubscribe_from_user(target_user)
        return Response(status=204)
