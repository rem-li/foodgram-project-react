from rest_framework import serializers
from django.contrib.auth.models import BaseUserManager
from djoser.serializers import UserCreateSerializer, UserSerializer
from recepies.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredients.name')
    
    class Meta:
        model = RecipeIngredient
        fields = ('ingredient_name', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)
    author = serializers.StringRelatedField()
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserRecieveTokenSerializer(serializers.Serializer):
    """Serializer of User JWT token."""

    email = serializers.CharField(
        # validators=[validate_username],
        # max_length=settings.LEN_USER_FIELDS,
        required=True
    )
    password = serializers.CharField(
        # max_length=settings.LEN_USER_FIELDS,
        required=True
    )

class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
