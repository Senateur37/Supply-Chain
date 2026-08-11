from rest_framework import serializers
from .models import Entrepot


class EntrepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrepot
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
