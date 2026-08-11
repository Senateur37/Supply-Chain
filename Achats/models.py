from django.db import models
from Produits.models import Produit


class Fournisseur(models.Model):
    nom = models.CharField(max_length=200, unique=True)
    contact = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class CommandeAchat(models.Model):
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('CONFIRMEE', 'Confirmée'),
        ('EN_COURS', 'En cours de livraison'),
        ('RECUE', 'Reçue'),
        ('ANNULEE', 'Annulée'),
    ]

    reference = models.CharField(max_length=50, unique=True, db_index=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name='commandes')
    date_commande = models.DateField()
    date_livraison_prevue = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='BROUILLON')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Commande d\'achat'
        verbose_name_plural = 'Commandes d\'achat'
        ordering = ['-date_commande']

    def __str__(self):
        return f'{self.reference} – {self.fournisseur}'


class LigneCommandeAchat(models.Model):
    commande = models.ForeignKey(CommandeAchat, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lignes_achat')
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Ligne de commande achat'
        verbose_name_plural = 'Lignes de commande achat'
        unique_together = ('commande', 'produit')

    def __str__(self):
        return f'{self.commande.reference} – {self.produit.designation} x{self.quantite}'

    @property
    def montant_total(self):
        return self.quantite * self.prix_unitaire
