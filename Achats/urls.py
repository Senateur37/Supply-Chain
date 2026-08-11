from rest_framework.routers import DefaultRouter
from .views import FournisseurViewSet, CommandeAchatViewSet, LigneCommandeAchatViewSet

router = DefaultRouter()
router.register(r'fournisseurs', FournisseurViewSet, basename='fournisseur')
router.register(r'commandes', CommandeAchatViewSet, basename='commande-achat')
router.register(r'lignes', LigneCommandeAchatViewSet, basename='ligne-commande-achat')

urlpatterns = router.urls
