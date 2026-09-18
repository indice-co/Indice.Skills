---
name: angular-architecture
description: >
  Use when creating or restructuring an Angular application or its ASP.NET
  Core UI host: app shell and routing, runtime configuration and injection
  tokens, OIDC auth wiring, interceptors and guards, generated API clients,
  localization, build and project files, the thin host that serves the app,
  and the test stack. For screen design and component choice use the
  angular-ux skill.
---

# Angular application architecture

Reference web projects are architecture and implementation-style sources only. Take the shape, never the values: no roles, scopes, claims, client IDs, endpoint values, legal copy, feature taxonomy, or provider settings come from a reference.

## Solution shape

* A core or shared .NET layer with generated service clients and API-facing abstractions.
* Separate API hosts for the public-facing and management-facing surfaces.
* Separate Angular applications for the public portal and the management UI.
* Separate thin ASP.NET Core UI host projects that serve each Angular app.
* Worker projects for background and event-driven integrations.

Keep Angular apps and their UI hosts separate whenever the UI is more than a static asset. The host owns runtime configuration, static file serving, SPA fallback, optional reverse proxying, health checks, and environment-specific endpoint injection.

## App shell

* Standalone bootstrap: `bootstrapApplication(AppComponent, appConfig)`.
* `app.config.ts` owns providers: router, HTTP interceptors, i18n, progress bar, animations, runtime settings, and generated API service tokens.
* `app.routes.ts` owns route structure: auth callback and silent-renew routes first, then a guarded root route with child feature routes.
* `core/` for auth, layout, interceptors, app settings, logging, and API base tokens. Generated TypeScript clients live under `core/services/` beside their `.nswag` inputs.
* `shared-ui/` for reusable UI controls that represent an actual repeated interaction.
* `features/` for vertical feature screens, each with its pages and nested subflows. Keep feature-specific widgets in their feature until reuse is proven.

The app shell hosts header, side navigation, footer, progress indicator, toast container, and modal or banner root. Folder rules and screen patterns are in the `angular-ux` skill.

## Runtime configuration

Environment-sensitive values are runtime settings, never compile-time constants or checked-in environment secrets.

* The UI host exposes `/app-settings.manifest.json` with `Cache-Control: no-store`. A manifest file ships as an asset for local development only.
* The app reads settings at startup and maps each value into an explicit injection token: API base URLs, document, messaging, and workflow service URLs, culture, telemetry, map or provider tokens, and auth settings.
* An optional template mode reads values from `app-root` attributes and removes them from the DOM.
* Missing required settings warn, and throw in development.
* Never commit real runtime keys, client secrets, endpoint values, or production identifiers.

## Auth wiring

* OIDC through `oidc-client-ts`, with settings from runtime configuration.
* One auth service wraps `UserManager`, token state, redirects, silent renew, sign-out callback, profile helpers, and locale fallback.
* Auth callback and silent-renew callback are real routes.
* An HTTP interceptor attaches the bearer token to API calls; a locale interceptor adds the user or app locale.
* A root auth guard redirects unauthenticated users; feature guards check route `data.roles`; navigation uses roles to show or hide groups.

Guards and menu visibility are UX helpers only. Server-side authorization is mandatory. Keep client auth plumbing small and centralized. Client IDs, scopes, redirect URIs, roles, and claims come from the approved IAM contract (see the `indice-iam` skill).

## Generated API clients

* Generate TypeScript clients from approved OpenAPI contracts with NSwag; keep the `.nswag` file beside the output.
* Generated clients expose typed models, enums, ProblemDetails and validation error parsing, and a per-client base URL injection token.
* Hand-written services and components consume generated clients. No ad hoc HTTP calls.
* Wrap a generated client in an application-facing service when the UI needs composition, caching, mapping, retries, or user-friendly errors.
* Expect several API boundaries (management API, document, messaging, workflow, public or CMS APIs) each with its own client and token. Never expose generated models as durable domain contracts.

## Styling and localization

* Tailwind configured with design tokens, functional colour aliases, custom fonts, forms and typography plugins, and safelisted dynamic classes. Keep design tokens and tenant or brand variables separate from business behaviour.
* Global SCSS assets plus component-level styles.
* Transloco configured centrally with available languages, default language, runtime re-rendering, and locale mapping. Locale comes from runtime settings with user-profile fallback and is sent through the interceptor.
* Never hardcode regulated or legal copy in components. It comes from server or configuration.

## UI host

A small ASP.NET Core web host that:

* adds service defaults and maps health checks;
* serves default and static files with SPA fallback to `index.html`;
* exposes runtime app settings as JSON with no-store cache headers;
* optionally proxies API calls through YARP, passing selected auth headers, only when the approved deployment shape includes a proxy;
* resolves required endpoints through configuration extension methods and fails closed when any is missing.

Keep it thin and configuration-driven.

## Build and project files

* Each Angular app owns its `package.json`, `angular.json`, TypeScript config, Tailwind config, and project file. Keep build scripts local to the app.
* The ASP.NET host references the Angular project through an `.esproj` project reference with `ReferenceOutputAssembly=false`.
* Build configurations may select environment files for dev, stage, or prod-like builds, but runtime host settings remain the deployment source of truth. Prefer few checked-in environment variants.
* Local development uses the ASP.NET HTTPS certificate bootstrap and SPA proxy settings.

## Testing

* Pick one Angular test stack per app (Karma/Jasmine or Jest with testing-library) and keep it consistent.
* For regulated flows, cover loading, empty, error, forbidden, success, auth-required, and role-visible states where technically possible.
* Backend integration tests use containerized dependencies.
* Test data is synthetic and sanitized.

## Reliability bar

Simplicity plus completeness: small explicit wiring, complete required configuration, and no hidden runtime assumptions.
