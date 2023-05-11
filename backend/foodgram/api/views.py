from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from api.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, UserCreateSerializer, UserRecieveTokenSerializer, UserSerializer, SetPasswordSerializer
from recepies.models import Tag, Ingredient, Recipe
from users.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
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
