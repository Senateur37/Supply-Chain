from rest_framework.routers import DefaultRouter
from .views import FactureAchatViewSet, FactureVenteViewSet

router = DefaultRouter()
router.register(r'factures-achat', FactureAchatViewSet, basename='facture-achat')
router.register(r'factures-vente', FactureVenteViewSet, basename='facture-vente')

urlpatterns = router.urls
