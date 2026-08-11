from django.db import models
from Achats.models import CommandeAchat
from Ventes.models import CommandeVente


class FactureAchat(models.Model):
    STATUT_CHOICES = [
        ('RECUE', 'Reçue'),
        ('VALIDEE', 'Validée'),
        ('PAYEE', 'Payée'),
        ('CONTESTEE', 'Contestée'),
    ]

    reference = models.CharField(max_length=100, unique=True, db_index=True)
    commande_achat = models.ForeignKey(
        CommandeAchat, on_delete=models.PROTECT,
        related_name='factures', null=True, blank=True
    )
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2)
    date_facture = models.DateField()
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='RECUE')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Facture achat'
        verbose_name_plural = 'Factures achat'
        ordering = ['-date_facture']

    def __str__(self):
        return f'{self.reference} – {self.montant_ttc} FCFA'


class FactureVente(models.Model):
    STATUT_CHOICES = [
        ('EMISE', 'Émise'),
        ('ENVOYEE', 'Envoyée'),
        ('PAYEE', 'Payée'),
        ('IMPAYEE', 'Impayée'),
        ('ANNULEE', 'Annulée'),
    ]

    reference = models.CharField(max_length=100, unique=True, db_index=True)
    commande_vente = models.ForeignKey(
        CommandeVente, on_delete=models.PROTECT,
        related_name='factures', null=True, blank=True
    )
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    montant_ttc = models.DecimalField(max_digits=14, decimal_places=2)
    date_facture = models.DateField()
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='EMISE')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Facture vente'
        verbose_name_plural = 'Factures vente'
        ordering = ['-date_facture']

    def __str__(self):
        return f'{self.reference} – {self.montant_ttc} FCFA'
