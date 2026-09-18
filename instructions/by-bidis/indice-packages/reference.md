# Indice.Platform integration reference

Supporting reference for the `indice-packages` skill. Read the section for the package you are integrating; do not load the whole file by default. Surface names were captured from the Indice.Platform source at version family 8.49.x; verify against the installed version.

## How every package is consumed

1. `dotnet add package <PackageName>`.
2. Register services with the package `Add...` method.
3. Choose backing stores and providers through options or `Use...` methods.
4. Map endpoints with the package `Map...` method when it exposes APIs.
5. Add UI middleware (`UseMessagesUI`, `UseCasesUI`, `UseRisksUI`, `UseSpaUI`) only through the wrapper package that embeds the built assets.

Registration and mapping are separate. Always call both, for example `AddMessaging` + `MapMessaging`, `AddRiskEndpoints` + `MapRisk`, `AddMediaLibrary` + `MapMediaLibrary`, `AddCaseServer` + `MapCases`, `AddExtendedIdentityServer` + `MapIdentityServer`. Authorization policies for package endpoints are package-owned: use `AddCampaignsManagementPolicy`, `AddCasesAccessPolicies`, `AddMediaLibraryManagementPolicy`, and the identity endpoint policies rather than recreating them.

Package options normally carry a path prefix, schema, scope, claim type, and `ConfigureDbContext`. EF-backed packages default to a named connection string when `ConfigureDbContext` is not supplied.

## API host defaults

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.AddMinimalApiDefaults();
builder.Services.AddGeneralSettings(builder.Configuration);
builder.AddWebServiceDefaults();

var app = builder.Build();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapHealthCheckDefaults();
app.Run();
```

* `AddMinimalApiDefaults` registers localization, CORS, JWT or reference-token auth (`AddApiAuthenticationDefaults`), authorization, endpoints API explorer, JSON converters, ProblemDetails, endpoint validation, general settings, and proxy defaults. It reads authority and API values through `GetAuthority`, `GetAuthorityMetadata`, `GetApiResourceName`, `GetApiSecret`. Do not add custom ProblemDetails or JSON defaults before checking it. Do not remove package-added defaults such as JSON converters without a recorded incompatible wire contract.
* `AddWebServiceDefaults` adds OpenTelemetry, health checks, and HTTP resilience. Optional `OTEL_EXPORTER_OTLP_ENDPOINT` or an Application Insights connection string enables exporters. Do not also call `AddDefaultHealthChecks()`; the package already registers the `self` check and a duplicate fails startup.
* The `indice.minimalapi` template uses `IndiceWebApplicationBuilder.CreateBuilder(args)`, `AddApplicationLocalization`, `AddApplicationCache`, `AddApplicationOpenApi`, `AddWebServiceDefaults`, `AddApplicationServices`, then maps OpenAPI, feature endpoints, and `MapHealthCheckDefaults`. OpenAPI uses `General:Api:ResourceName` for the document name, Swagger UI at `/docs`, and authorization-code PKCE. Use `BuildDefault()` when the host must keep its own protected middleware order; `IndiceWebApplicationBuilder.Build()` applies package middleware that can preempt custom CORS, security headers, and auth ProblemDetails.
* The `indice.restapi.mvc` template adds MVC controllers and Hellang ProblemDetails mapping for `BusinessException`, `NotImplementedException`, `HttpRequestException`, and generic failures.
* An IAM host calls `AddWebServiceDefaults()` only. `AddMinimalApiDefaults` is for API hosts, not identity journeys.
* Proxy settings: `Proxy:Enabled`, `Proxy:KnownNetworks`, `Proxy:KnownProxies`, `Proxy:ForwardLimit`.

Common mistake: skipping `UseAuthentication()` / `UseAuthorization()`, or overriding token behavior without checking `AddApiAuthenticationDefaults`.

## Per-package setup

| Package | Purpose | Key methods | Required configuration |
| --- | --- | --- | --- |
| `Indice.Common` | Utilities, events, serialization, extensions | Use exported types directly | None |
| `Indice.AspNetCore` | Middleware, OpenAPI, security, avatars, reCAPTCHA, translations, SignalR proxy | `AddRecaptcha(configuration)`, `MapRecaptcha()`, `AddSignalRProxy`, `MapSignalRProxy` | Feature-specific |
| `Indice.AspNetCore.Builder` | Host defaults | `AddMinimalApiDefaults`, `AddWebServiceDefaults`, `MapHealthCheckDefaults` | Authority and API values; optional telemetry and proxy keys |
| `Indice.AspNetCore.EmbeddedUI` | Embedded SPA middleware used by UI wrappers | `UseSpaUI` | Prefer the feature UI wrapper packages |
| `Indice.AspNetCore.Authentication.Apple` | Apple OIDC | `AddAppleID(options => ...)` | `TeamId`, `ServiceId`, `PrivateKey`, `PrivateKeyId`; callback `/signin-apple`; on Azure set `WEBSITE_LOAD_USER_PROFILE=1` |
| `Indice.AspNetCore.Authentication.GovGr` | GovGr OAuth/OIDC and KYC | `AddGovGr(...)`, `AddGovGrKyc(...)` | Authority, endpoints, client credentials, scopes; callback `/signin-govgr` |
| `Indice.Services` | Files, email, SMS, push, events, locks | `AddFiles`, `AddFilesAzure`, `AddFilesLocal`, `AddFilesInMemory`, `AddFilesNoop`, `AddEmailService(configuration)`, `AddSmsService(configuration)`, `AddPushNotificationServiceAzure`, `AddEventDispatcherAzure`, `AddEventDispatcherAzureServiceBus`, `AddPlatformEventHandler`, `AddLockManagerAzure`, `AddLockManagerInMemory` | `Email:Provider` (smtp, sparkpost, sendgrid, brevo, azurecommunicationservices, none), `Sms:Provider` (yuboto, vonage, twilio, smsup, apifon, mstat, none; missing throws), `StorageConnection`, `ServiceBusConnection`, managed-identity settings under the connection name |
| `Indice.Extensions.Configuration.Database` | Database-backed configuration provider | `AddDatabase...` overloads; check before use | DB connection |
| `Indice.EntityFrameworkCore` | EF utilities and schema helpers | Query extensions such as `ToResultSetAsync` | None |
| `Indice.Features.Identity.*` | IAM host, Identity UI, Admin UI, sign-in logs | `AddExtendedIdentityServer(configuration, environment, options => ...)`, chained `AddExtendedEndpoints`, `AddDeviceEndpoints`, `AddTotpEndpoints`, `AddDatabaseSettingEndpoints`; `AddIdentityUI(configuration, options => ...)`; `MapIdentityServer()`, `MapMultiFactorAuthentication()`, `MapTotps`, `MapSignInLogs` | `IdentityDb`, `ConfigurationDb`, `OperationalDb`; `IdentityServer:SigningPfxFile` and `IdentityServer:SigningPfxPass` outside Development; optional `IdentityServer:DuendeLicenseKey` (net9+), `IdentityServer:Features`, `IdentityServer:RateLimiter` |
| `Indice.Features.ActivityLogs` | Activity log publisher, queue, persistence, enrichers, filters, GeoIP, platform-event listener | `AddActivityLogs(configuration, o => o.Enable = true).UseEntityFrameworkCoreStore((sp, db) => ...)`, `ListenToPlatformEvents`, `AddEnricher<T>` | `ActivityLogOptions`; EF store DbContext when persisting |
| `Indice.Features.Messages.*` | Campaigns, messages, inbox, templates, workers, UI | `AddMessaging(options => ...)`, `AddMessageManagement`, `AddMessageInbox`, `MapMessaging`, `MapMessagingInbox`, `MapMessagingManagement`; options `UseFilesLocal`, `UseFilesAzure`, `UseEventDispatcherAzure`, `UseEventDispatcherAzureServiceBus`, `UseIdentityContactResolver`, `UseContactResolver<T>`, `UseMultiTenancy`; workers `AddMessageJobs`, `ConfigureMessageQueue`, `AddMessageFunctions`; UI `UseMessagesUI` | `MessagesDb` or `ConfigureDbContext`; file, event, and contact provider settings |
| `Indice.Features.Cases.*` | Case management, back-office APIs, workflow integration, UI | `AddCasesCore`, `AddCasesManagement`, `AddCaseServer`, `MapCases`, `AddCasesWorkflow`, `UseCasesWorkflow`, `UseContactProviderIdentity`, `AddCaseAuthorizationService<T>`, `UseCasesUI` | `CasesDb`; authority via `GetAuthority`; `ClientId`, `ClientSecret`, `ServerLoopbackUri`; schema, scope, claim-type options |
| `Indice.Features.Risk.*` | Risk rule engine, API, UI | `AddRiskEngine`, `RiskEngineBuilder.AddRule`, `AddRiskEndpoints`, `MapRisk`, `UseRisksUI` | `RiskEngineOptions`; `RiskApiOptions.ApiPrefix`, `ApiScope`, `AuthenticationScheme`; rule options and validators |
| `Indice.Features.Media.AspNetCore` | Media library API, folders, files, settings, cleanup jobs | `AddMediaLibrary(o => o.UseFilesLocal())` or `UseFilesAzure()`, `MapMediaLibrary()` | `MediaLibraryDbConnection`; `MediaApiOptions.PathPrefix`, `AuthenticationScheme`, `AcceptableFileExtensions`, `Scope`, `MaxFileSize`, `UseSoftDelete` |
| `Indice.Features.Multitenancy.*` | Tenant resolution in ASP.NET and worker hosts | `AddMultiTenancy`, `AddMultiTenancy<TTenant>`, `UseMultiTenancy`, worker `UseMultiTenancy` | Tenant source and resolution options; register before tenant-dependent services |
| `Indice.Features.GeoIP` | IP geolocation | `AddGeoIPResolver` (used by ActivityLogs and Risk) | GeoIP database |
| `Indice.Features.GovGr`, `Indice.Features.FtpServer` | Greek government clients; FTP server | Inspect README and source before use | Endpoints, credentials, storage |
| `Indice.Hosting` | Worker scheduling, locks, relational stores | `AddWorkerHost`, `AddWorkPublisher`, `UseLockManager...`, `UseStoreRelational`, `UseScheduledTaskStore...` via `WorkerHostConfiguration` and `WorkPublisherConfiguration` | Store, schedule, and lock options |
| `Indice.Functions.Builder` | Azure Functions (isolated) defaults | `ConfigureFunctionsWebApplicationDefaults`, `AddWorkerServiceDefaults`, `AddFunctionHealthCheck` | Telemetry and health options; local dev expects Azurite-compatible `AzureWebJobsStorage` |

## Options and contracts

| Name | Used by | Purpose |
| --- | --- | --- |
| `ExtendedIdentityServerOptions`, `ExtendedEndpointOptions`, `IdentityUIOptions` | Identity packages | Host seed, store, session, endpoint prefix and scope, UI toggles, links, events, theming. Prefer `IdentityUIOptions.Events` over editing pages. |
| `MessageEndpointOptions`, `MessageManagementOptions`, `MessageInboxOptions` | Messaging | Path, DB, schema, scope, files, analytics |
| `CasesOptions`, `CaseServerOptions` | Cases | DB, schema, scope, claims, workflow behavior |
| `RiskEngineOptions`, `RiskApiOptions` | Risk | Score mapping, API auth |
| `MediaApiOptions` | Media | Path, DB, file limits, soft delete, scope, `UseFilesLocal/Azure` |
| `Tenant`, `TenantBuilder<TTenant>`, `ITenantAccessor<TTenant>` | Multitenancy | Tenant model and resolution |
| `IFileService`, `IEmailService`, `ISmsService`, `IPushNotificationService`, `IEventDispatcher`, `ILockManager` | `Indice.Services` | Infrastructure contracts; register via package extensions |
| `IActivityLogPublisher`, `IActivityLogStore`, `IActivityLogEntryEnricher` | ActivityLogs | Publish, persist, enrich |

## Extension points

| Extension point | How |
| --- | --- |
| Identity UI events and labels | `IdentityUIOptions.Events` (for example `OnUserRegistering`); `AddIdentityUILabelDescriber<TDescriber>` |
| Identity pages and assets | Override Razor pages and static assets at the documented host paths only |
| Messaging file store and contact resolver | `UseFilesLocal/Azure`; `UseIdentityContactResolver` or `UseContactResolver<T>` implementing `IContactResolver` |
| Cases authorization and events | `AddCaseAuthorizationService<T>` implementing `ICaseAuthorizationService`; `AddCaseEventHandler<TEvent, THandler>` where the event implements `ICaseEvent` |
| Activity log enrichers | `AddEnricher<TEnricher>` implementing `IActivityLogEntryEnricher` |
| Risk rules | Derive `RiskRule`, `RuleOptions`, `RuleOptionsValidator`; register with `RiskEngineBuilder.AddRule`; configure JSON polymorphism per the Risk README |
| Media file store | `MediaApiOptions.UseFilesLocal/Azure` |
| Multitenancy tenant type | `AddMultiTenancy<TTenant>` with a `Tenant` subclass |

Do not consume: the private `*.App` Angular projects, endpoint handler classes under `Endpoints/*Handlers.cs`, package EF DbContexts and entities (except approved migrations or host setup), or no-op fallback services except through package options.

## Workflows

**Add messaging to an API.** See the `indice-messaging` skill for the host and worker boundary, IAM contract, and template model. Install `Indice.Features.Messages.AspNetCore` and companions. Configure `MessagesDb` or `ConfigureDbContext`. Register `AddMessaging(options => ...)` and select file, event, contact, and multitenancy providers with `Use...`. Map `MapMessaging()`, or only `MapMessagingInbox()` / `MapMessagingManagement()`. Add `Indice.Features.Messages.UI` and `UseMessagesUI` only when the management UI is needed. The messaging template registers avatars, Media Library, Messaging, then `AddWebServiceDefaults`, and resolves contacts through IAM with configured authority and client credentials. Worker templates use isolated Azure Functions with `AddMessageFunctions` plus file, event, push, email, SMS, and contact-resolver providers. Mistakes: `AddMessaging` without `MapMessaging`; custom campaign or send endpoints; bypassing the contact resolver.

**Compose an IAM host.** See the `indice-iam` skill for ownership rules. Install the identity packages. Configure `IdentityDb`, `ConfigurationDb`, `OperationalDb`, and the signing certificate outside Development. Register `AddExtendedIdentityServer(...)` and chain `AddExtendedEndpoints`, `AddDeviceEndpoints`, `AddTotpEndpoints`. Register `AddIdentityUI(...)` for pages. Map `MapIdentityServer()` and `MapMultiFactorAuthentication()` when login MFA is required. `MapMultiFactorAuthentication` is login MFA, not product-action step-up. Mistakes: custom user, client, scope, token, MFA, or session stores; skipping the signing certificate; copying UI pages instead of documented overrides.

**Host cases.** See the `indice-cases` skill for the boundary, IAM contract, database keys, and workflow rules. The cases template registers localization, cache, OpenAPI, `AddWebServiceDefaults`, `AddCaseServer`, `AddCasesWorkflow`, then maps `UseCasesWorkflow`, `UseCasesUI`, `MapCases`, OpenAPI, and health. Keep custom authorization in `AddCaseAuthorizationService<T>`.

**Add a risk rule.** Derive `RiskRule`, `RuleOptions`, and `RuleOptionsValidator`; register with `RiskEngineBuilder.AddRule`; configure JSON polymorphism; expose with `AddRiskEndpoints` and `MapRisk` (`POST /risk/events`, `POST /risk`). Mistakes: scores outside `RiskRule`; skipping options validation; omitting polymorphism.

**Add files or media.** For generic storage, register a provider with `AddFiles...` and inject `IFileService`. For a media API, configure `MediaLibraryDbConnection`, register `AddMediaLibrary(o => o.UseFilesLocal())` or `UseFilesAzure()`, map `MapMediaLibrary()`, and set limits, extensions, scope, and soft delete through `MediaApiOptions`. Mistakes: direct `BlobServiceClient` wrappers; Azure storage without `StorageConnection` or managed identity; bypassing size and extension options.

## Configuration keys

| Key | Used by | Notes |
| --- | --- | --- |
| `IdentityDb`, `ConfigurationDb`, `OperationalDb` | Identity host | Required unless DbContext delegates are supplied |
| `IdentityServer:SigningPfxFile`, `IdentityServer:SigningPfxPass` | Identity signing | Required outside Development; never checked in |
| `IdentityServer:DuendeLicenseKey` | Duende (net9+) | Optional |
| `MessagesDb`, `CasesDb`, `MediaLibraryDbConnection` | Messaging, Cases, Media | Required unless overridden |
| `StorageConnection`, `ServiceBusConnection` | `Indice.Services` | Azure file, event, and lock defaults |
| `Email:Provider`, `Sms:Provider` | `Indice.Services` | Provider selection; missing SMS provider throws |
| `Proxy:*` | ASP.NET builder | Forwarded headers |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Service defaults | Telemetry exporter |
| `General:Api:ResourceName` | OpenAPI template extension | Document name |

All secrets, connection strings, certificates, and provider keys come from secure configuration, never source.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Endpoint returns 404 | `Add...` called but `Map...` not called | Call the matching mapper |
| Auth fails | Wrong authority, API resource, scope, secret, or scheme | Use package options and builder defaults |
| UI assets missing | Consumed `*.App` directly or skipped the UI wrapper | Use the wrapper package |
| Database startup fails | Missing package connection string or `ConfigureDbContext` | Supply it |
| SMS provider not found | `Sms:Provider` missing or invalid | Configure a supported value or `none` |
| Apple auth option error | Missing TeamId, ServiceId, PrivateKey, or PrivateKeyId | Configure them |
| Duplicate health check at startup | `AddDefaultHealthChecks` plus `AddWebServiceDefaults` | Remove the separate call |
| Telemetry exporter absent | Exporter not configured | Set the OTLP endpoint or Application Insights connection string |

## Compatibility and risks

* Targets `net8.0;net9.0;net10.0`. Identity has net9+ Duende and pre-net9 IdentityServer4 branches (`#if NET9_0_OR_GREATER`); align target framework and package versions. Templates default to net10.0 except `indice.messaging.workers` (net9.0).
* Angular apps under `src/*App` are private build inputs (Angular 20.x, Node 24 in CI), not npm packages.
* Email and SMS providers send real messages; use noop or test providers in tests and development.
* Identity UI legal markdown and branding assets are placeholders.
* Repository SQL migration scripts (IdentityServer 4 to 7, campaigns to messages) are version-specific and potentially destructive; review manually.
* Not every package has a complete setup recipe. When unsure, inspect the package `.csproj`, README, `*Options.cs`, `*FeatureExtensions.cs`, `*EndpointExtensions.cs`, and `*Api.cs` before writing code.

## Where to look in the Indice.Platform source

`README.md` (package catalog), `src/Directory.Build.props` (targets and versions), `pack.ps1` (packed projects), `.github/workflows/build.template.yml` (build and test sequence), and per package: `src/Indice.AspNetCore.Builder/WebApplicationBuilderExtensions.cs`, `src/Indice.AspNetCore.Builder/ServiceDefaultsExtensions.cs`, `src/Indice.Features.Identity.Server/Extensions/*.cs`, `src/Indice.Features.Identity.Server/Mfa/MfaApi.cs`, `src/Indice.Features.Identity.UI/README.md`, `src/Indice.Features.Messages.AspNetCore/Message*Extensions.cs`, `src/Indice.Features.Cases.Core/CasesFeatureExtensions.cs`, `src/Indice.Features.Cases.Server/CaseServerFeatureExtensions.cs`, `src/Indice.Features.Risk.Core/README.md`, `src/Indice.Features.Risk.Server/RiskApi.cs`, `src/Indice.Features.Media.AspNetCore/MediaLibrary*Extensions.cs`, `src/Indice.Services/README.md`, `src/Indice.Services/Extensions/*.cs`, `src/Indice.Features.MultiTenancy.AspNetCore/Configuration/*.cs`. Tests under `test/*.Tests` show the intended usage patterns.

Repository validation: `dotnet restore Indice.Platform.slnx`, `dotnet build Indice.Platform.Ecmascript.slnf --configuration Release`, `dotnet build Indice.Platform.slnf --configuration Release`, `dotnet test Indice.Platform.slnf --configuration Release`, `./pack.ps1`.
