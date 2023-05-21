from rest_framework.filters import SearchFilter

from .permissions import IsAnyIsAdmin
from api.mixins import CreateListDestroyViewSet


class AdminOrReadyViewSet(CreateListDestroyViewSet):
    """Кастомный вьюсет для Genre и Category."""
    permission_classes = (IsAnyIsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'
