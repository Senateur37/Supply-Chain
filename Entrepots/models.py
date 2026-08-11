from django.db import models


class Entrepot(models.Model):
    nom = models.CharField(max_length=150, unique=True)
    adresse = models.TextField()
    responsable = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, blank=True)
    capacite_totale = models.PositiveIntegerField(help_text='Capacité maximale en unités de stockage')
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Entrepôt'
        verbose_name_plural = 'Entrepôts'
        ordering = ['nom']

    def __str__(self):
        return self.nom
