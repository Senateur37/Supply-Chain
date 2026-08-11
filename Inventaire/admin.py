from django.contrib import admin
from .models import Stock, MouvementStock


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'entrepot', 'quantite_disponible', 'updated_at')
    list_filter = ('entrepot',)
    search_fields = ('produit__designation', 'produit__reference', 'entrepot__nom')
    readonly_fields = ('updated_at',)


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('date_mouvement', 'type_mouvement', 'produit', 'entrepot', 'quantite', 'reference_document')
    list_filter = ('type_mouvement', 'entrepot')
    search_fields = ('produit__designation', 'reference_document')
    readonly_fields = ('date_mouvement',)
