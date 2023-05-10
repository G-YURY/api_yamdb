from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAuthorActionsOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение на уровне объекта, чтобы разрешить его редактирование
        только владельцам объекта.
    """
    def has_object_permission(self, request, view, obj):
        return bool(obj.author == request.user
                    or request.method in SAFE_METHODS)
