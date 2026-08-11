from rest_framework.permissions import BasePermission

WRITE_GROUPS = ('magasinier', 'admin')
READ_GROUPS = ('magasinier', 'admin', 'commercial', 'gestionnaire_achats')


class IsMagasinierOrAdminInventaire(BasePermission):
    """Écriture : magasinier, admin. Lecture : + commercial, gestionnaire_achats."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.groups.filter(name__in=READ_GROUPS).exists() or request.user.is_staff
        return request.user.groups.filter(name__in=WRITE_GROUPS).exists() or request.user.is_staff
