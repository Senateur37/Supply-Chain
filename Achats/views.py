from rest_framework import viewsets, filters
from .models import Fournisseur, CommandeAchat, LigneCommandeAchat
from .serializers import FournisseurSerializer, CommandeAchatSerializer, LigneCommandeAchatSerializer
from .permissions import IsGestionnaireAchatsOrAdmin


class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = [IsGestionnaireAchatsOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'email']
    ordering_fields = ['nom']


class CommandeAchatViewSet(viewsets.ModelViewSet):
    queryset = CommandeAchat.objects.select_related('fournisseur').prefetch_related('lignes__produit')
    serializer_class = CommandeAchatSerializer
    permission_classes = [IsGestionnaireAchatsOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference', 'fournisseur__nom']
    ordering_fields = ['date_commande', 'statut']


class LigneCommandeAchatViewSet(viewsets.ModelViewSet):
    queryset = LigneCommandeAchat.objects.select_related('commande', 'produit')
    serializer_class = LigneCommandeAchatSerializer
    permission_classes = [IsGestionnaireAchatsOrAdmin]
