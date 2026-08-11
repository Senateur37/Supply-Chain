from rest_framework import viewsets, filters
from .models import Produit
from .serializers import ProduitSerializer
from .permissions import IsAdminOrReadOnly


class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference', 'designation']
    ordering_fields = ['reference', 'designation', 'prix_unitaire']
