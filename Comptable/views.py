from rest_framework import viewsets, filters
from .models import FactureAchat, FactureVente
from .serializers import FactureAchatSerializer, FactureVenteSerializer
from .permissions import IsComptableOrAdmin


class FactureAchatViewSet(viewsets.ModelViewSet):
    queryset = FactureAchat.objects.select_related('commande_achat')
    serializer_class = FactureAchatSerializer
    permission_classes = [IsComptableOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference', 'commande_achat__reference']
    ordering_fields = ['date_facture', 'statut', 'montant_ttc']


class FactureVenteViewSet(viewsets.ModelViewSet):
    queryset = FactureVente.objects.select_related('commande_vente')
    serializer_class = FactureVenteSerializer
    permission_classes = [IsComptableOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference', 'commande_vente__reference']
    ordering_fields = ['date_facture', 'statut', 'montant_ttc']
