from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


ROLE_CHOICES = (
    ('admin', 'Administrateur'),
    ('gestionnaire_achats', 'Gestionnaire des achats'),
    ('magasinier', 'Magasinier'),
    ('commercial', 'Commercial'),
    ('comptable', 'Comptable'),
    ('auditeur', 'Auditeur'),
)


def role_required(*roles):
    """Restreint une vue aux rôles indiqués et aux administrateurs."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if user.is_staff or user.groups.filter(name__in=('admin', *roles)).exists():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator