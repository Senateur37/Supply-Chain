from rest_framework.permissions import BasePermission


class IsGroupMember(BasePermission):
    """Autorise l'accès si l'utilisateur appartient au groupe requis."""

    def __init__(self, group_name):
        self.group_name = group_name

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name=self.group_name).exists()
        )


class IsAdminOrReadOnly(BasePermission):
    """Lecture seule pour les utilisateurs authentifiés, écriture réservée aux admins."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.groups.filter(name='admin').exists() or request.user.is_staff
