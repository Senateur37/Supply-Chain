from rest_framework import serializers
from .models import Client, CommandeVente, LigneCommandeVente


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class LigneCommandeVenteSerializer(serializers.ModelSerializer):
    montant_total = serializers.ReadOnlyField()

    class Meta:
        model = LigneCommandeVente
        fields = '__all__'
        read_only_fields = ('id',)


class CommandeVenteSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeVenteSerializer(many=True, read_only=True)

    class Meta:
        model = CommandeVente
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
