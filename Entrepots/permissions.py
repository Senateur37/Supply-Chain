from rest_framework.permissions import BasePermission


class IsMagasinierOrAdmin(BasePermission):
    """Écriture réservée aux magasiniers et admins ; lecture pour les autres groupes."""

    WRITE_GROUPS = ('magasinier', 'admin')

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.groups.filter(name__in=self.WRITE_GROUPS).exists() or request.user.is_staff
