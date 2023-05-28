from django.db import transaction
# from djoser.serializers import UserSerializer
from recepies.models import (Ingredient, Recipe, RecipeIngredient,
                             ShoppingList, Tag)
from rest_framework import serializers
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), write_only=True
        )
    amount = serializers.FloatField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def to_internal_value(self, data):
        ingredient = data.get('id')
        if isinstance(ingredient, Ingredient):
            data['id'] = ingredient.id
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.is_subscribed_to(obj)
        return False

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'is_subscribed'
            )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        queryset = obj.ingredients.through.objects.filter(recipe=obj)
        return [
            {
                'id': ingredient.ingredients.id,
                'name': ingredient.ingredients.name,
                'measurement_unit': ingredient.ingredients.units,
                'amount': ingredient.amount,
            }
            for ingredient in queryset
        ]

    def get_is_favorited(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        user = self.context['request'].user
        return user.favorite_recipes.filter(pk=obj.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        user = self.context['request'].user
        return obj.shopping_lists.filter(user=user).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited', 'name',
            'image', 'text', 'cooking_time', 'is_in_shopping_cart'
            )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
        required=False
        )
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
            )

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredient_amounts = validated_data.pop('ingredients')
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        instance = super().update(instance, validated_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipe_ingredients = [
            RecipeIngredient(
                recipe=instance, **ia
            ) for ia in ingredient_amounts
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        ingredient_amounts = validated_data.pop('ingredients')
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.author = self.context['request'].user
        recipe_ingredients = []
        for ia in ingredient_amounts:
            ingredient = ia['id']
            amount = ia['amount']
            recipe_ingredient = RecipeIngredient(
                recipe=recipe, ingredients=ingredient, amount=amount
            )
            recipe_ingredients.append(recipe_ingredient)
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)
        return recipe


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingList
        fields = ('id', 'recipe', 'user')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserRecieveTokenSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
