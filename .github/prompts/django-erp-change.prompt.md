---
description: "Implement or adjust a feature in this Django ERP project while following the repository conventions"
name: "Django ERP change"
argument-hint: "Feature or change request"
agent: "agent"
---

Implement the requested change in this Django ERP repository.

Requirements:
- Read [AGENTS.md](../../AGENTS.md) and the relevant app files before making changes.
- Prefer small, targeted edits that fit the existing Django structure.
- Keep the UI and user-facing messages in French unless the task explicitly asks otherwise.
- Follow the existing patterns for views, URLs, forms, templates, and migrations in the relevant app.
- Update the app-level URL file and the main router in [Supply_Chainn/urls.py](../../Supply_Chainn/urls.py) when routes change.
- When models change, create or update migrations instead of editing the database manually.
- Preserve existing template context variables and Bootstrap-style form classes used in [apps/forms.py](../../apps/forms.py).

When you respond:
1. Briefly summarize the implemented change.
2. List the files that were updated.
3. Mention any validation or follow-up steps that should be run.

If the request is ambiguous, ask the minimum clarifying questions before making changes.
