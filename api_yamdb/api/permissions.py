from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """Доступ только админу."""
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return (request.user.is_admin or request.user.is_superuser)


class IsAnyIsAdmin(permissions.BasePermission):
    """Доступ только админу, но просмотр для всех."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_admin or request.user.is_superuser)
        return request.method in permissions.SAFE_METHODS


class IsAuthorActionOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """Доступ только текущему пользователю, модератору и админу."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user or request.user.is_moderator
                or request.user.is_admin or request.user.is_superuser
                )


class IsUserEditOnlyPermission(permissions.BasePermission):
    """Доступ к users/me только текущему пользователю."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (obj.id == request.user)
