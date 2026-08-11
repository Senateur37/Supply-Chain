from rest_framework import serializers
from .models import Fournisseur, CommandeAchat, LigneCommandeAchat


class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class LigneCommandeAchatSerializer(serializers.ModelSerializer):
    montant_total = serializers.ReadOnlyField()

    class Meta:
        model = LigneCommandeAchat
        fields = '__all__'
        read_only_fields = ('id',)


class CommandeAchatSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeAchatSerializer(many=True, read_only=True)

    class Meta:
        model = CommandeAchat
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
