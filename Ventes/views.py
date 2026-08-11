from rest_framework import viewsets, filters
from .models import Client, CommandeVente, LigneCommandeVente
from .serializers import ClientSerializer, CommandeVenteSerializer, LigneCommandeVenteSerializer
from .permissions import IsCommercialOrAdmin


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsCommercialOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email']
    ordering_fields = ['nom']


class CommandeVenteViewSet(viewsets.ModelViewSet):
    queryset = CommandeVente.objects.select_related('client').prefetch_related('lignes__produit')
    serializer_class = CommandeVenteSerializer
    permission_classes = [IsCommercialOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference', 'client__nom']
    ordering_fields = ['date_commande', 'statut']


class LigneCommandeVenteViewSet(viewsets.ModelViewSet):
    queryset = LigneCommandeVente.objects.select_related('commande', 'produit')
    serializer_class = LigneCommandeVenteSerializer
    permission_classes = [IsCommercialOrAdmin]
