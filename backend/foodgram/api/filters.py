import django_filters
from recepies.models import Recipe, Tag
from rest_framework import filters


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = django_filters.CharFilter(
        field_name='author__id'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
