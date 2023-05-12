from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from api.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, UserCreateSerializer, UserRecieveTokenSerializer, UserSerializer, SetPasswordSerializer
from recepies.models import Tag, Ingredient, Recipe
from users.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )


class UserReceiveTokenViewSet(CreateAPIView):
    """ViewSet to get JWT token."""

    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer

    def create(self, request, *args, **kwargs):
        """Get JWT token."""
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
    """ViewSet for User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
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
        
        user = serializer.save()

        return Response({"status": "success", "data": serializer.data}, status=HTTP_201_CREATED)


class UserDeleteTokenViewSet(APIView):
    """ViewSet to manage user tokens."""

    def post(self, request, *args, **kwargs):
        """Logout user and revoke token."""
        request.user.auth_token.delete()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class SetPasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetPasswordSerializer

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


class UserSubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        subscriptions = user.subscriptions.all()
        
        if not subscriptions:
            return Response([])
        
        subscribed_users = [s for s in subscriptions]
        recipes_list = []
        
        for user in subscribed_users:
            recipes = Recipe.objects.filter(author=user).prefetch_related('tags')
            serializer = RecipeSerializer(recipes, many=True)
            recipes_list.append(serializer.data)

        serializer = UserSerializer(subscribed_users, many=True)
        response_data = {'users': serializer.data, 'recipes': recipes_list}
        return Response(response_data)
    
    def post(self, request, user_id):
        target_user_id = user_id

        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=400)

        user = request.user

        if target_user == user or target_user.role == User.ADMIN:
            return Response({'error': 'Invalid target user'}, status=400)

        user.subscribe_to_user(target_user)
        return Response({'success': True})

    def delete(self, request, user_id):
        user = request.user

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=400)

        if not user.is_subscribed_to(target_user):
            return Response({'error': 'User is not subscribed'}, status=400)

        user.unsubscribe_from_user(target_user)
        return Response({'success': True})
