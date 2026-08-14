from .models import ParametreApp, UserProfile


def parametres_app(request):
    """Injecte les paramètres de l'application dans tous les templates."""
    try:
        params = ParametreApp.get_instance()
    except Exception:
        params = None

    user_profile = None
    user_roles = set()
    if request.user.is_authenticated:
        user_roles = set(request.user.groups.values_list('name', flat=True))
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None

    return {
        'parametres': params,
        'user_profile': user_profile,
        'user_roles': user_roles,
        'is_admin': request.user.is_authenticated and (
            request.user.is_staff or 'admin' in user_roles
        ),
    }
