from django.contrib import admin
from .models import Client, CommandeVente, LigneCommandeVente


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'email', 'telephone', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom', 'email')
    readonly_fields = ('created_at', 'updated_at')


class LigneCommandeVenteInline(admin.TabularInline):
    model = LigneCommandeVente
    extra = 1
    readonly_fields = ('montant_total',)


@admin.register(CommandeVente)
class CommandeVenteAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'date_commande', 'date_livraison_prevue', 'statut')
    list_filter = ('statut',)
    search_fields = ('reference', 'client__nom')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LigneCommandeVenteInline]
