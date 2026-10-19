---
name: indice-packages
description: >
  Use before writing custom infrastructure, IAM, messaging, audit/activity logs,
  file storage, email/SMS/push, media, risk, cases, multitenancy, API host
  defaults, EF/query helpers, workers, or other platform plumbing in a .NET
  project: which Indice.* package covers which need, the Add/Use/Map methods to
  call, when to keep custom code, and how to set a package up (see reference.md).
---

# Indice package map

Indice.Platform is a family of NuGet packages for .NET web applications and services: common utilities, ASP.NET Core host defaults, authentication providers, IAM, activity logs, messaging, cases and workflows, risk, multitenancy, media library, GeoIP, GovGr integrations, hosting and worker helpers, Azure Functions helpers, and infrastructure service abstractions.

Consume it as a package platform, not as a source tree to copy from. Install the specific package, register with its `Add...` method, choose stores and providers with its `Use...` methods, and expose endpoints with its `Map...` method.

## Decision rule

Use suitable Indice utilities first. Use custom code when Indice does not fit.

* Check Indice before writing repeated platform plumbing. Search for `Add...`, `Use...`, `Map...`, `...Options`, and service interfaces before writing integration code.
* Use an Indice package where it clearly removes repeated infrastructure code without changing regulated behavior, approved contracts, security boundaries, audit evidence, or module ownership.
* Keep custom code where the behavior is domain-specific, legally material, or not covered by an exact Indice utility. Do not replace approved evidence, audit, idempotency, authorization, or data-model behavior just because a utility exists.
* Prefer local adapters around Indice APIs so module code stays module-first and testable.
* An adopted Indice product may generate and own the artifacts it needs (APIs, EF models, DbContexts, migrations, schema, stores, UI assets, workers, cleanup jobs) inside its own host or schema. Application modules must not build parallel stores for those capabilities. Package and secret rules are in the engineering rules instructions.
* When no package capability is proven, record "no existing Indice capability found" before writing custom code.
* Record every choice as "Indice used because ..." or "Custom used because ...".

## Package map

| Need | Package | Use this | Do not build |
| --- | --- | --- | --- |
| API host defaults: localization, CORS, JWT or reference-token auth, authorization, JSON converters, ProblemDetails, endpoint validation, proxy defaults | `Indice.AspNetCore.Builder` | `builder.AddMinimalApiDefaults()` | Custom auth, CORS, ProblemDetails, or JSON bootstrap |
| Telemetry, health checks, HTTP resilience | `Indice.AspNetCore.Builder` | `AddWebServiceDefaults()`, `MapHealthCheckDefaults()` | Custom health JSON or OpenTelemetry setup |
| API helpers: OpenAPI, security, reCAPTCHA, avatars, SignalR proxy, validation, rate limiting, upload limits, mock auth for tests (`AddMock`, `MockAuthenticationDefaults`) | `Indice.AspNetCore` | Feature-specific `Add...`/`Map...` such as `AddRecaptcha`, `MapRecaptcha`, `AddSignalRProxy`, `MapSignalRProxy` | Production auth shortcuts, implicit permission rules |
| Common primitives, builders, event abstractions, list and result-set types | `Indice.Common` | Exported types directly | Domain rules, regulated state machines, evidence models |
| Bounded EF paging (`ToResultSetAsync`), filtering, sorting, JSON conversions, query helpers | `Indice.EntityFrameworkCore` | Extension methods on queries | Cross-module joins, unbounded or dynamic query exposure |
| File storage, email, SMS, push, event dispatch, distributed locks | `Indice.Services` | `AddFiles`, `AddFilesAzure`, `AddFilesLocal`, `AddEmailService`, `AddSmsService`, `AddPushNotificationServiceAzure`, `AddEventDispatcherAzure`, `AddEventDispatcherAzureServiceBus`, `AddLockManagerAzure`, `AddLockManagerInMemory` | Custom blob wrapper, provider factories, lease managers, queue plumbing |
| Workers, queues, scheduled jobs, relational stores and locks | `Indice.Hosting` | `AddWorkerHost`, `AddWorkPublisher`, `UseLockManager...`, `UseStoreRelational`, `UseScheduledTaskStore...` | Custom scheduler; not a local dev launcher |
| Azure Functions defaults | `Indice.Functions.Builder` | `ConfigureFunctionsWebApplicationDefaults`, `AddWorkerServiceDefaults`, `AddFunctionHealthCheck` | Custom function telemetry and health |
| IAM host, Identity UI, Admin UI, sign-in logs | `Indice.Features.Identity.*` | `AddExtendedIdentityServer`, `AddExtendedEndpoints`, `AddDeviceEndpoints`, `AddTotpEndpoints`, `AddIdentityUI`, `MapIdentityServer`, `MapMultiFactorAuthentication` | Any user, client, scope, token, MFA, or session store. See the `indice-iam` skill. |
| Activity or audit-style platform logs | `Indice.Features.ActivityLogs` | `AddActivityLogs(...).UseEntityFrameworkCoreStore(...)`, `ListenToPlatformEvents`, `AddEnricher<T>` | Custom log queues; not a substitute for regulated domain audit |
| Campaigns, messages, inbox, templates, delivery workers, management UI | `Indice.Features.Messages.*` | `AddMessaging` + `MapMessaging` (or `MapMessagingInbox` / `MapMessagingManagement`), `UseMessagesUI`, worker `AddMessageJobs` | Custom campaign, template, send, or inbox APIs. See the `indice-messaging` skill. |
| Case management, back-office case APIs, workflows, case UI | `Indice.Features.Cases.*` | `AddCaseServer` + `MapCases`, `AddCasesWorkflow`, `UseCasesWorkflow`, `UseCasesUI` | Custom case or workflow engine. See the `indice-cases` skill. |
| Risk rules and scoring API | `Indice.Features.Risk.*` | `AddRiskEngine`, `RiskEngineBuilder.AddRule`, `AddRiskEndpoints`, `MapRisk`, `UseRisksUI` | Custom scoring loops or hardcoded fraud logic |
| Media library: folders, files, settings, storage | `Indice.Features.Media.AspNetCore` | `AddMediaLibrary(o => o.UseFilesAzure())`, `MapMediaLibrary` | Ad hoc blob or file endpoints |
| Tenant resolution and access | `Indice.Features.Multitenancy.*` | `AddMultiTenancy`, `UseMultiTenancy`, `AddMultiTenancy<TTenant>` | Custom tenant accessor or middleware. Compare with an existing tenant model first. |
| Apple and GovGr sign-in | `Indice.AspNetCore.Authentication.Apple`, `Indice.AspNetCore.Authentication.GovGr` | `AddAppleID`, `AddGovGr`, `AddGovGrKyc` | Custom OIDC handlers. GovGr needs approved credentials, scopes, and personal-data handling. |
| Greek government services, GeoIP, FTP server, database-backed configuration | `Indice.Features.GovGr`, `Indice.Features.GeoIP`, `Indice.Features.FtpServer`, `Indice.Extensions.Configuration.Database` | Inspect the package README and source before use; setup is not fully documented | Custom MaxMind or FTP wrappers |
| Certificates, HTTP signing, PSD2 / FAPI | `Indice.Cryptography.*` | Approved certificate parsing, message signing, store integration | Sample keys, certificate-server endpoints, or signature middleware without approved redaction, replay, revocation, rotation, and audit decisions |
| Bank, PSP, eGov KYC, tax-authority integration patterns | `Indice.Banking.*` / `Indice.Integration.*` | Adapter, mapper, consent, journaling, and mock/real separation patterns | Copied provider clients, product codes, fee logic, validation semantics, or realistic personal data. See the `regulated-integrations` skill. |
| Angular UI | `Indice.Angular` (https://github.com/indice-co/Indice.Angular); `Indice.Features.*.UI` wrapper packages | The wrapper NuGet packages that embed built assets | Consuming the private `*.App` Angular projects directly |

## Typically kept custom

Usually domain-specific and small. Do not replace with a generic utility unless an exact match is approved:

* A `Result<T>` outcome type required by the architecture.
* Append-only audit streams with canonical payloads, redaction allow-lists, and hash chains.
* Idempotency stores tied to a specific request contract.
* ProblemDetails mappings whose status codes and validation details are part of an approved API contract.
* Design-time EF `DbContext` factories, schema validation tooling, and local developer scripts.

## Before implementing shared infrastructure

1. Identify the requested capability and find its row above.
2. Check the installed package version in `Directory.Packages.props` and the package README, XML docs, `*Options.cs`, `*FeatureExtensions.cs`, `*EndpointExtensions.cs`, or `*Api.cs` for the exact surface. Never invent setup commands, config keys, or environment variables.
3. Pair service registration with endpoint or middleware mapping when the package exposes both.
4. Choose stores and providers through package options, and use package-defined policies and scopes rather than hardcoding endpoint auth.
5. For certificate or HTTP-signature work, record decisions on key material, storage, authorization, redaction, replay, revocation, rotation, and audit first. For external regulated integrations, require the adapter boundary, idempotency model, ledger and evidence interaction, authorization, scoping, callback and retry behavior, error mapping, data minimization, retention, secret management, mock/real separation, and verification plan first.
6. Read `reference.md` in this folder for setup recipes, configuration keys, extension points, and troubleshooting.

## Before replacing existing custom code with an Indice package

State, in the task or design: which custom utility is replaced; which package and feature is approved; dependency and transitive impact; behavior parity expectations; affected modules; migration, audit, authorization, and test evidence expectations.

## Review line

Add one line to every implementation review:

```text
Indice utility review: <package used / custom chosen> because <reason>.
```

## Discovering packages and templates

```powershell
dotnet package search Indice --format json --take 80
dotnet package search Indice.AspNetCore --exact-match --format json --take 5
dotnet new install Indice.DotNet.Templates.Web
dotnet new list indice
```

Templates: `indice.minimalapi`, `indice.restapi.mvc`, `indice.identity.pages`, `indice.cases`, `indice.messaging`, `indice.messaging.workers`, `indice.messaging.solution`, `indice.workers`, `indice.functions`. Generate into a scratch location and port the smallest useful wiring into an existing host. Never run generation over existing source, and never copy sample connection strings, authority URLs, scopes, client IDs, secrets, PFX paths, legal markdown, or provider keys.

## Read deeper

* `reference.md` in this folder: setup recipes, configuration keys, options, extension points, workflows, troubleshooting.
* https://github.com/indice-co/Indice.Platform
