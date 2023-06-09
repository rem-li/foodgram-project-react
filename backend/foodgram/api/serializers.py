from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from recepies.models import (Ingredient, Recipe, RecipeIngredient,
                             ShoppingList, Tag)
from rest_framework import serializers
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='units')

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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
    color = serializers.CharField(source='hexcolor')

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated and user != obj:
            return user.is_subscribed_to(obj)
        return False

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribed'
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


class RecipeShortSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
        )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
            'id'
            )

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'name' in validated_data:
            instance.name = validated_data['name']
        if 'text' in validated_data:
            instance.text = validated_data['text']
        if 'cooking_time' in validated_data:
            instance.cooking_time = validated_data['cooking_time']
        if 'image' in validated_data:
            instance.image = validated_data['image']
        ingredient_amounts = validated_data.get('ingredients')
        if ingredient_amounts is not None:
            recipe_ingredients = []
            for ia in ingredient_amounts:
                ingredient = ia['id']
                amount = ia['amount']
                recipe_ingredient, _ = (
                    RecipeIngredient.objects.update_or_create(
                        recipe=instance,
                        ingredients=ingredient,
                        defaults={'amount': amount}
                    )
                )
                recipe_ingredients.append(recipe_ingredient)
            RecipeIngredient.objects.filter(
                recipe=instance
            ).exclude(
                id__in=[ri.id for ri in recipe_ingredients]
            ).delete()
        tags = validated_data.get('tags')
        if tags is not None:
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


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.is_subscribed_to(obj)
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author__id=obj.id).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(
            author__id=obj.id
        ).order_by('-pub_date')[:3]
        serializer = SubscriptionRecipeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data
