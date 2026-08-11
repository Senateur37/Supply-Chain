from rest_framework import viewsets, filters
from .models import Stock, MouvementStock
from .serializers import StockSerializer, MouvementStockSerializer
from .permissions import IsMagasinierOrAdminInventaire


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('produit', 'entrepot')
    serializer_class = StockSerializer
    permission_classes = [IsMagasinierOrAdminInventaire]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produit__designation', 'produit__reference', 'entrepot__nom']
    ordering_fields = ['produit__designation', 'quantite_disponible']


class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.select_related('produit', 'entrepot')
    serializer_class = MouvementStockSerializer
    permission_classes = [IsMagasinierOrAdminInventaire]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['produit__designation', 'reference_document']
    ordering_fields = ['date_mouvement', 'type_mouvement']
