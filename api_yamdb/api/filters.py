import django_filters
from reviews.models import Title


class TitlesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )
    category = django_filters.CharFilter(
        field_name='category__slug'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug'
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')
