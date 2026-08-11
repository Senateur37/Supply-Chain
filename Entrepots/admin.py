from django.contrib import admin
from .models import Entrepot


@admin.register(Entrepot)
class EntrepotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'responsable', 'telephone', 'capacite_totale', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom', 'responsable')
    readonly_fields = ('created_at', 'updated_at')
