from django import forms
from Produits.models import Produit
from Entrepots.models import Entrepot
from Achats.models import Fournisseur, CommandeAchat
from Ventes.models import Client, CommandeVente
from Inventaire.models import Stock, MouvementStock
from Comptable.models import FactureAchat, FactureVente
from .models import ParametreApp, UserProfile


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'reference', 'designation', 'description', 'prix_unitaire', 'unite_mesure',
            'stock_minimum', 'stock_securite', 'stock_alerte', 'stock_maximum', 'montant',
        ]
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. REF-001'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description (optionnel)'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unite_mesure': forms.Select(attrs={'class': 'form-control'}),
            'stock_minimum': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_securite': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_alerte': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'stock_maximum': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class EntrepotForm(forms.ModelForm):
    class Meta:
        model = Entrepot
        fields = ['nom', 'adresse', 'responsable', 'telephone', 'capacite_totale']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. Entrepôt central'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du responsable'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone (optionnel)'}),
            'capacite_totale': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'email', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personne de contact'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse (optionnel)'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'contact', 'email', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du client'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Personne de contact'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse (optionnel)'}),
        }


class CommandeAchatForm(forms.ModelForm):
    class Meta:
        model = CommandeAchat
        fields = ['reference', 'fournisseur', 'date_commande', 'date_livraison_prevue', 'statut']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. CA-001'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'date_commande': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_livraison_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class CommandeVenteForm(forms.ModelForm):
    class Meta:
        model = CommandeVente
        fields = ['reference', 'client', 'date_commande', 'date_livraison_prevue', 'statut']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. CV-001'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'date_commande': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_livraison_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'entrepot', 'type_mouvement', 'quantite', 'reference_document', 'notes']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'entrepot': forms.Select(attrs={'class': 'form-control'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'help_text': 'Positif pour entrée, négatif pour sortie'}),
            'reference_document': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Réf. document (optionnel)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes (optionnel)'}),
        }

    def clean_quantite(self):
        q = self.cleaned_data['quantite']
        if q == 0:
            raise forms.ValidationError('La quantité ne peut pas être nulle.')
        return q


class FactureAchatForm(forms.ModelForm):
    class Meta:
        model = FactureAchat
        fields = ['reference', 'commande_achat', 'montant_ht', 'taux_tva', 'montant_ttc', 'date_facture', 'date_echeance', 'statut']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. FA-001'}),
            'commande_achat': forms.Select(attrs={'class': 'form-control'}),
            'montant_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'date_facture': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class FactureVenteForm(forms.ModelForm):
    class Meta:
        model = FactureVente
        fields = ['reference', 'commande_vente', 'montant_ht', 'taux_tva', 'montant_ttc', 'date_facture', 'date_echeance', 'statut']
        widgets = {
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. FV-001'}),
            'commande_vente': forms.Select(attrs={'class': 'form-control'}),
            'montant_ht': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'taux_tva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_ttc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'date_facture': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class ParametreAppForm(forms.ModelForm):
    class Meta:
        model = ParametreApp
        fields = [
            'nom_entreprise', 'slogan', 'logo', 'email_contact',
            'telephone', 'adresse', 'devise', 'pied_de_page',
            'couleur_principale', 'couleur_accent',
        ]
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de votre entreprise'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sous-titre / slogan'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'email_contact': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@entreprise.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+225 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse de l\'entreprise'}),
            'devise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FCFA'}),
            'pied_de_page': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Mention en pied de page des documents'}),
            'couleur_principale': forms.TextInput(attrs={'class': 'form-control color-input', 'type': 'color'}),
            'couleur_accent': forms.TextInput(attrs={'class': 'form-control color-input', 'type': 'color'}),
        }


class UserProfileForm(forms.ModelForm):
    """Formulaire d'édition du profil utilisateur (photo, coordonnées, fonction)."""

    class Meta:
        model = UserProfile
        fields = ['photo', 'fonction', 'telephone', 'bio']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. Responsable logistique'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+225 00 00 00 00'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Courte présentation (optionnel)'}),
        }
