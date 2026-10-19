---
name: indice-iam
description: >
  Use when a task touches identity, authentication, authorization, login,
  registration, external providers, users, clients, scopes, tokens, sessions,
  MFA, TOTP, step-up, devices, Identity UI, Admin UI, sign-in logs, activity
  logs, or IAM databases in a project that hosts Indice IAM. Defines what
  Indice IAM owns, the package surface to compose instead of rewriting, host
  composition, security contracts, and the database boundary.
---

# Indice IAM

## Product shape

Indice IAM is a deployed, .NET-native IAM product, not a SaaS dependency and not a set of primitives for application modules to reimplement. It is delivered as composable libraries hosted in your own environment:

* ASP.NET Identity for users.
* Duende IdentityServer for OIDC/OAuth2.
* `Indice.Features.Identity.Core`, `Server`, `SignInLogs`, `UI`, and `AdminUI`, plus ActivityLogs / platform event audit integration where the installed package set exposes it.
* Your own databases, DNS, TLS, operations, key material, and deployment topology.

A dedicated identity host project runs the product instance. Application modules consume validated identity context only.

## Workflow when IAM appears in a task

1. Check `Directory.Packages.props` for the installed `Indice.Features.Identity.*` versions.
2. Inspect the installed package README and XML docs for that exact version when a capability is used or questioned.
3. Search for an Indice-owned API or extension point before writing any identity code.
4. If Indice owns the capability, compose or configure it in the identity host.
5. If no Indice capability is proven, document the gap and fail closed. Do not invent an application-owned substitute.

Surface names in this skill were last checked against `Indice.Features.Identity.*` 8.57.0 XML docs and assemblies. Re-verify against the installed version and record the reviewed version before relying on changed behaviour. Product decks and template READMEs are leads, not sources of truth; where they disagree with the package (for example `LatestTermsReleaseDate`, `urn:indice:totp`, `BlockLogin`, or `MfaPolicy` values `Encouraged`/`Prohibited`), the package wins.

## Ownership boundary

Indice IAM owns:

* users, credentials, passwords, profile verification, and identity lifecycle;
* authentication, registration, login, logout, external providers, recovery, and account flows;
* MFA methods, TOTP secrets, device trust, trusted browsers, lockout, suspicious-login guards, and the identity validation pipeline;
* sessions, single-active-session policy, token issuance, signing, revocation, custom grants, and consent screens;
* OIDC/OAuth2 clients, API resources, scopes, identity resources, and service applications;
* Identity UI, Admin UI, page assets, localization, runtime settings, generated files, provider-owned EF models, DbContexts, migrations, schemas, stores, cleanup jobs, and compatibility artifacts;
* sign-in logs and identity activity logs.

The application owns: product permissions and business-action authorization; tenant scoping; business module state and evidence; audit evidence for its own product decisions; and regulated business gates.

| Forbidden application-owned duplicate | Owner |
| --- | --- |
| Users, profiles, passwords, password history, recovery codes, profile verification | ASP.NET Identity / Indice IAM |
| External identities and provider account links | ASP.NET Identity / Indice IAM |
| OIDC/OAuth clients and client secrets | Duende configuration store / Indice IAM |
| Identity resources, API resources, API scopes | Duende configuration store / Indice IAM |
| Grants, device codes, refresh-token state, consent, server-side sessions, token revocation state | Duende operational store / Indice IAM |
| MFA methods, TOTP secrets, trusted devices and browsers, suspicious-login guards | Indice IAM |
| Sign-in logs and identity activity logs | Indice SignInLogs / ActivityLogs |
| Admin UI writes and identity lifecycle administration | Indice IAM Admin UI |

Allowed pattern: the identity host composes Indice-owned capabilities from approved decisions; the application API and modules consume validated identity context (claims, scopes, roles, policies) and enforce product authorization. They never host identity persistence, token issuance, client/resource/scope administration, sign-in evidence, MFA or device state, or IAM lifecycle writes.

## Capability check

Before implementing any IAM behaviour, check whether Indice already owns it.

| Capability | Indice-owned surface |
| --- | --- |
| Identity host composition | `AddExtendedIdentityServer(...)` |
| Identity UI composition | `AddIdentityUI(...)` |
| Extended endpoints | `AddExtendedEndpoints(...)` where the installed package exposes the endpoint group |
| Runtime IAM settings | `AddDatabaseSettingEndpoints(...)` / AppSettings handlers |
| MFA login endpoints | `MfaApi.MapMultiFactorAuthentication(...)` |
| Device features | `AddDeviceEndpoints(...)`, `DeviceOptions` |
| Authenticator-app MFA | `AuthenticatorAppAuthenticationMethod` and its validation models and assets |
| SMS / Viber / email / trusted-device MFA | `SmsAuthenticationMethod`, `ViberAuthenticationMethod`, `EmailAuthenticationMethod`, `TrustedDeviceAuthenticationMethod` |
| FIDO2 / WebAuthn MFA | `Fido2AuthenticationMethod` where the package version confirms support |
| MFA method abstraction | `IAuthenticationMethodProvider`, `AuthenticationMethodProviderInMemory` |
| TOTP primitives | `TotpOptions`, `TotpOptionsBase`, `TotpServiceFactory` |
| Custom OAuth grants | Extension-grant validators for TOTP, device authentication, delegation, guest, MFA, and OTP-authenticate (`CustomGrantTypes`, `TotpConstants.GrantType`, `OtpAuthenticateExtensionGrantValidator`) |
| Two-factor user policy | `User.TwoFactorPolicy`, `IExtendedUserStore.TwoFactorPolicy`; `MfaPolicy` values `Default`, `Optional`, `Enforced` |
| Sessions | `ExtendedIdentityServerOptions.EnableServerSideSessions`, `EnforceSingleActiveSession` |
| Device limits and trust delay | `ExtendedUserManager.MaxAllowedRegisteredDevices`, `TrustActivationDelay` |
| Action attempt limiting | `AddActionRateLimiter(...)`, `ActionRateLimiterOptions` (`Enabled`, `MaxAttempts`, `Window`) |
| Password and registration validators | `AddNonCommonPasswordValidator()`, `AddEmailDomainBlacklistValidator(...)` |
| Impossible travel | `IImpossibleTravelDetector`, `ImpossibleTravelFlowType` (`PromptMfa`, `DenyLogin`) via the sign-in guard |
| Operator-to-client assignment | `ClientUser` (`ExtendedConfigurationDbContext.ClientUsers`) |
| IAM authorization policies | `BasicPolicyNames` / `IdentityEndpoints.Policies` (for example `BeAdmin`, `BeUsersReader`) |
| Post-login validation pipeline | Identity validation activities: terms acceptance, MFA onboarding, email/phone verification, password change |
| MFA UI | `/Mfa`, `/MfaOnboarding`, `/MfaOnboardingAddPhone`, `/MfaOnboardingVerifyPhone`, `/MfaOnboardingAddEmail`, `/MfaOnboardingVerifyEmail` |
| Sign-in evidence | `Indice.Features.Identity.SignInLogs`: event sink, enrichers, filters, retention cleanup, activity-log integration |
| Admin and configuration UI | `Indice.Features.Identity.AdminUI` |

Strongest extension points: `IExtensionGrantValidator`, `IIdentityValidationActivity`, `IEventHandler<TEvent>`, `ISignInLogEntryEnricher`, Razor class library page overrides, and static asset overrides. Do not assume a sign-in-log filter interface exists; 8.57.0 exposes enrichers only.

## Host composition

Use a standalone identity host with a thin `Program.cs` and focused extension classes (localization, SignalR, external providers, OpenAPI, application services, health checks). Do not spread Indice setup across unrelated modules.

The `indice.identity.pages` template is the clean product-host baseline. Install with `dotnet new install Indice.DotNet.Templates.Web`, generate into a scratch location, and port the smallest useful wiring into the existing host. Never overwrite host source files wholesale.

Template composition, as an ordering reference:

1. Use `WebApplication.CreateBuilder(args)` and call `builder.WebHost.AddDatabaseSettings()`.
2. Register localization, SignalR, OpenAPI, cache, Razor Pages, CORS, developer DB exception filter, avatars, email/SMS services, CSP, `AddIdentityUI`, `AddExtendedIdentityServer`, `AddExtendedEndpoints`, `AddDatabaseSettingEndpoints`, `AddDeviceEndpoints`, `AddSignInLogs`, authentication-method providers, data protection and file storage, forwarded headers, ActivityLogs, external providers, then `AddWebServiceDefaults()`.
3. Keep application-specific services in a thin `AddApplicationServices()` extension after product composition.
4. Runtime order: forwarded headers; exception/status pages; production redirect/HSTS or development provider-store setup; static files; cookie policy; routing; `UseRateLimiter`; request localization; response caching; authentication; authorization; IdentityServer; CORS; output cache; Admin UI; OpenAPI; `MapIdentityServer`; avatars; Razor Pages; MFA endpoints and hub; health checks.

Block resource-owner-password grants (including the template's `needs_mfa` password-grant path), seeded all-access users, copied secrets, copied legal copy, provider credentials, sample connection strings, and unconfigured provider stores.

`AddWebServiceDefaults()` and `MapHealthCheckDefaults()` provide package-owned health, telemetry, and HTTP-client defaults. Do not call `AddDefaultHealthChecks()` separately when `AddWebServiceDefaults()` is present. Do not call `AddMinimalApiDefaults()` in the identity host; its JWT, CORS, and ProblemDetails behaviour belongs to API hosts.

Production must fail closed when required configuration is missing.

## Security contract pattern

Keep IAM contract definitions in focused files under a `Security/` folder in the identity host: constants for client IDs, scopes, roles, and custom claims; client definitions; identity resources, API scopes, and API resources; optional seed definitions when approved.

Separate `IdentityResource` (user identity data a client may request), `ApiScope` (a permission a client may request against an API), and `ApiResource` (a protected API with its secret, user claims, and attached scopes).

Rules:

* Define scopes before building clients around them.
* Keep IAM/Admin scopes, UI scopes, service-to-service scopes, and application module scopes separate. Preserve package-owned scopes such as `identity:clients`, `identity:users`, `identity:totp`, `identity:users.devices.secret.read`, and `identity:logs` for IAM surfaces. The package-owned `idsrv-admin-ui` client stays IAM-only.
* Do not register a broad catch-all API scope that satisfies every policy by itself. APIs validate audience and the required scope before endpoint execution, then apply product permissions.
* Expose only approved, minimal claims. Review claim exposure for PII, scoping, and least privilege.
* API resource secrets, redirect URIs, origins, issuer, and hostnames come from configuration or secret stores. Production fails closed on missing, placeholder, malformed, or unregistered values. No wildcard callbacks, shared credentials, or public-client conversions.
* Interactive clients use OAuth 2.0 authorization code with PKCE through Indice IAM, per the security rules in `engineering-rules.instructions.md`. SPA clients (for example via `oidc-client-ts`) attach bearer tokens only to the configured API root. Client-side guards are UX only.
* Delegation, device-authentication, guest, MFA, OTP-authenticate, and device-code grants are each enabled per client only with an approved design covering actor, scope, audit, and abuse limits.

For every client record: purpose and owning surface; human or service actor; grant type and token type; allowed scopes and identity resources; redirect, post-logout, and CORS origins; secret storage and rotation; offline access and refresh-token behaviour; access-token lifetime and reference vs JWT; emitted claims; environment availability. No UI, worker, host, or Admin UI surface is ready until this contract is approved.

## Configuration boundary

IAM configuration includes: identity, configuration, operational, sign-in-log, and activity-log database connections and retention; external providers; data protection storage; SignalR backplane and push settings; email/SMS delivery; MFA, TOTP, WebAuthn, trusted-browser, and device options; password, lockout, terms reacceptance, and validation-pipeline settings; runtime database settings; reCAPTCHA keys; signing credentials; forwarded headers; OpenAPI and Admin UI authority values; CSP and rate-limiter settings.

All of it comes from configuration providers, user secrets, environment variables, or approved secret stores. Never check in fallback LocalDB or provider settings, connection strings, secret values, signing certificate files, or provider credentials. Signing PFX files and passwords come only from an approved secret store.

Runtime settings written through `AddDatabaseSettingEndpoints()` are IAM configuration changes: restrict them to IAM operator scopes, keep their activity-log evidence, and keep any development-only bulk-load of `appsettings.json` unreachable outside development.

## External providers

Provider login is IAM-owned. Before implementing, approve: client id and secret storage; authority or tenant; scopes; token persistence; account-linking behaviour; cancellation and remote-failure behaviour; email verification assumptions; audit requirements; onboarding or registration handoff. Capture the provider contract before code; do not discover behaviour by reflection during implementation.

## Identity UI and assets

UI correctness depends on the whole asset path: layouts, partials, validators, `.resx` resources, page scripts, static assets, package dependencies, Webpack/Tailwind/Sass output, Admin UI stylesheet injection, Razor runtime compilation, static-file middleware, and route prefix.

* The packaged Identity UI layout is `_IdentityLayout`; local `_ViewStart.cshtml` points at it unless a UI change intentionally replaces it.
* Include the template-style `_ViewImports.cshtml` tag-helper imports when adding local Razor pages, or packaged components render without helpers and styles.
* Never add a local `_Layout.cshtml`, `site.css`, admin override stylesheet, or page override by guessing the file name. Compare the generated template or RCL path and use the exact override path. Local pages, layouts, partials, static assets, and CSS win over packaged ones.
* After any UI override, smoke test login, logout, registration if enabled, MFA pages if enabled, static CSS/JS/image loading, and Admin UI if mounted.
* Never copy reference branding, colours, logos, legal text, provider labels, or page copy.

Registration and onboarding journeys are product behaviour, not IAM plumbing. Reference onboarding flows (email capture, provider entry, profile prefill, individual/company branches, phone collection, provider linking) are architecture examples only.

## MFA, devices, TOTP, and hardening

MFA is composed setup, not a page: identity options and user two-factor policy; device and trusted-browser options; MFA and device endpoints; authentication methods; TOTP delivery and validation; SignalR/push or OTP delivery; rate limiting; localized resources; sign-in and activity evidence. Email, SMS, push, Viber, WebAuthn, and trusted devices are security-sensitive product choices: fail closed unless explicitly approved.

* Rate limiting: the template enables `UseRateLimiter()` with `IdentityServer:RateLimiter` rules per endpoint (login, forgot-password, register, TOTP, username-exists, password validation, account updates, confirmations). Carry the template-shaped rules forward with approved values, or leave the feature clearly disabled. Never a no-op policy set.
* reCAPTCHA: v3 keys with optional v2 fallback; CSP must allow `https://www.google.com` and `https://www.gstatic.com` in connect, script, and frame directives. Validation sends the user's IP address to Google, so enabling it also needs privacy approval. Do not enable without approved keys, score threshold, CSP, accessibility handling, and test evidence.
* Terms: `IdentityOptions:SignIn:RequirePostSigninAcceptedTerms`, `TermsLastModifiedDate`, `RequiresTermsAcceptanceActivity`, and markdown under `wwwroot/legal/`. The sample legal markdown is placeholder content; real terms are legal copy and fall under the gated sensitive zones.
* MFA policy: the global policy and per-user `TwoFactorPolicy` are separate levels. Downgrade of authentication method, trusted-browser remember duration and expiration type, and MFA on expired password with a trusted browser are approved policy values, not template defaults.
* Devices: `TrustActivationDelay` and `MaxAllowedRegisteredDevices` are approved values; do not shorten the trust delay or remove the cap without approval.
* Impossible travel: choose `PromptMfa` or `DenyLogin` as an approved decision. Do not build a separate geo or velocity check.
* Validation pipeline: custom `IIdentityValidationActivity` steps that implement regulated gates (for example KYC) follow the gated sensitive zone rules.
* Other hardening areas (password validators, lockout, trusted browser and device policy, CSP) must each be explicitly approved and configured.

## Step-up for sensitive actions

Use the native Indice authenticator-app TOTP grant. `TotpConstants.GrantType.Totp` is the grant type and `TotpGrantValidator` validates token-endpoint requests with `grant_type=totp` plus raw `token`, `code`, and optional `reason`. Consume package constants and request shapes from the installed version; never copy literal aliases or rename the grant.

Risk-based or conditional login MFA and action-specific step-up are cumulative controls; one does not replace the other.

After a native TOTP exchange, an API may accept the token for a protected action only when all hold: normal signature, issuer, audience, expiry, client, and scope validation; `amr` contains `totp`; `auth_time` is within the action-specific maximum age; the token `sub` is the actor executing the command; the required product permission is present; and resource authorization succeeds. Keep the protected-action catalogue and recency policy server-side in the application.

Source of truth: authentication and TOTP verification are Indice IAM; grant identifier and request shape are the installed package; action and recency policy are the application; product permission and resource authorization are the application.

Do not add: application-owned OTP validation, MFA sessions, assurance cookies, claim-injection middleware, a parallel step-up endpoint, a package fork, a custom grant, a secondary assurance store, replay or consumption stores, custom step-up claims, client-supplied MFA or step-up flags, or local-development bypasses (fake assurance providers, synthetic `amr` or `auth_time`, skip switches, skipped-authentication audit events). Local development uses the same catalogue with real Indice TOTP enrollment. If the native token lacks a required proof element, fail closed and report the package or configuration mismatch.

Evidence must prove native TOTP exchange wiring, resulting `amr=totp` and usable `auth_time`, rejection of invalid, missing, stale, or different-subject proof, rejection of missing permission or wrong scope, and absence of any bypass.

## Evidence and audit

IAM-owned events use Indice evidence: sign-in logs (auth-attempt shaped), activity logs (entity-mutation shaped), provider-owned lifecycle evidence, and IAM store records. Keep that distinction. Application audit is for application-owned product decisions only; do not treat sign-in logs as regulated business audit evidence unless an approved design defines the relationship.

Never log or expose raw tokens, OTPs, TOTP values, recovery codes, passwords, provider payloads, secrets, signing material, or unnecessary PII.

Keep `SignInLogOptions.AnonymizePersonalData` enabled unless a privacy-approved design says otherwise. `LogCleanupOptions.RetentionDays` is an approved retention value; do not add a separate cleanup job.

## Database and deployment boundary

| IAM store | Classification |
| --- | --- |
| `IdentityDb` | Indice IAM provider store |
| `ConfigurationDb` | Indice IAM provider store |
| `OperationalDb` | Indice IAM provider store |
| `SignInLogsDb` | Indice IAM provider store |
| `ActivityLogsDb` | Indice IAM provider store |

Schema documentation classifies these as provider-owned evidence, not application schema churn. Application module manifests list only application-owned DbContexts. Exact database count, schemas, retention, and storage tiers are approved configuration decisions, not defaults to copy.

Production readiness validation fails closed on crossed boundaries: the application host rejects IAM provider-store connection strings (`IdentityDb`, `OperationalDb`, `SignInLogsDb`, `ActivityLogsDb`), and the identity host rejects application-store connection strings. `ConfigurationDb` is not name-rejected because both an application configuration module and Duende / Indice IAM may use a configuration-store concept under separate SQL boundaries.

Deployment keeps the two SQL boundaries apart:

* Separate Azure SQL logical servers, elastic pools, and failover groups for application and IAM databases.
* Separate managed identities for API runtime, identity runtime, application migration, and identity migration. Runtime identities get only DML/execute; migration identities hold schema rights only for their own boundary.
* Public database access disabled; private endpoints and private DNS only.
* Regulatory reporting or evidence storage does not live in these pools.
* Deployment shape lives in source-controlled IaC with a policy denying public SQL access. Environment names, SKUs, subnet IDs, DNS zones, failover partners, and principal IDs are deployment parameters, never hardcoded.

## Do-not-copy list

Never copy from reference projects or templates: client IDs, scopes, roles, claims, secrets, passwords, signing material, certificates, authority URLs, connection strings, database names, redirect URIs, CORS origins, provider settings, tenant IDs, endpoint URLs; branding, logos, colours, legal copy, email copy, locale defaults, support links, provider labels, page copy; phone or country rules, tax fields, consent semantics, account-intent or company/individual semantics, communication preferences, onboarding journeys; generated or provider models into public API contracts or durable module records.

## Changing the boundary

Any task touching IAM databases, provider migrations, identity stores, client/resource/scope persistence, MFA or device stores, or sign-in and activity logs must either use Indice-owned artifacts inside the identity host or obtain an explicit, approved design that changes this boundary.

Production hardening, signing and encryption key custody, token lifetime and rotation, real client-secret registration, new user journeys, real notification delivery, external-provider behaviour, MFA and device enablement, step-up, and Admin UI write enablement are each separate, explicitly approved pieces of work. None is implied by hosting the product.

## Review checklist

When IAM or auth appears in a task, answer:

* Which Indice package capability and version was checked?
* Is the behaviour Indice-owned or application-owned?
* If Indice-owned, where is it composed or configured in the identity host?
* If application-owned, what validated identity context does it consume?
* Are clients, scopes, resources, claims, redirects, CORS, secrets, and environments approved?
* Are tenant, PII, audit, and evidence boundaries clear?
* Does missing configuration fail closed?
* Are unauthorized and forbidden paths tested separately?
* Is any gap recorded as remaining work instead of guessed behaviour?
