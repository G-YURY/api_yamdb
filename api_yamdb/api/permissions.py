from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsUserRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return False
        return request.user.role == 'user' or request.user.is_superuser


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.role == 'admin' or request.user.is_superuser


class IsAnyIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            if not request.user.is_anonymous:
                return False
            return (request.user.is_authenticated
                    and (request.user.role == 'admin'
                         or request.user.is_superuser
                         or request.user.is_staff))
        return True


class IsAuthorIsAllRoles(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            if not request.user.is_anonymous:
                return False
            if request.method == 'POST':
                return request.user.is_authenticated
            return (request.user.is_authenticated
                    and (request.user.role == 'admin'
                         or request.user.role == 'moderator'
                         or obj.author == request.user
                         or request.user.is_superuser))
        return True


class IsModeratorRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return False
        return request.user.role == 'moderator' or request.user.is_superuser


class IsAuthorActionsOrReadOnly(permissions.BasePermission):
    """Разрешение на уровне объекта, чтобы разрешить его редактирование
        только владельцам объекта.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthorActionOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and (request.user.role == 'admin'
                     or request.user.role == 'moderator'
                     or obj.author == request.user
                     or request.user.is_superuser
                     or request.user.is_staff))


class IsUserEditOnlyPermission(permissions.BasePermission):
    """Доступ к users/me только текущему пользователю."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (obj.id == request.user)
