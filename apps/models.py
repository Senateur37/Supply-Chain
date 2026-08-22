from django.conf import settings
from django.db import models
from Produits.models import Produit
from Achats.models import Fournisseur, CommandeAchat
from Entrepots.models import Entrepot
from Ventes.models import Client, CommandeVente


class UserProfile(models.Model):
    """Profil utilisateur lié à un compte (photo, coordonnées, fonction)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    photo = models.ImageField(upload_to='profils/', blank=True, null=True)
    fonction = models.CharField(max_length=150, blank=True, help_text='Poste / fonction')
    telephone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True, help_text='Courte présentation')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateur'

    def __str__(self):
        return f'Profil de {self.user.username}'


class ParametreApp(models.Model):
    """Paramètres globaux de l'application (nom d'entreprise, logo, coordonnées...).

    Modèle singleton : une seule instance doit exister en base.
    """

    nom_entreprise = models.CharField(
        max_length=200, default='Supply Chain', help_text='Nom de l\'entreprise affiché dans l\'application'
    )
    slogan = models.CharField(max_length=200, blank=True, help_text='Slogan ou sous-titre')
    logo = models.ImageField(
        upload_to='logos/', blank=True, null=True, help_text='Logo affiché dans l\'en-tête'
    )
    email_contact = models.EmailField(blank=True, help_text='Email de contact')
    telephone = models.CharField(max_length=20, blank=True, help_text='Téléphone de contact')
    adresse = models.TextField(blank=True, help_text='Adresse de l\'entreprise')
    devise = models.CharField(max_length=10, default='FCFA', help_text='Devise utilisée (ex. FCFA, €, $)')
    pied_de_page = models.TextField(
        blank=True, help_text='Mention affichée en pied de page des documents'
    )
    couleur_principale = models.CharField(
        max_length=7, default='#14345B', help_text='Couleur principale du thème (barre latérale, titres)'
    )
    couleur_accent = models.CharField(
        max_length=7, default='#0EA5A4', help_text='Couleur d\'accent du thème (logo, éléments clés)'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètre de l\'application'
        verbose_name_plural = 'Paramètres de l\'application'

    def __str__(self):
        return self.nom_entreprise

    @classmethod
    def get_instance(cls):
        """Retourne l'unique instance, en la créant si nécessaire."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1  # force le singleton
        super().save(*args, **kwargs)


class SuiviExpedition(models.Model):
    """Modèle de suivi d'une expédition produit du fournisseur au client."""

    STATUT_CHOICES = [
        ('1_FOURNISSEUR', 'Fournisseur — Commande / Prêt au départ'),
        ('2_TRANSIT_ENTREPOT', 'Transit — En route vers Entrepôt'),
        ('3_ENTREPOT', 'Entrepôt — Reçu & En Stock'),
        ('4_TRANSIT_CLIENT', 'Transit — En cours de livraison Client'),
        ('5_LIVRE', 'Client — Produit Livré'),
    ]

    numero_suivi = models.CharField(max_length=50, unique=True, db_index=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='suivis')
    quantite = models.PositiveIntegerField(default=1)

    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='expeditions')
    entrepot = models.ForeignKey(Entrepot, on_delete=models.SET_NULL, null=True, blank=True, related_name='expeditions')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='expeditions')

    commande_achat = models.ForeignKey(CommandeAchat, on_delete=models.SET_NULL, null=True, blank=True, related_name='expeditions')
    commande_vente = models.ForeignKey(CommandeVente, on_delete=models.SET_NULL, null=True, blank=True, related_name='expeditions')

    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='1_FOURNISSEUR')

    # Coordonnées GPS des 3 pôles principaux
    lat_fournisseur = models.FloatField(default=12.6392, help_text='Latitude Fournisseur')
    lng_fournisseur = models.FloatField(default=-8.0029, help_text='Longitude Fournisseur')
    lat_entrepot = models.FloatField(default=12.6500, help_text='Latitude Entrepôt')
    lng_entrepot = models.FloatField(default=-7.9800, help_text='Longitude Entrepôt')
    lat_client = models.FloatField(default=12.6100, help_text='Latitude Client')
    lng_client = models.FloatField(default=-7.9500, help_text='Longitude Client')

    # GPS en temps réel du véhicule / produit
    lat_actuelle = models.FloatField(default=12.6392, help_text='Latitude actuelle GPS')
    lng_actuelle = models.FloatField(default=-8.0029, help_text='Longitude actuelle GPS')
    vitesse_kmh = models.FloatField(default=0.0, help_text='Vitesse instantanée en km/h')
    progression_pct = models.PositiveIntegerField(default=0, help_text='Progression globale 0-100%')

    # Informations Transporteur
    transporteur = models.CharField(max_length=100, blank=True, default='Logistique Express')
    immatriculation_vehicule = models.CharField(max_length=50, blank=True, default='M-1234-BK')
    nom_chauffeur = models.CharField(max_length=100, blank=True, default='Moussa Traoré')
    telephone_chauffeur = models.CharField(max_length=20, blank=True, default='+223 70 00 00 00')

    # Dates
    date_expedition = models.DateTimeField(null=True, blank=True)
    date_livraison_estimee = models.DateTimeField(null=True, blank=True)
    date_livraison_effective = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Suivi d\'expédition'
        verbose_name_plural = 'Suivis d\'expédition'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.numero_suivi} – {self.produit.designation} ({self.get_statut_display()})'


class EtapeSuivi(models.Model):
    """Jalon ou événement horodaté dans l'historique d'une expédition."""

    expedition = models.ForeignKey(SuiviExpedition, on_delete=models.CASCADE, related_name='etapes')
    code_etape = models.CharField(max_length=30)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lieu = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    date_etape = models.DateTimeField(auto_now_add=True)
    est_terminee = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Étape de suivi'
        verbose_name_plural = 'Étapes de suivi'
        ordering = ['date_etape']

    def __str__(self):
        return f'{self.expedition.numero_suivi} - {self.titre}'


class PositionGPSHistorique(models.Model):
    """Historique des positions GPS enregistrées au fil du trajet."""

    expedition = models.ForeignKey(SuiviExpedition, on_delete=models.CASCADE, related_name='historique_positions')
    latitude = models.FloatField()
    longitude = models.FloatField()
    vitesse = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Position GPS'
        verbose_name_plural = 'Positions GPS'
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.expedition.numero_suivi} @ ({self.latitude}, {self.longitude})'

