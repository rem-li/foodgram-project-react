from rest_framework import serializers
from django.contrib.auth.models import BaseUserManager
from rest_framework.pagination import PageNumberPagination
from djoser.serializers import UserCreateSerializer, UserSerializer
from recepies.models import Ingredient, Tag, Recipe, RecipeIngredient, ShoppingList
from users.models import User
from rest_framework.authentication import TokenAuthentication


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), write_only=True)
    amount = serializers.FloatField()
    
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def to_internal_value(self, data):
        ingredient = data.get('id')
        if isinstance(ingredient, Ingredient):
            data['id'] = ingredient.id
        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer()
    amount = serializers.FloatField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredients', 'amount')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        # Проверяем, есть ли текущий рецепт в списке любимых рецептов пользователя
        return user.favorite_recipes.filter(pk=obj.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        # Проверяем, был ли выполнен запрос авторизации
        if not self.context['request'].user.is_authenticated:
            return False

        user = self.context['request'].user
        shopping_lists = ShoppingList.objects.filter(user=user)
        for shopping_list in shopping_lists:
            if shopping_list.shoppinglistitem_set.filter(recipe=obj).exists():
                return True
        return False


    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'name', 'image', 'text', 'cooking_time', 'is_in_shopping_cart')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')
    
    def create(self, validated_data):
        # Extract and remove nested data from validated_data
        ingredient_amounts = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        
        # Create Recipe object
        recipe = Recipe.objects.create(**validated_data, author=self.context['request'].user)

        # Create RecipeIngredient objects
        for ingredient_amount in ingredient_amounts:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_amount)

        # Add tags to Recipe
        recipe.tags.set(tags)

        return recipe


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingList
        fields = ('id', 'recipe', 'user')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(source='is_subscribed_to', read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_subscribed')


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
