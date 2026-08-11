from django.db import models
from Produits.models import Produit


class Client(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    contact = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class CommandeVente(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('CONFIRMEE', 'Confirmée'),
        ('EN_PREPARATION', 'En préparation'),
        ('EXPEDIEE', 'Expédiée'),
        ('LIVREE', 'Livrée'),
        ('ANNULEE', 'Annulée'),
    ]

    reference = models.CharField(max_length=50, unique=True, db_index=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='commandes')
    date_commande = models.DateField()
    date_livraison_prevue = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Commande de vente'
        verbose_name_plural = 'Commandes de vente'
        ordering = ['-date_commande']

    def __str__(self):
        return f'{self.reference} – {self.client}'


class LigneCommandeVente(models.Model):
    commande = models.ForeignKey(CommandeVente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lignes_vente')
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Ligne de commande vente'
        verbose_name_plural = 'Lignes de commande vente'
        unique_together = ('commande', 'produit')

    def __str__(self):
        return f'{self.commande.reference} – {self.produit.designation} x{self.quantite}'

    @property
    def montant_total(self):
        return self.quantite * self.prix_unitaire
