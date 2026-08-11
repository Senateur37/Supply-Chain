# AGENTS.md

## Project overview
This repository is a Django 6 ERP-style supply chain application for products, warehouses, purchases, inventory, sales, accounting, and reporting. The main project package is [Supply_Chainn](Supply_Chainn) and the business logic is split into app modules such as [Produits](Produits), [Entrepots](Entrepots), [Achats](Achats), [Inventaire](Inventaire), [Ventes](Ventes), [Comptable](Comptable), and [apps](apps).

## How to work in this codebase
- Prefer small, targeted changes that fit the existing app structure instead of introducing a new architecture.
- Keep the UI and user messages in French unless the task explicitly requires otherwise.
- Follow the existing Django pattern: function-based views, `@login_required` where appropriate, and templates under [templates](templates).
- When adding or updating forms, keep the Bootstrap-style `form-control` widget classes consistent with [apps/forms.py](apps/forms.py).
- When adding or changing URL routes, update the app-level URL file and the main project router in [Supply_Chainn/urls.py](Supply_Chainn/urls.py).
- When changing models, create or update migrations rather than editing the database manually.

## Important files
- [manage.py](manage.py) — Django entry point.
- [Supply_Chainn/settings.py](Supply_Chainn/settings.py) — project settings, installed apps, database config, templates, media/static paths.
- [Supply_Chainn/urls.py](Supply_Chainn/urls.py) — global URL configuration.
- [apps/views.py](apps/views.py) — most dashboard and page-level views.
- [apps/forms.py](apps/forms.py) — shared form definitions for the UI.
- [templates/base.html](templates/base.html) — shared layout and sidebar.
- [TODO.md](TODO.md) — current project notes and completed tasks.

## Development commands
Run commands from the repository root:
- `python manage.py check`
- `python manage.py migrate`
- `python manage.py test`
- `python manage.py runserver`

## Environment and configuration
- The project uses PostgreSQL by default via the database settings in [Supply_Chainn/settings.py](Supply_Chainn/settings.py).
- Database settings can be overridden with `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
- Static and media files are served from [static](static) and [media](media) respectively.

## Conventions to preserve
- Keep existing naming patterns for models, views, and templates.
- Preserve the current French terminology for modules, labels, and success/error messages.
- Preserve the existing context variables used by the templates when changing views.
- Prefer reusing the existing forms and view patterns for CRUD flows rather than creating entirely new patterns.
