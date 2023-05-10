from rest_framework import serializers

from recepies.models import Ingredient, Tag, Recipe, RecipeIngredient


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
