from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)


class IsUserRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'user' or request.user.is_superuser


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser


class IsModeratorRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'moderator' or request.user.is_superuser


class IsAuthorActionsOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение на уровне объекта, чтобы разрешить его редактирование
        только владельцам объекта.
    """
    def has_object_permission(self, request, view, obj):
        return bool(obj.author == request.user
                    or request.method in SAFE_METHODS)
