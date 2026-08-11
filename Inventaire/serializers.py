from rest_framework import serializers
from .models import Stock, MouvementStock


class StockSerializer(serializers.ModelSerializer):
    produit_designation = serializers.CharField(source='produit.designation', read_only=True)
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)

    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ('id', 'updated_at')


class MouvementStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementStock
        fields = '__all__'
        read_only_fields = ('id', 'date_mouvement')
