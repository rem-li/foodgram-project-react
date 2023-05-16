from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recepies.models import (Ingredient, Recipe, RecipeIngredient,
                             ShoppingList, Tag)
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), write_only=True
        )
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
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return user.favorite_recipes.filter(pk=obj.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context['request'].user.is_authenticated:
            return False
        user = self.context['request'].user
        shopping_lists = ShoppingList.objects.filter(user=user).prefetch_related('shoppinglistitem_set')
        recipes_in_cart = Recipe.objects.filter(shoppinglistitem__shopping_list__in=shopping_lists)
        return recipes_in_cart.filter(pk=obj.pk).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited', 'name',
            'image', 'text', 'cooking_time', 'is_in_shopping_cart'
            )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
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
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        recipe_ingredients = [RecipeIngredient(recipe=instance, **ia) for ia in ingredient_amounts]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        instance.tags.set(tags)
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        ingredient_amounts = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        with transaction.atomic():
            recipe = Recipe.objects.create(
                **validated_data, author=self.context['request'].user
                )
            recipe_ingredients = [RecipeIngredient(recipe=recipe, **ia) for ia in ingredient_amounts]
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
            recipe.tags.set(tags)
        return recipe


class ShoppingListSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = ShoppingList
        fields = ('id', 'recipe', 'user')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'is_subscribed'
            )

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        return current_user.is_subscribed_to(obj)


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')


class UserRecieveTokenSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
