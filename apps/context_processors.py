from .models import ParametreApp, UserProfile


def parametres_app(request):
    """Injecte les paramètres de l'application dans tous les templates."""
    try:
        params = ParametreApp.get_instance()
    except Exception:
        params = None

    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None

    return {'parametres': params, 'user_profile': user_profile}
