import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from Produits.models import Produit
from Entrepots.models import Entrepot
from Achats.models import Fournisseur, CommandeAchat
from Inventaire.models import Stock, MouvementStock
from Ventes.models import Client, CommandeVente
from Comptable.models import FactureAchat, FactureVente
from .forms import (
    ProduitForm, EntrepotForm, FournisseurForm, ClientForm,
    CommandeAchatForm, CommandeVenteForm, MouvementStockForm,
    FactureAchatForm, FactureVenteForm, ParametreAppForm, UserProfileForm,
    UtilisateurForm, UtilisateurModificationForm,
    SuiviExpeditionForm, MiseAJourPositionGPSForm,
)
from .models import ParametreApp, UserProfile, SuiviExpedition, EtapeSuivi, PositionGPSHistorique
from .permissions import role_required


logger = logging.getLogger('django.request')
User = get_user_model()


def administrateur_requis(user):
    return user.is_staff or user.groups.filter(name='admin').exists()


def appliquer_role(utilisateur, role):
    """Associe un seul rôle métier au compte et synchronise le statut admin."""
    utilisateur.groups.set([Group.objects.get_or_create(name=role)[0]])
    if not utilisateur.is_superuser:
        utilisateur.is_staff = role == 'admin'
        utilisateur.save(update_fields=['is_staff'])


@login_required
def dashboard_view(request):
    nb_produits = Produit.objects.count()
    nb_entrepots = Entrepot.objects.count()
    nb_fournisseurs = Fournisseur.objects.count()
    nb_clients = Client.objects.count()

    nb_commandes_achat = CommandeAchat.objects.count()
    nb_commandes_vente = CommandeVente.objects.count()

    # Stock total (somme des quantités disponibles)
    stock_total = Stock.objects.aggregate(total=Sum('quantite_disponible'))['total'] or 0

    # Alertes stock bas : productions dont le stock total < stock_minimum
    produits = Produit.objects.filter(actif=True)
    alertes = []
    for p in produits:
        q = p.stocks.aggregate(t=Sum('quantite_disponible'))['t'] or 0
        if q < p.stock_minimum:
            alertes.append({'produit': p, 'quantite': q})

    # Derniers mouvements de stock
    mouvements = MouvementStock.objects.select_related('produit', 'entrepot')[:8]

    # Ventilation des factures (montants)
    ca_ttc = FactureVente.objects.exclude(statut='ANNULEE').aggregate(t=Sum('montant_ttc'))['t'] or 0
    achats_ttc = FactureAchat.objects.aggregate(t=Sum('montant_ttc'))['t'] or 0

    # --- Historique des activités récentes ---
    activites = []

    for m in MouvementStock.objects.select_related('produit', 'entrepot')[:8]:
        activites.append({
            'type': 'stock',
            'type_label': 'Stock',
            'date': m.date_mouvement,
            'description': f"{m.get_type_mouvement_display()} — {m.produit.designation} ({m.quantite:+d})",
        })

    for c in CommandeAchat.objects.select_related('fournisseur')[:6]:
        activites.append({
            'type': 'achat',
            'type_label': 'Achat',
            'date': c.created_at,
            'description': f"Commande {c.reference} — {c.fournisseur.nom}",
        })

    for c in CommandeVente.objects.select_related('client')[:6]:
        activites.append({
            'type': 'vente',
            'type_label': 'Vente',
            'date': c.created_at,
            'description': f"Commande {c.reference} — {c.client.nom}",
        })

    for f in FactureAchat.objects.all()[:5]:
        activites.append({
            'type': 'facture_achat',
            'type_label': 'Facture achat',
            'date': f.created_at,
            'description': f"{f.reference} — {f.montant_ttc:,.0f} FCFA",
        })

    for f in FactureVente.objects.all()[:5]:
        activites.append({
            'type': 'facture_vente',
            'type_label': 'Facture vente',
            'date': f.created_at,
            'description': f"{f.reference} — {f.montant_ttc:,.0f} FCFA",
        })

    activites.sort(key=lambda a: a['date'], reverse=True)
    activites = activites[:12]

    context = {
        'nb_produits': nb_produits,
        'nb_entrepots': nb_entrepots,
        'nb_fournisseurs': nb_fournisseurs,
        'nb_clients': nb_clients,
        'nb_commandes_achat': nb_commandes_achat,
        'nb_commandes_vente': nb_commandes_vente,
        'stock_total': stock_total,
        'alertes': alertes,
        'mouvements': mouvements,
        'ca_ttc': ca_ttc,
        'achats_ttc': achats_ttc,
        'activites': activites,
    }
    return render(request, 'dashboard.html', context)


@role_required('magasinier', 'gestionnaire_achats', 'commercial', 'comptable', 'auditeur')
def produits_view(request):
    form = ProduitForm()
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit créé avec succès.')
            return redirect('produits')
    recherche = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '').strip()
    produits = Produit.objects.all()
    if recherche:
        produits = produits.filter(Q(reference__icontains=recherche) | Q(designation__icontains=recherche))
    if statut in ('actif', 'inactif'):
        produits = produits.filter(actif=statut == 'actif')
    context = {
        'produits': produits,
        'nb_produits': produits.count(),
        'nb_actifs': produits.filter(actif=True).count(),
        'form': form,
        'recherche': recherche,
        'statut_filtre': statut,
    }
    return render(request, 'produits.html', context)


@role_required('magasinier', 'gestionnaire_achats', 'commercial', 'auditeur')
def produit_edit(request, pk):
    """Modifie un produit existant."""
    produit = get_object_or_404(Produit, pk=pk)
    form = ProduitForm(instance=produit)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit modifié avec succès.')
            return redirect('produits')
    return render(request, 'produits.html', {
        'form': form,
        'edit_instance': produit,
        'produits': Produit.objects.all(),
        'nb_produits': Produit.objects.count(),
        'nb_actifs': Produit.objects.filter(actif=True).count(),
    })


@role_required('magasinier', 'gestionnaire_achats', 'commercial', 'auditeur')
def produit_delete(request, pk):
    """Supprime un produit."""
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, 'Produit supprimé avec succès.')
    return redirect('produits')



@role_required('magasinier', 'gestionnaire_achats', 'auditeur')
def fournisseur_edit(request, pk):
    """Modifie un fournisseur existant."""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    form = FournisseurForm(instance=fournisseur)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur modifié avec succès.')
            return redirect('achats')
    return render(request, 'achats.html', {
        'fournisseur_form': form,
        'commande_form': CommandeAchatForm(),
        'edit_instance': fournisseur,
        'fournisseurs': Fournisseur.objects.all(),
        'commandes': CommandeAchat.objects.select_related('fournisseur').prefetch_related('lignes'),
        'nb_fournisseurs': Fournisseur.objects.count(),
        'nb_commandes': CommandeAchat.objects.count(),
        'en_attente': CommandeAchat.objects.exclude(statut__in=['RECUE', 'ANNULEE']).count(),
    })


@role_required('magasinier', 'gestionnaire_achats', 'auditeur')
def fournisseur_delete(request, pk):
    """Supprime un fournisseur."""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, 'Fournisseur supprimé avec succès.')
    return redirect('achats')


@role_required('magasinier', 'auditeur')
def entrepots_view(request):

    form = EntrepotForm()
    if request.method == 'POST':
        form = EntrepotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrepôt créé avec succès.')
            return redirect('entrepots')
    recherche = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '').strip()
    entrepots = Entrepot.objects.annotate(
        nb_stocks=Count('stocks'),
        stock_total=Sum('stocks__quantite_disponible'),
    )
    if recherche:
        entrepots = entrepots.filter(
            Q(nom__icontains=recherche) | Q(adresse__icontains=recherche) |
            Q(responsable__icontains=recherche)
        )
    if statut in ('actif', 'inactif'):
        entrepots = entrepots.filter(actif=statut == 'actif')
    context = {
        'entrepots': entrepots,
        'nb_entrepots': entrepots.count(),
        'nb_actifs': entrepots.filter(actif=True).count(),
                'form': form,
            'recherche': recherche,
            'statut_filtre': statut,
    }
    return render(request, 'entrepots.html', context)


@role_required('magasinier', 'auditeur')
def entrepot_edit(request, pk):
    """Modifie un entrepôt existant."""
    entrepot = get_object_or_404(Entrepot, pk=pk)
    form = EntrepotForm(instance=entrepot)
    if request.method == 'POST':
        form = EntrepotForm(request.POST, instance=entrepot)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrepôt modifié avec succès.')
            return redirect('entrepots')
    return render(request, 'entrepots.html', {
        'form': form,
        'edit_instance': entrepot,
        'entrepots': Entrepot.objects.all(),
        'nb_entrepots': Entrepot.objects.count(),
        'nb_actifs': Entrepot.objects.filter(actif=True).count(),
    })


@role_required('magasinier', 'auditeur')
def entrepot_delete(request, pk):
    """Supprime un entrepôt."""
    entrepot = get_object_or_404(Entrepot, pk=pk)
    if request.method == 'POST':
        entrepot.delete()
        messages.success(request, 'Entrepôt supprimé avec succès.')
    return redirect('entrepots')


@role_required('gestionnaire_achats', 'auditeur')
def achats_view(request):
    fournisseur_form = FournisseurForm()
    commande_form = CommandeAchatForm()
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'fournisseur':
            fournisseur_form = FournisseurForm(request.POST)
            if fournisseur_form.is_valid():
                fournisseur_form.save()
                messages.success(request, 'Fournisseur créé avec succès.')
                return redirect('achats')
        elif form_type == 'commande':
            commande_form = CommandeAchatForm(request.POST)
            if commande_form.is_valid():
                commande_form.save()
                messages.success(request, 'Commande d\'achat créée avec succès.')
                return redirect('achats')
    recherche = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '').strip()
    fournisseurs = Fournisseur.objects.all()
    commandes = CommandeAchat.objects.select_related('fournisseur').prefetch_related('lignes')
    if recherche:
        fournisseurs = fournisseurs.filter(
            Q(nom__icontains=recherche) | Q(contact__icontains=recherche) |
            Q(email__icontains=recherche)
        )
        commandes = commandes.filter(
            Q(reference__icontains=recherche) | Q(fournisseur__nom__icontains=recherche)
        )
    if statut:
        commandes = commandes.filter(statut=statut)
    en_attente = commandes.exclude(statut__in=['RECUE', 'ANNULEE']).count()
    context = {
        'fournisseurs': fournisseurs,
        'commandes': commandes,
        'nb_fournisseurs': fournisseurs.count(),
        'nb_commandes': commandes.count(),
        'en_attente': en_attente,
        'fournisseur_form': fournisseur_form,
        'commande_form': commande_form,
        'recherche': recherche,
        'statut_filtre': statut,
    }
    return render(request, 'achats.html', context)


@role_required('magasinier', 'auditeur')
def inventaire_view(request):
    form = MouvementStockForm()
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save()
            # Mise à jour du stock associé
            stock, _ = Stock.objects.get_or_create(
                produit=mouvement.produit,
                entrepot=mouvement.entrepot,
                defaults={'quantite_disponible': 0},
            )
            stock.quantite_disponible += mouvement.quantite
            if stock.quantite_disponible < 0:
                stock.quantite_disponible = 0
            stock.save()
            messages.success(request, 'Mouvement de stock enregistré.')
            return redirect('inventaire')
    recherche = request.GET.get('q', '').strip()
    type_mouvement = request.GET.get('type_mouvement', '').strip()
    stocks = Stock.objects.select_related('produit', 'entrepot')
    mouvements = MouvementStock.objects.select_related('produit', 'entrepot')
    if recherche:
        filtre = Q(produit__designation__icontains=recherche) | Q(produit__reference__icontains=recherche) | Q(entrepot__nom__icontains=recherche)
        stocks = stocks.filter(filtre)
        mouvements = mouvements.filter(filtre | Q(reference_document__icontains=recherche))
    if type_mouvement in ('ENTREE', 'SORTIE'):
        mouvements = mouvements.filter(type_mouvement=type_mouvement)
    mouvements = mouvements[:12]
    stock_total = stocks.aggregate(t=Sum('quantite_disponible'))['t'] or 0
    context = {
        'stocks': stocks,
        'mouvements': mouvements,
        'nb_lignes_stock': stocks.count(),
        'stock_total': stock_total,
        'nb_mouvements': MouvementStock.objects.count(),
                'form': form,
            'recherche': recherche,
            'type_mouvement_filtre': type_mouvement,
    }
    return render(request, 'inventaire.html', context)


@role_required('commercial', 'auditeur')
def ventes_view(request):
    client_form = ClientForm()
    commande_form = CommandeVenteForm()
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'client':
            client_form = ClientForm(request.POST)
            if client_form.is_valid():
                client_form.save()
                messages.success(request, 'Client créé avec succès.')
                return redirect('ventes')
        elif form_type == 'commande':
            commande_form = CommandeVenteForm(request.POST)
            if commande_form.is_valid():
                commande_form.save()
                messages.success(request, 'Commande de vente créée avec succès.')
                return redirect('ventes')
    recherche = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '').strip()
    clients = Client.objects.all()
    commandes = CommandeVente.objects.select_related('client').prefetch_related('lignes')
    if recherche:
        clients = clients.filter(
            Q(nom__icontains=recherche) | Q(contact__icontains=recherche) |
            Q(email__icontains=recherche)
        )
        commandes = commandes.filter(
            Q(reference__icontains=recherche) | Q(client__nom__icontains=recherche)
        )
    if statut:
        commandes = commandes.filter(statut=statut)
    context = {
        'clients': clients,
        'commandes': commandes,
        'nb_clients': clients.count(),
        'nb_commandes': commandes.count(),
        'nb_en_cours': commandes.exclude(statut__in=['LIVREE', 'ANNULEE']).count(),
        'client_form': client_form,
        'commande_form': commande_form,
        'recherche': recherche,
        'statut_filtre': statut,
    }
    return render(request, 'ventes.html', context)


@role_required('commercial', 'auditeur')
def client_edit(request, pk):
    """Modifie un client existant."""
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(instance=client)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client modifié avec succès.')
            return redirect('ventes')
    return render(request, 'ventes.html', {
        'client_form': form,
        'commande_form': CommandeVenteForm(),
        'edit_instance': client,
        'clients': Client.objects.all(),
        'commandes': CommandeVente.objects.select_related('client').prefetch_related('lignes'),
        'nb_clients': Client.objects.count(),
        'nb_commandes': CommandeVente.objects.count(),
        'nb_en_cours': CommandeVente.objects.exclude(statut__in=['LIVREE', 'ANNULEE']).count(),
    })


@role_required('commercial', 'auditeur')
def client_delete(request, pk):
    """Supprime un client."""
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Client supprimé avec succès.')
    return redirect('ventes')


@role_required('comptable', 'auditeur')
def comptable_view(request):

    facture_achat_form = FactureAchatForm()
    facture_vente_form = FactureVenteForm()
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'facture_achat':
            facture_achat_form = FactureAchatForm(request.POST)
            if facture_achat_form.is_valid():
                facture_achat_form.save()
                messages.success(request, 'Facture d\'achat créée avec succès.')
                return redirect('comptable')
        elif form_type == 'facture_vente':
            facture_vente_form = FactureVenteForm(request.POST)
            if facture_vente_form.is_valid():
                facture_vente_form.save()
                messages.success(request, 'Facture de vente créée avec succès.')
                return redirect('comptable')

    recherche = request.GET.get('q', '').strip()
    statut = request.GET.get('statut', '').strip()
    factures_achat = FactureAchat.objects.all()
    factures_vente = FactureVente.objects.all()
    if recherche:
        factures_achat = factures_achat.filter(
            Q(reference__icontains=recherche) | Q(commande_achat__reference__icontains=recherche)
        )
        factures_vente = factures_vente.filter(
            Q(reference__icontains=recherche) | Q(commande_vente__reference__icontains=recherche)
        )
    if statut:
        factures_achat = factures_achat.filter(statut=statut)
        factures_vente = factures_vente.filter(statut=statut)

    # Achats
    total_achat = factures_achat.aggregate(t=Sum('montant_ttc'))['t'] or 0
    ht_achat = factures_achat.aggregate(t=Sum('montant_ht'))['t'] or 0
    a_payer = factures_achat.exclude(statut__in=['PAYEE', 'CONTESTEE']).aggregate(t=Sum('montant_ttc'))['t'] or 0

    # Ventes
    total_vente = factures_vente.exclude(statut='ANNULEE').aggregate(t=Sum('montant_ttc'))['t'] or 0
    ht_vente = factures_vente.exclude(statut='ANNULEE').aggregate(t=Sum('montant_ht'))['t'] or 0
    impayees = factures_vente.filter(statut='IMPAYEE').aggregate(t=Sum('montant_ttc'))['t'] or 0

    # TVA estimée
    tva_collectee = total_vente - ht_vente
    tva_deductible = total_achat - ht_achat
    solde_tva = tva_collectee - tva_deductible

    context = {
        'factures_achat': factures_achat,
        'factures_vente': factures_vente,
        'nb_achat': factures_achat.count(),
        'nb_vente': factures_vente.count(),
        'total_achat': total_achat,
        'total_vente': total_vente,
        'impayees': impayees,
        'a_payer': a_payer,
        'tva_collectee': tva_collectee,
        'tva_deductible': tva_deductible,
        'solde_tva': solde_tva,
        'facture_achat_form': facture_achat_form,
        'facture_vente_form': facture_vente_form,
        'recherche': recherche,
        'statut_filtre': statut,
    }
    return render(request, 'comptable.html', context)


@role_required('auditeur')
def rapports_view(request):
    """Tableau de bord analytique : indicateurs globaux de la chaîne logistique."""
    # Ventes / achats
    ca_ttc = FactureVente.objects.exclude(statut='ANNULEE').aggregate(t=Sum('montant_ttc'))['t'] or 0
    achats_ttc = FactureAchat.objects.aggregate(t=Sum('montant_ttc'))['t'] or 0
    marge = ca_ttc - achats_ttc

    # Commandes
    nb_comm_achat = CommandeAchat.objects.count()
    nb_comm_vente = CommandeVente.objects.count()
    nb_comm_achat_en_cours = CommandeAchat.objects.exclude(statut__in=['RECUE', 'ANNULEE']).count()
    nb_comm_vente_en_cours = CommandeVente.objects.exclude(statut__in=['LIVREE', 'ANNULEE']).count()

    # Factures impayées
    nb_factures_impayees = FactureVente.objects.filter(statut='IMPAYEE').count()

    # Stock par entrepôt
    stocks_par_entrepot = Entrepot.objects.annotate(
        nb_references=Count('stocks'),
        stock_total=Sum('stocks__quantite_disponible'),
    ).filter(stock_total__gt=0)

    # Mouvements par type
    entrees = MouvementStock.objects.filter(quantite__gt=0).aggregate(t=Count('id'))['t'] or 0
    sorties = MouvementStock.objects.filter(quantite__lt=0).aggregate(t=Count('id'))['t'] or 0

    # --- Données pour graphiques ---
    # Évolution mensuelle des ventes et achats (12 derniers mois)
    ventes_mensuel = (
        FactureVente.objects.exclude(statut='ANNULEE')
        .annotate(mois=TruncMonth('date_facture'))
        .values('mois')
        .annotate(total=Sum('montant_ttc'))
        .order_by('mois')
    )
    achats_mensuel = (
        FactureAchat.objects
        .annotate(mois=TruncMonth('date_facture'))
        .values('mois')
        .annotate(total=Sum('montant_ttc'))
        .order_by('mois')
    )

    # Fusionner les mois disponibles
    mois_set = set()
    for r in ventes_mensuel:
        mois_set.add(r['mois'])
    for r in achats_mensuel:
        mois_set.add(r['mois'])
    mois_series = sorted([m for m in mois_set if m])
    # Limiter aux 12 derniers mois
    mois_series = mois_series[-12:]

    vente_series = []
    achat_series = []
    vente_map = {r['mois']: float(r['total']) for r in ventes_mensuel if r['mois']}
    achat_map = {r['mois']: float(r['total']) for r in achats_mensuel if r['mois']}
    mois_labels = []
    for m in mois_series:
        mois_labels.append(m.strftime('%b %Y'))
        vente_series.append(vente_map.get(m, 0))
        achat_series.append(achat_map.get(m, 0))

    # Répartition des commandes d'achat par statut
    commandes_achat_par_statut = CommandeAchat.objects.values('statut').annotate(n=Count('id'))
    # Répartition des commandes de vente par statut
    commandes_vente_par_statut = CommandeVente.objects.values('statut').annotate(n=Count('id'))

    # Répartition des factures de vente par statut
    factures_vente_par_statut = FactureVente.objects.values('statut').annotate(n=Count('id'))

    # Sérialiser les répartitions pour Chart.js dans les templates
    commandes_achat_par_statut_list = list(commandes_achat_par_statut)
    commandes_vente_par_statut_list = list(commandes_vente_par_statut)

    context = {
        'ca_ttc': ca_ttc,
        'achats_ttc': achats_ttc,
        'marge': marge,
        'nb_comm_achat': nb_comm_achat,
        'nb_comm_vente': nb_comm_vente,
        'nb_comm_achat_en_cours': nb_comm_achat_en_cours,
        'nb_comm_vente_en_cours': nb_comm_vente_en_cours,
        'nb_factures_impayees': nb_factures_impayees,
        'stocks_par_entrepot': stocks_par_entrepot,
        'entrees': entrees,
        'sorties': sorties,
        'mois_labels': mois_labels,
        'vente_series': vente_series,
        'achat_series': achat_series,
        'commandes_achat_par_statut': commandes_achat_par_statut,
        'commandes_vente_par_statut': commandes_vente_par_statut,
        'factures_vente_par_statut': factures_vente_par_statut,
        'mois_labels_json': json.dumps(mois_labels),
        'vente_series_json': json.dumps(vente_series),
        'achat_series_json': json.dumps(achat_series),
        'commandes_achat_par_statut_j': json.dumps(commandes_achat_par_statut_list),
        'commandes_vente_par_statut_j': json.dumps(commandes_vente_par_statut_list),
        'entrepot_labels': [e.nom for e in stocks_par_entrepot],
        'entrepot_stocks': [float(e.stock_total or 0) for e in stocks_par_entrepot],
        'entrepot_labels_json': json.dumps([e.nom for e in stocks_par_entrepot]),
        'entrepot_stocks_json': json.dumps([float(e.stock_total or 0) for e in stocks_par_entrepot]),
    }
    return render(request, 'rapports.html', context)


@role_required('auditeur')
def statistiques_view(request):
    """Page de statistiques détaillées : répartitions et indicateurs avancés."""
    # Répartition des produits par statut
    nb_produits_actifs = Produit.objects.filter(actif=True).count()
    nb_produits_inactifs = Produit.objects.filter(actif=False).count()

    # Répartition des entrepôts par statut
    nb_entrepots_actifs = Entrepot.objects.filter(actif=True).count()
    nb_entrepots_inactifs = Entrepot.objects.filter(actif=False).count()

    # Répartition par statut des commandes d'achat
    commandes_achat_par_statut = CommandeAchat.objects.values('statut').annotate(n=Count('id'))

    # Répartition par statut des commandes de vente
    commandes_vente_par_statut = CommandeVente.objects.values('statut').annotate(n=Count('id'))

    # Répartition par statut des factures d'achat
    factures_achat_par_statut = FactureAchat.objects.values('statut').annotate(n=Count('id'))

    # Répartition par statut des factures de vente
    factures_vente_par_statut = FactureVente.objects.values('statut').annotate(n=Count('id'))

    # Valorisation du stock (prix unitaire x quantité disponible)
    stock_valorise = Stock.objects.filter(quantite_disponible__gt=0)
    valeur_stock = 0
    for s in stock_valorise.select_related('produit'):
        valeur_stock += s.quantite_disponible * s.produit.prix_unitaire

    # Top produits par quantité en stock
    top_stocks = Stock.objects.select_related('produit', 'entrepot').order_by('-quantite_disponible')[:8]

    # Top clients par nombre de commandes
    top_clients = Client.objects.annotate(nb_commandes=Count('commandes')).order_by('-nb_commandes')[:8]

    # Top fournisseurs par nombre de commandes
    top_fournisseurs = Fournisseur.objects.annotate(nb_commandes=Count('commandes')).order_by('-nb_commandes')[:8]

    # Total mouvements
    nb_entre_total = MouvementStock.objects.filter(quantite__gt=0).aggregate(t=Sum('quantite'))['t'] or 0
    nb_sortie_total = MouvementStock.objects.filter(quantite__lt=0).aggregate(t=Sum('quantite'))['t'] or 0

    # --- Données pour graphiques ---
    # Valeur du stock par entrepôt
    entrepots_stock = Stock.objects.filter(quantite_disponible__gt=0).select_related('produit', 'entrepot')
    valeur_par_entrepot = {}
    for s in entrepots_stock:
        valeur_par_entrepot[s.entrepot.nom] = valeur_par_entrepot.get(s.entrepot.nom, 0) + (
            s.quantite_disponible * s.produit.prix_unitaire
        )
    entrepot_val_labels = list(valeur_par_entrepot.keys())
    entrepot_val_values = [float(v) for v in valeur_par_entrepot.values()]

    # Répartition produits actifs / inactifs (libellés)
    produits_labels = ['Actifs', 'Inactifs']
    produits_values = [nb_produits_actifs, nb_produits_inactifs]

    # Répartition entrepôts actifs / inactifs
    entrepots_labels = ['Actifs', 'Inactifs']
    entrepots_dispo_values = [nb_entrepots_actifs, nb_entrepots_inactifs]

    # Répartition des mouvements (entrées / sorties)
    mouvements_labels = ['Sorties', 'Entrées']
    mouvements_values = [abs(nb_sortie_total), nb_entre_total]

    # Top stocks : labels et valeurs
    top_stocks_labels = [f"{s.produit.designation}" for s in top_stocks]
    top_stocks_values = [s.quantite_disponible for s in top_stocks]

    context = {
        'nb_produits_actifs': nb_produits_actifs,
        'nb_produits_inactifs': nb_produits_inactifs,
        'nb_entrepots_actifs': nb_entrepots_actifs,
        'nb_entrepots_inactifs': nb_entrepots_inactifs,
        'commandes_achat_par_statut': commandes_achat_par_statut,
        'commandes_vente_par_statut': commandes_vente_par_statut,
        'factures_achat_par_statut': factures_achat_par_statut,
        'factures_vente_par_statut': factures_vente_par_statut,
        'valeur_stock': valeur_stock,
        'top_stocks': top_stocks,
        'top_clients': top_clients,
        'top_fournisseurs': top_fournisseurs,
        'nb_entre_total': nb_entre_total,
        'nb_sortie_total': nb_sortie_total,
        'entrepot_val_labels': entrepot_val_labels,
        'entrepot_val_values': entrepot_val_values,
        'produits_labels': produits_labels,
        'produits_values': produits_values,
        'entrepots_labels': entrepots_labels,
        'entrepots_dispo_values': entrepots_dispo_values,
        'mouvements_labels': mouvements_labels,
        'mouvements_values': mouvements_values,
        'top_stocks_labels': top_stocks_labels,
        'top_stocks_values': top_stocks_values,
        'produits_labels_json': json.dumps(produits_labels),
        'produits_values_json': json.dumps(produits_values),
        'entrepots_labels_json': json.dumps(entrepots_labels),
        'entrepots_dispo_values_json': json.dumps(entrepots_dispo_values),
        'mouvements_labels_json': json.dumps(mouvements_labels),
        'mouvements_values_json': json.dumps(mouvements_values),
        'entrepot_val_labels_json': json.dumps(entrepot_val_labels),
        'entrepot_val_values_json': json.dumps(entrepot_val_values),
        'top_stocks_labels_json': json.dumps(top_stocks_labels),
        'top_stocks_values_json': json.dumps(top_stocks_values),
    }
    return render(request, 'statistiques.html', context)


@role_required('comptable')
def facture_achat_payee(request, pk):
    """Marque une facture d'achat comme payée."""
    facture = get_object_or_404(FactureAchat, pk=pk)
    if request.method == 'POST' and facture.statut != 'PAYEE':
        facture.statut = 'PAYEE'
        facture.save()
        messages.success(request, f'Facture achat {facture.reference} marquée comme payée.')
    return redirect('comptable')


@role_required('comptable', 'auditeur')
def facture_achat_imprimer(request, pk):
    """Affiche une facture d'achat dans une mise en page imprimable."""
    facture = get_object_or_404(FactureAchat, pk=pk)
    tva = facture.montant_ttc - facture.montant_ht
    context = {
        'type': 'achat',
        'titre': 'FACTURE D\'ACHAT',
        'facture': facture,
        'partie': facture.commande_achat.fournisseur if facture.commande_achat else None,
        'partie_label': 'Fournisseur',
        'tva': tva,
    }
    return render(request, 'impression_facture.html', context)


@role_required('comptable', 'auditeur')
def facture_vente_imprimer(request, pk):
    """Affiche une facture de vente dans une mise en page imprimable."""
    facture = get_object_or_404(FactureVente, pk=pk)
    tva = facture.montant_ttc - facture.montant_ht
    context = {
        'type': 'vente',
        'titre': 'FACTURE DE VENTE',
        'facture': facture,
        'partie': facture.commande_vente.client if facture.commande_vente else None,
        'partie_label': 'Client',
        'tva': tva,
    }
    return render(request, 'impression_facture.html', context)


@role_required('comptable')
def facture_vente_payee(request, pk):
    """Marque une facture de vente comme payée."""
    facture = get_object_or_404(FactureVente, pk=pk)
    if request.method == 'POST' and facture.statut not in ('PAYEE', 'ANNULEE'):
        facture.statut = 'PAYEE'
        facture.save()
        messages.success(request, f'Facture vente {facture.reference} marquée comme payée.')
    return redirect('comptable')


@role_required('comptable')
def facture_vente_annuler(request, pk):
    """Annule une facture de vente."""
    facture = get_object_or_404(FactureVente, pk=pk)
    if request.method == 'POST' and facture.statut != 'ANNULEE':
        facture.statut = 'ANNULEE'
        facture.save()
        messages.success(request, f'Facture vente {facture.reference} annulée.')
    return redirect('comptable')


@user_passes_test(administrateur_requis)
def parametres_view(request):
    """Page de configuration des paramètres de l'application."""
    instance = ParametreApp.get_instance()
    form = ParametreAppForm(instance=instance)
    if request.method == 'POST':
        form = ParametreAppForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres de l\'application enregistrés avec succès.')
            return redirect('parametres')
    context = {
        'form': form,
        'instance': instance,
    }
    return render(request, 'parametres.html', context)


@login_required
def profil_view(request):
    """Page de profil utilisateur : permet de modifier sa photo et ses coordonnées."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    form = UserProfileForm(instance=profile)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            try:
                form.save()
            except Exception:
                logger.exception("Échec de l'enregistrement de la photo de profil.")
                messages.error(
                    request,
                    "Impossible d'enregistrer la photo. Vérifiez le stockage média du service Render.",
                )
            else:
                messages.success(request, 'Profil mis à jour avec succès.')
                return redirect('profil')
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'profil.html', context)


@login_required
@user_passes_test(administrateur_requis)
def utilisateurs_view(request):
    """Liste et création des comptes utilisateurs."""
    form = UtilisateurForm()
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            utilisateur = form.save()
            appliquer_role(utilisateur, form.cleaned_data['role'])
            messages.success(request, 'Utilisateur créé avec succès.')
            return redirect('utilisateurs')

    recherche = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()
    utilisateurs = User.objects.order_by('username')
    if recherche:
        utilisateurs = utilisateurs.filter(
            Q(username__icontains=recherche) | Q(first_name__icontains=recherche) |
            Q(last_name__icontains=recherche) | Q(email__icontains=recherche)
        )
    if role:
        utilisateurs = utilisateurs.filter(groups__name=role).distinct()
    return render(request, 'utilisateurs.html', {
        'form': form,
        'utilisateurs': utilisateurs,
        'recherche': recherche,
        'role_filtre': role,
    })


@login_required
@user_passes_test(administrateur_requis)
def utilisateur_edit(request, pk):
    """Modifie les informations d'un compte sans changer son mot de passe."""
    utilisateur = get_object_or_404(User, pk=pk)
    form = UtilisateurModificationForm(request.POST or None, instance=utilisateur)
    if request.method == 'POST' and form.is_valid():
        utilisateur = form.save()
        appliquer_role(utilisateur, form.cleaned_data['role'])
        messages.success(request, 'Utilisateur mis à jour avec succès.')
        return redirect('utilisateurs')
    return render(request, 'utilisateur_edit.html', {'form': form, 'utilisateur': utilisateur})


@login_required
@user_passes_test(administrateur_requis)
def utilisateur_toggle_actif(request, pk):
    """Active ou désactive un compte, sans permettre à l'administrateur de se bloquer."""
    utilisateur = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if utilisateur == request.user:
            messages.error(request, 'Vous ne pouvez pas désactiver votre propre compte.')
        else:
            utilisateur.is_active = not utilisateur.is_active
            utilisateur.save(update_fields=['is_active'])
            statut = 'activé' if utilisateur.is_active else 'désactivé'
            messages.success(request, f'Utilisateur {utilisateur.username} {statut}.')
    return redirect('utilisateurs')


@login_required
@user_passes_test(administrateur_requis)
def utilisateur_delete(request, pk):
    """Supprime un compte, sauf le compte courant et les comptes superutilisateur."""
    utilisateur = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if utilisateur == request.user:
            messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        elif utilisateur.is_superuser:
            messages.error(request, 'Un compte superutilisateur ne peut pas être supprimé ici.')
        else:
            nom = utilisateur.username
            utilisateur.delete()
            messages.success(request, f'Utilisateur {nom} supprimé.')
    return redirect('utilisateurs')


# ==========================================
# VUES SUIVI DE PRODUIT ET GÉOLOCALISATION GPS
# ==========================================

@login_required
def suivi_list_view(request):
    """Liste et tableau de bord des suivis d'expéditions du fournisseur au client."""
    query = request.GET.get('q', '').strip()
    statut_filtre = request.GET.get('statut', '').strip()

    suivis = SuiviExpedition.objects.select_related(
        'produit', 'fournisseur', 'entrepot', 'client', 'commande_achat', 'commande_vente'
    ).all()

    if query:
        suivis = suivis.filter(
            Q(numero_suivi__icontains=query) |
            Q(produit__designation__icontains=query) |
            Q(fournisseur__nom__icontains=query) |
            Q(client__nom__icontains=query) |
            Q(transporteur__icontains=query) |
            Q(immatriculation_vehicule__icontains=query)
        )

    if statut_filtre:
        suivis = suivis.filter(statut=statut_filtre)

    # Statistiques
    all_suivis = SuiviExpedition.objects.all()
    stats = {
        'total': all_suivis.count(),
        'fournisseur': all_suivis.filter(statut='1_FOURNISSEUR').count(),
        'transit_entrepot': all_suivis.filter(statut='2_TRANSIT_ENTREPOT').count(),
        'entrepot': all_suivis.filter(statut='3_ENTREPOT').count(),
        'transit_client': all_suivis.filter(statut='4_TRANSIT_CLIENT').count(),
        'livre': all_suivis.filter(statut='5_LIVRE').count(),
    }

    return render(request, 'suivi_list.html', {
        'suivis': suivis,
        'query': query,
        'statut_filtre': statut_filtre,
        'stats': stats,
        'statut_choices': SuiviExpedition.STATUT_CHOICES,
    })


@login_required
def suivi_detail_view(request, pk):
    """Vue détaillée d'un suivi avec carte Leaflet.js interactive et simulation GPS."""
    suivi = get_object_or_404(
        SuiviExpedition.objects.select_related(
            'produit', 'fournisseur', 'entrepot', 'client', 'commande_achat', 'commande_vente'
        ).prefetch_related('etapes', 'historique_positions'),
        pk=pk
    )

    form_position = MiseAJourPositionGPSForm(instance=suivi)

    if request.method == 'POST':
        form_position = MiseAJourPositionGPSForm(request.POST, instance=suivi)
        if form_position.is_valid():
            ancien_statut = suivi.statut
            updated_suivi = form_position.save()

            # Enregistrer dans l'historique GPS
            PositionGPSHistorique.objects.create(
                expedition=updated_suivi,
                latitude=updated_suivi.lat_actuelle,
                longitude=updated_suivi.lng_actuelle,
                vitesse=updated_suivi.vitesse_kmh
            )

            # Si le statut a changé, ajouter une étape automatique dans le journal
            if ancien_statut != updated_suivi.statut:
                libelle_statut = dict(SuiviExpedition.STATUT_CHOICES).get(updated_suivi.statut, updated_suivi.statut)
                EtapeSuivi.objects.create(
                    expedition=updated_suivi,
                    code_etape=updated_suivi.statut,
                    titre=f"Changement d'étape : {libelle_statut}",
                    description=f"Statut mis à jour manuellement par {request.user.username}.",
                    latitude=updated_suivi.lat_actuelle,
                    longitude=updated_suivi.lng_actuelle,
                    est_terminee=True
                )

            messages.success(request, 'Position GPS et statut mis à jour.')
            return redirect('suivi_detail', pk=suivi.pk)

    etapes = suivi.etapes.all()
    historique_positions = suivi.historique_positions.all()[:50]

    return render(request, 'suivi_detail.html', {
        'suivi': suivi,
        'form_position': form_position,
        'etapes': etapes,
        'historique_positions': historique_positions,
        'statut_choices': dict(SuiviExpedition.STATUT_CHOICES),
    })


@login_required
def suivi_create_view(request):
    """Créer une nouvelle expédition de produit."""
    if request.method == 'POST':
        form = SuiviExpeditionForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            if not suivi.numero_suivi:
                date_str = timezone.now().strftime('%Y%m%d')
                cnt = SuiviExpedition.objects.count() + 1
                suivi.numero_suivi = f'TRK-{date_str}-{cnt:03d}'
            suivi.date_expedition = timezone.now()
            suivi.save()

            # Création du 1er jalon d'étape
            fournisseur_nom = suivi.fournisseur.nom if suivi.fournisseur else 'Fournisseur'
            EtapeSuivi.objects.create(
                expedition=suivi,
                code_etape='1_FOURNISSEUR',
                titre='Commande enregistrée chez le fournisseur',
                description=f'Prise en charge initiale du produit {suivi.produit.designation} chez {fournisseur_nom}.',
                lieu=fournisseur_nom,
                latitude=suivi.lat_fournisseur,
                longitude=suivi.lng_fournisseur,
                est_terminee=True
            )

            messages.success(request, f'Expédition {suivi.numero_suivi} créée avec succès.')
            return redirect('suivi_detail', pk=suivi.pk)
    else:
        initial_data = {}
        date_str = timezone.now().strftime('%Y%m%d')
        cnt = SuiviExpedition.objects.count() + 1
        initial_data['numero_suivi'] = f'TRK-{date_str}-{cnt:03d}'
        form = SuiviExpeditionForm(initial=initial_data)

    return render(request, 'suivi_form.html', {
        'form': form,
        'titre_page': 'Créer un nouveau suivi d\'expédition',
        'bouton_label': 'Créer l\'expédition',
    })


@login_required
def suivi_edit_view(request, pk):
    """Modifier les détails d'un suivi d'expédition."""
    suivi = get_object_or_404(SuiviExpedition, pk=pk)
    if request.method == 'POST':
        form = SuiviExpeditionForm(request.POST, instance=suivi)
        if form.is_valid():
            form.save()
            messages.success(request, f'Suivi {suivi.numero_suivi} mis à jour.')
            return redirect('suivi_detail', pk=suivi.pk)
    else:
        form = SuiviExpeditionForm(instance=suivi)

    return render(request, 'suivi_form.html', {
        'form': form,
        'suivi': suivi,
        'titre_page': f'Modifier le suivi {suivi.numero_suivi}',
        'bouton_label': 'Enregistrer les modifications',
    })


@login_required
def suivi_delete_view(request, pk):
    """Supprimer un suivi d'expédition."""
    suivi = get_object_or_404(SuiviExpedition, pk=pk)
    if request.method == 'POST':
        num = suivi.numero_suivi
        suivi.delete()
        messages.success(request, f'Suivi {num} supprimé avec succès.')
        return redirect('suivi_list')
    return redirect('suivi_detail', pk=pk)


@login_required
def suivi_update_gps_api(request, pk):
    """API JSON POST pour la mise à jour GPS en temps réel depuis le simulateur ou un tracker."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)

    suivi = get_object_or_404(SuiviExpedition, pk=pk)
    try:
        data = json.loads(request.body)
        lat = float(data.get('lat', suivi.lat_actuelle))
        lng = float(data.get('lng', suivi.lng_actuelle))
        vitesse = float(data.get('vitesse', suivi.vitesse_kmh))
        progression = int(data.get('progression', suivi.progression_pct))
        nouveau_statut = data.get('statut', suivi.statut)

        ancien_statut = suivi.statut
        suivi.lat_actuelle = lat
        suivi.lng_actuelle = lng
        suivi.vitesse_kmh = vitesse
        suivi.progression_pct = min(100, max(0, progression))

        if nouveau_statut in dict(SuiviExpedition.STATUT_CHOICES):
            suivi.statut = nouveau_statut
            if nouveau_statut == '5_LIVRE' and not suivi.date_livraison_effective:
                suivi.date_livraison_effective = timezone.now()

        suivi.save()

        # Enregistrer la position historique
        PositionGPSHistorique.objects.create(
            expedition=suivi,
            latitude=lat,
            longitude=lng,
            vitesse=vitesse
        )

        # Si le statut a évolué, créer un jalon d'étape
        if ancien_statut != suivi.statut:
            libelle = dict(SuiviExpedition.STATUT_CHOICES).get(suivi.statut, suivi.statut)
            EtapeSuivi.objects.create(
                expedition=suivi,
                code_etape=suivi.statut,
                titre=f"Étape atteinte : {libelle}",
                description=f"Le véhicule a franchi l'étape à la position GPS ({lat:.4f}, {lng:.4f})",
                latitude=lat,
                longitude=lng,
                est_terminee=True
            )

        return JsonResponse({
            'status': 'success',
            'numero_suivi': suivi.numero_suivi,
            'lat': suivi.lat_actuelle,
            'lng': suivi.lng_actuelle,
            'vitesse_kmh': suivi.vitesse_kmh,
            'progression_pct': suivi.progression_pct,
            'statut': suivi.statut,
            'statut_display': suivi.get_statut_display(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def suivi_ajouter_etape(request, pk):
    """Ajouter manuellement une étape au journal de suivi."""
    suivi = get_object_or_404(SuiviExpedition, pk=pk)
    if request.method == 'POST':
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        lieu = request.POST.get('lieu', '').strip()
        if titre:
            EtapeSuivi.objects.create(
                expedition=suivi,
                code_etape=suivi.statut,
                titre=titre,
                description=description,
                lieu=lieu,
                latitude=suivi.lat_actuelle,
                longitude=suivi.lng_actuelle,
                est_terminee=True
            )
            messages.success(request, 'Nouvelle étape ajoutée au journal.')
    return redirect('suivi_detail', pk=pk)

