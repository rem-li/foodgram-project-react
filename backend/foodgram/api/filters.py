import django_filters

from recepies.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        to_field_name='name',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['tags']
