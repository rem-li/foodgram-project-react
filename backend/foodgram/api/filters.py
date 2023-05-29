import django_filters
from recepies.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = django_filters.CharFilter(
        field_name='author__id'
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def __init__(self, *args, **kwargs):
        self.serializer = kwargs.pop('serializer')
        super().__init__(*args, **kwargs)

    def filter_is_favorited(self, queryset, name, value):
        is_favorited = self.serializer.data.get('is_favorited')
        return self.serializer.filter_is_favorited(queryset, is_favorited)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        is_in_shopping_cart = self.serializer.data.get('is_in_shopping_cart')
        return self.serializer.filter_is_in_shopping_cart(
            queryset, is_in_shopping_cart
        )
