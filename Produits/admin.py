from django.contrib import admin
from .models import Produit


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('reference', 'designation', 'prix_unitaire', 'unite_mesure', 'stock_minimum', 'actif')
    list_filter = ('actif', 'unite_mesure')
    search_fields = ('reference', 'designation')
    readonly_fields = ('created_at', 'updated_at')
