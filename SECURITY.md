# Sécurité

## Variables de production

Définir ces variables dans l'environnement de déploiement, jamais dans le dépôt :

```text
SECRET_KEY=<clé aléatoire longue d'au moins 50 caractères>
DJANGO_DEBUG=False
ALLOWED_HOSTS=supply-chain-tsji.onrender.com
CSRF_TRUSTED_ORIGINS=https://supply-chain-tsji.onrender.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

`SECURE_HSTS_PRELOAD=True` doit être activé uniquement après avoir confirmé que tous les sous-domaines fonctionnent exclusivement en HTTPS.

## Vérification avant déploiement

```bash
python manage.py check --deploy
```

Les avertissements restants doivent être évalués selon le certificat HTTPS et le reverse proxy utilisés par l'hébergeur.

## Règles applicatives

- Les actions de création, modification et suppression utilisent des requêtes `POST` protégées par CSRF.
- Les accès aux modules sont contrôlés côté serveur par rôle Django.
- Les comptes utilisateurs ne peuvent pas supprimer leur propre compte ni un superutilisateur depuis l'interface.
- Les paramètres de l'application et la gestion des comptes sont réservés aux administrateurs.
