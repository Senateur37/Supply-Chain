from django.conf import settings
from django.db import models


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
