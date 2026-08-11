from rest_framework import viewsets, filters
from .models import Entrepot
from .serializers import EntrepotSerializer
from .permissions import IsMagasinierOrAdmin


class EntrepotViewSet(viewsets.ModelViewSet):
    queryset = Entrepot.objects.all()
    serializer_class = EntrepotSerializer
    permission_classes = [IsMagasinierOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'responsable']
    ordering_fields = ['nom', 'capacite_totale']
