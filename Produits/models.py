from django.db import models


class Produit(models.Model):
    UNITE_CHOICES = [
        ('PCS', 'Pièce'),
        ('KG', 'Kilogramme'),
        ('L', 'Litre'),
        ('M', 'Mètre'),
        ('BOITE', 'Boîte'),
        ('PALETTE', 'Palette'),
    ]

    reference = models.CharField(max_length=50, unique=True, db_index=True)
    designation = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    unite_mesure = models.CharField(max_length=10, choices=UNITE_CHOICES, default='PCS')
    stock_minimum = models.PositiveIntegerField(default=0)
    stock_securite = models.PositiveIntegerField(default=0)
    stock_alerte = models.PositiveIntegerField(default=0)
    stock_maximum = models.PositiveIntegerField(default=0)
    montant = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['designation']

    def __str__(self):
        return f'{self.reference} – {self.designation}'
