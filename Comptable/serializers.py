from rest_framework import serializers
from .models import FactureAchat, FactureVente


class FactureAchatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactureAchat
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class FactureVenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactureVente
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
