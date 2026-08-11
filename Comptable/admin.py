from django.contrib import admin
from .models import FactureAchat, FactureVente


@admin.register(FactureAchat)
class FactureAchatAdmin(admin.ModelAdmin):
    list_display = ('reference', 'commande_achat', 'montant_ht', 'montant_ttc', 'date_facture', 'statut')
    list_filter = ('statut',)
    search_fields = ('reference', 'commande_achat__reference')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FactureVente)
class FactureVenteAdmin(admin.ModelAdmin):
    list_display = ('reference', 'commande_vente', 'montant_ht', 'montant_ttc', 'date_facture', 'statut')
    list_filter = ('statut',)
    search_fields = ('reference', 'commande_vente__reference')
    readonly_fields = ('created_at', 'updated_at')
