from rest_framework.routers import DefaultRouter
from .views import StockViewSet, MouvementStockViewSet

router = DefaultRouter()
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'mouvements', MouvementStockViewSet, basename='mouvement-stock')

urlpatterns = router.urls
