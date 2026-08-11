from django.db import models
from Produits.models import Produit
from Entrepots.models import Entrepot


class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='stocks', db_index=True)
    entrepot = models.ForeignKey(Entrepot, on_delete=models.PROTECT, related_name='stocks', db_index=True)
    quantite_disponible = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        unique_together = ('produit', 'entrepot')

    def __str__(self):
        return f'{self.produit} – {self.entrepot} : {self.quantite_disponible}'


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
        ('TRANSFERT', 'Transfert'),
        ('AJUSTEMENT', 'Ajustement'),
    ]

    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='mouvements', db_index=True)
    entrepot = models.ForeignKey(Entrepot, on_delete=models.PROTECT, related_name='mouvements')
    type_mouvement = models.CharField(max_length=15, choices=TYPE_CHOICES)
    quantite = models.IntegerField(help_text='Positif pour entrée, négatif pour sortie')
    reference_document = models.CharField(max_length=100, blank=True, db_index=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-date_mouvement']

    def __str__(self):
        return f'{self.type_mouvement} – {self.produit} – {self.quantite}'
