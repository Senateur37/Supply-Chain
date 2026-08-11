from django.contrib import admin
from .models import Fournisseur, CommandeAchat, LigneCommandeAchat


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'email', 'telephone', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom', 'contact', 'email')
    readonly_fields = ('created_at', 'updated_at')


class LigneCommandeAchatInline(admin.TabularInline):
    model = LigneCommandeAchat
    extra = 1
    readonly_fields = ('montant_total',)


@admin.register(CommandeAchat)
class CommandeAchatAdmin(admin.ModelAdmin):
    list_display = ('reference', 'fournisseur', 'date_commande', 'date_livraison_prevue', 'statut')
    list_filter = ('statut',)
    search_fields = ('reference', 'fournisseur__nom')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LigneCommandeAchatInline]
