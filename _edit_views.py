p = 'apps/views.py'
s = open(p, encoding='utf-8').read()

# Fournisseur edit/delete
fournisseur_block = '''
@login_required
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


@login_required
def fournisseur_delete(request, pk):
    """Supprime un fournisseur."""
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, 'Fournisseur supprimé avec succès.')
    return redirect('achats')


@login_required
def entrepots_view(request):
'''

anchor = '@login_required\ndef entrepots_view(request):'
if fournisseur_block not in s:
    s = s.replace(anchor, fournisseur_block, 1)

# Client edit/delete - insert before comptable_view
client_block = '''@login_required
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


@login_required
def client_delete(request, pk):
    """Supprime un client."""
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, 'Client supprimé avec succès.')
    return redirect('ventes')


@login_required
def comptable_view(request):
'''

anchor2 = '@login_required\ndef comptable_view(request):'
if client_block not in s:
    s = s.replace(anchor2, client_block, 1)

open(p, 'w', encoding='utf-8').write(s)
print('done')
