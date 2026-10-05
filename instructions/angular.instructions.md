---
applyTo: "**/*.ts"
---
# Indice Angular conventions (always on)
- Follow the common `angular-conventions` skill.
- Before building new UI, auth, or configuration code, check Indice.Angular (see the `indice-angular` skill) and say what you checked.
- Where an imported skill and an Indice skill disagree, the Indice skill wins.
- Match the Angular version and patterns of the app you are in. Do not migrate modules, templates, or change detection in code you were not asked to change.
- New components, directives, and pipes are standalone and use `input()` / `output()`, built-in control flow (`@if`, `@for`, `@switch`), and OnPush change detection.
- Keep component state in signals. End every manual subscription with `takeUntilDestroyed()` or the `async` pipe.
- Organize code by feature and lazy-load feature routes. Keep `core/` for app-wide infrastructure and shared UI free of feature dependencies and API calls.
- Call backend APIs through the generated API clients. Do not write ad hoc `HttpClient` calls or hand-written DTOs for an API that has a client.
- Values that differ per environment (API URLs, authority, client IDs) come from runtime settings, not `environment.ts` or constants.
- Never put secrets, tokens, or customer data in code, settings files, or logs.
- Route guards, hidden menus, and disabled controls are UX only. The server authorizes, and the UI never computes financial, eligibility, or other regulated results.
- Handle the loading, empty, error, and forbidden states a screen can reach.
