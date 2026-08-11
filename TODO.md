# TODO - Actions Modifier / Supprimer + Palette de couleurs

## Tâches — Actions Modifier / Supprimer
- [x] 1. Ajouter les actions Modifier / Supprimer dans `templates/produits.html`
- [x] 2. Ajouter les actions Modifier / Supprimer dans `templates/entrepots.html`
- [x] 3. Ajouter les actions Modifier / Supprimer dans `templates/achats.html` (fournisseurs)
- [x] 4. Ajouter les actions Modifier / Supprimer dans `templates/ventes.html` (clients)

## Tâches — Palette de couleurs / Thème
- [x] 5. Ajouter les champs `couleur_principale` et `couleur_accent` au modèle `ParametreApp`
- [x] 6. Ajouter les champs couleur au formulaire `ParametreAppForm`
- [x] 7. Créer la migration `apps.0003_parametreapp_couleurs` et l'appliquer
- [x] 8. Injecter les variables CSS dynamiques (couleurs) dans `templates/base.html`
- [x] 9. Ajouter la section palette de couleurs dans `templates/parametres.html`
- [x] 10. Ajouter les styles (palette, color-picker) dans `static/css/app.css`
- [x] 11. Tester (`python manage.py migrate` + `python manage.py check` → aucune erreur)
