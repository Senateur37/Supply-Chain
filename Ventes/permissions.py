from rest_framework.permissions import BasePermission

WRITE_GROUPS = ('commercial', 'admin')
READ_GROUPS = ('commercial', 'admin', 'auditeur')


class IsCommercialOrAdmin(BasePermission):
    """Écriture : commercial, admin. Lecture : + auditeur."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.groups.filter(name__in=READ_GROUPS).exists() or request.user.is_staff
        return request.user.groups.filter(name__in=WRITE_GROUPS).exists() or request.user.is_staff
