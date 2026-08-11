from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, CommandeVenteViewSet, LigneCommandeVenteViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'commandes', CommandeVenteViewSet, basename='commande-vente')
router.register(r'lignes', LigneCommandeVenteViewSet, basename='ligne-commande-vente')

urlpatterns = router.urls
