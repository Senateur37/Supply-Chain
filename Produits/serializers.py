from rest_framework import serializers
from .models import Produit


class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
