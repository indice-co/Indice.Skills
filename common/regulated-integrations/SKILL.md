---
name: regulated-integrations
description: >
  Use when designing or implementing integrations with external systems:
  banks and PSD2 / open banking, payment gateways and schedulers, token
  providers, government KYC, registry, or tax-authority services, CRM,
  document, ERP, market-data or listing providers, search indexes, event hubs,
  real-time hubs, notification workers, and the logging around them. Gives
  the host, module, adapter, and worker patterns to carry forward and the
  provider-specific semantics that must never be copied from references.
---

# External and regulated integration patterns

This skill describes **how to build** an integration with an external provider: structure, calls, callbacks, workers and tests. It does not define **what the integration does**. Behaviour that the provider or the business decides (statuses, mappings, flows, timings, copy) is decided for each project. Check the "Domain risk and approval" table before writing any of it.

Use existing projects to learn the shape of an integration only. Never copy their values or behaviour.

## When to ask (what "approved" means)

**Approved** means the user has explicitly confirmed the decision in this conversation, or it is already defined in the work item or its linked design. If neither is true, it is not approved.

* **Ask before** storing, keeping or logging any provider data, tokens, consent or personal data, and before implementing any behaviour listed in the "Domain risk and approval" table that the requirement doesn't define.
* **Ask one specific question**, for example: *"Store the raw KYC provider response? If yes, for how long, and who can read it?"*
* **Implement only what the user confirms.** Do not widen it.
using the user's actual answer, for example: *"Decision: store <data> <how protected>, retained for <period>, readable by <roles>; confirmed by <user> on <date>."* Never fill these values in with defaults.
* **If the user can't decide**, follow the gated sensitive zone rule in `engineering-rules.instructions.md`: deliver only the safe scaffolding, list what is missing, and stop.
* **Do not ask about routine engineering choices**, such as layout, health checks, reading values from configuration, or the module's own persistence. Choose them from existing patterns.

## Boundaries to carry forward

Separate host, module, adapter, generated client, mapper, service, decorator, and worker:

* The host is a composition root. It wires common platform services first, then each integration module through focused `AddX` and `MapX` extension methods.
* Integration modules are explicit, small, and separately registered. Each owns its endpoint mapping, options, validators, service interfaces, provider clients, and background or event consumers.
* Provider clients are generated or typed where useful but always hidden behind owned adapters, mappers, and service interfaces. Generated SDKs, SOAP or WCF proxies, and provider models never appear in public API contracts, module contracts, audit contracts, or durable domain records.
* Module services map provider behaviour into owned DTOs and facts, and own mapping, error handling, and orchestration.
* Explicit sandbox or mock versus production or real provider wiring.
* Decorators for journaling, job scheduling, and evidence cross-cuts where the ordering is explicit.
* Module persistence stays in the module's own schema. Store provider consent or session state only when approved (see "When to ask").
* Separate hosts for distinct product surfaces such as live-event UI and API, and for worker concerns.
* Provider endpoints, credentials, API keys and merchant IDs come from configuration, and the module fails at startup when one is missing. For secret storage, follow the engineering rules and `security-owasp` (Secrets).
* The domains in "Domain risk and approval" are gated. Follow "When to ask" before implementing their behaviour.

## Module registration pattern

Each integration module: configures its API options from code and configuration; registers validators with FluentValidation; registers endpoint explorer and OpenAPI support; registers services behind interfaces; registers provider clients and handlers through `HttpClient`; registers event producers and consumers from configuration; maps endpoints through a module-level `MapX` method.

Use the shape, not the values. Never copy route names, scopes, authorization values, request/response models, or provider option names.

### Module layout

```
Company.Services.<Feature>/
  <Feature>FeatureExtensions.cs   // Add<Feature>(services, configuration, configure?) + Map<Feature>(routes)
  <Feature>ApiOptions.cs          // Prefix, Scope, Group, ConfigureDbContext?, Configure<Provider>?
  <Provider>Options.cs            // SectionName const, base URLs, credential references, provider timeouts
  Clients/                        // generated client (nswag/Kiota) + auth DelegatingHandler; never public
  Endpoints/<Feature>Api.cs       // MapGroup, tags, group name, scope policy, OpenAPI
  Endpoints/<Feature>Handlers.cs  // thin: validate -> call service -> map to TypedResults/ProblemDetails
  Services/Abstractions/I<Feature>Service.cs
  Services/<Feature>Service.cs    // orchestration + provider-to-owned mapping
  Models/ , Mappings/ , Validators/
  Hubs/<Name>/Consumers, Worker   // only if the module consumes events
  Data/                           // only if the module owns persistence (own schema + DbContext)
```

### Registration example

```csharp
public static IServiceCollection AddAcme(this IServiceCollection services, IConfiguration configuration, Action<AcmeApiOptions>? configure = null) {
    var options = new AcmeApiOptions();
    configure?.Invoke(options);
    services.Configure<AcmeApiOptions>(o => { o.Prefix = options.Prefix; o.Scope = options.Scope; o.Group = options.Group; });

    services.AddOptions<AcmeProviderOptions>()
        .Bind(configuration.GetSection(AcmeProviderOptions.SectionName))
        .ValidateDataAnnotations()
        .ValidateOnStart();                                    // fail closed: missing URL/credentials stop startup
    if (options.ConfigureProvider is not null) services.PostConfigure(options.ConfigureProvider);

    services.AddTransient<AcmeAuthHandler>();
    services.AddHttpClient<IAcmeClient, AcmeClient>((sp, http) =>
            http.BaseAddress = sp.GetRequiredService<IOptions<AcmeProviderOptions>>().Value.BaseAddress) // never hardcoded
        .AddHttpMessageHandler<AcmeAuthHandler>();             // resilience comes from the Indice builder

    services.AddScoped<IAcmeService, AcmeService>();
    services.AddEndpointsApiExplorer();
    services.AddEndpointParameterFluentValidation();
    services.AddValidatorsFromAssemblyContaining<AcmeApiOptions>();
    return services;
}

public static IEndpointRouteBuilder MapAcme(this IEndpointRouteBuilder routes) {
    var options = routes.ServiceProvider.GetRequiredService<IOptions<AcmeApiOptions>>().Value;
    var group = routes.MapGroup($"{options.Prefix.Value?.TrimEnd('/')}/acme")
        .WithTags("Acme").WithGroupName(options.Group)
        .RequireAuthorization(p => p.RequireAuthenticatedUser().RequireClaim("scope", options.Scope))
        .WithOpenApi();
    group.MapPost("/reports/{propertyId}", AcmeHandlers.RequestReport).WithName(nameof(AcmeHandlers.RequestReport));
    return routes;
}
```

### Calling Indice platform services from a module

Calls to other Indice services (Cases, Messaging, other internal APIs) use `Duende.AccessTokenManagement`:

* **Machine-to-machine:** register a named client-credentials client once per module, then add `.AddClientCredentialsTokenHandler("<name>")` to each typed client. Read the base URL from configuration, and send each service only the scopes it needs. Do not register two named clients with the same credentials and scope.
* **Acting for a user:** use an on-behalf-of (token exchange) handler only when the downstream service must see the end user. Never swap a user call for a client-credentials call to get around user authorization.
* For the API contracts, see `indice-cases` and `indice-messaging`.

### Provider authentication handlers

When a provider uses its own login (username and password, an API key, or a token endpoint that isn't OIDC), put it in one `DelegatingHandler`:

* Cache the provider **token**, not the request, with an expiry taken from the token response minus a safety margin. Use `IMemoryCache` or `HybridCache`, with a key that includes the provider and the client.
* Prevent a stampede of token refreshes with a `SemaphoreSlim`. On a 401, refresh once and retry once.
* If the token call fails, fail with a typed error. Never send the request without authentication, and never swallow the failure.
* Use `FormUrlEncodedContent` or JSON as the provider documents. Deserialize with shared `JsonSerializerOptions` and pass the `CancellationToken`.
* Never inject an `HttpClient` into a `DelegatingHandler` (it causes handler cycles and socket misuse). Use `IHttpClientFactory.CreateClient("<provider>-auth")` for the token call.
* Keep version and accept headers in options, not hardcoded.

### Scheduled sync and trigger consumers

For periodic jobs (price sync, pushing orders to an ERP, cleaning up pending payments), use a trigger event consumed by a hosted service:

* The consumer takes a **distributed lock** per job type (for example `ILockManager`), so only one instance runs each job. Release the lock in a `finally` block, never only on the success path.
* Process each record independently. Persist progress as a resumable state (for example `NotSent → CustomerSent → OrderSent`), with an attempt counter and the time of the last attempt. One failure must not stop the batch.
* After N failed attempts, alert operations through Indice Messaging (see `indice-messaging`), using an alias for the template or recipient list. Don't send an email straight from the job.
* Generate a correlation or call ID for each outbound sync and log it, so it can be reconciled with the provider.
* If an event fails to deserialize, return or dead-letter it immediately. Do not continue with a null model.

## Outbound calls

Every call to an external provider goes through a typed or named `HttpClient` with explicit timeouts and error mapping.

The Indice builder (`Indice.AspNetCore.Builder`) already adds a resilience handler to every `HttpClient`. **Do not add `AddStandardResilienceHandler` or any other resilience handler yourself.** Stacked handlers multiply retries and timeouts. If a provider needs different resilience settings, change the builder's configuration rather than adding a second handler.

```csharp
builder.Services.AddOptions<AcmeProviderOptions>()
    .BindConfiguration("Integrations:Acme");

builder.Services.AddHttpClient<AcmeProviderClient>((sp, http) => {
        var options = sp.GetRequiredService<IOptions<AcmeProviderOptions>>().Value;
        http.BaseAddress = options.BaseAddress;
    })
    .AddHttpMessageHandler<AcmeSigningHandler>();         // mTLS / signing / auth stay in handlers
                                                          // resilience comes from the Indice builder
```

* **Idempotency.** Generate an idempotency key once per business operation, store it with the operation, and send the same key on every retry. Before re-sending after a timeout, reconcile by querying the provider. A timeout means the outcome is unknown, not that the call failed.
* **Cancellation.** Pass the `CancellationToken` through every endpoint, service, adapter and client call. Do not cancel a command once it has been sent to the provider. Record it as pending and reconcile it later.
* **Error mapping.** The adapter turns provider responses into owned results such as `Result<T>` or typed errors. Endpoints return `ProblemDetails`:
  * Provider validation errors map to 400 or 422.
  * "Not found" maps to 404.
  * Unavailable, timeout or open circuit maps to 503 or 504.
  * Unexpected provider errors map to 502.
  * Never return provider error bodies, codes or stack traces to callers. Log them redacted, with a correlation ID.
* **Long-running or deferred work.** Use an outbox. The business transaction stores the intent, and a worker sends it to the provider. Do not call providers inside a database transaction.

## Inbound callbacks and webhooks

Treat every provider callback as untrusted input from the internet.

1. **Authenticate:** verify the provider's signature or HMAC over the raw request body, using a constant-time comparison (`CryptographicOperations.FixedTimeEquals`) and a secret from a secret store. Where the provider supports them, also use mTLS or IP allow-lists. Reject unsigned callbacks before parsing or logging the body.
2. **Prevent replay:** require a timestamp and a nonce or event ID. Reject timestamps outside a short window, for example 5 minutes, and reject event IDs you have already seen.
3. **Deduplicate:** store the provider event ID in an inbox table with a unique constraint, and process each event at most once. Providers deliver the same event more than once.
4. **Acknowledge fast:** validate, persist to the inbox, and return 2xx. Process the event asynchronously in a worker. Never do slow or external work inside the callback request.
5. **Reconcile before acting:** for financial, KYC or consent state, a callback is only a hint. Fetch the authoritative state from the provider API before changing business state. Never trust amounts, statuses or identifiers that only appear in the callback body.
6. **Expect out-of-order delivery:** apply state transitions only if they move forward, and ignore stale events.
7. **Redirect callbacks** (for example after SCA or 3DS): treat query parameters as untrusted. Bind them to the server-side session with `state` and PKCE, and only redirect to allow-listed URLs.
8. **Endpoint hygiene:** callback endpoints are anonymous only when signature verification replaces authentication. They are rate-limited, have no CORS, have request-size limits, and respond the same way to unknown and invalid events.

### Common pitfalls (seen in real integrations)

| Pitfall | Do instead |
|---|---|
| Base URL hardcoded in code, sometimes the same in both branches of an `IsDevelopment` check | Provider options with `ValidateOnStart`; one value per environment in configuration |
| Credentials defaulting to `string.Empty` when missing | Required options; fail at startup |
| Auth handler caching the `HttpRequestMessage` instead of the token, with a fixed 60-minute expiry | Cache the token, with expiry taken from the token response |
| `HttpClient` injected into a `DelegatingHandler` | `IHttpClientFactory` with a separate auth client |
| `DisableAntiforgery()` on a callback with no signature check, trusting the posted order and transaction IDs | Verify the signature, then reconcile with the provider API before changing state |
| Redirect URL built from posted IDs without checking them against the session | Look up the server-side order, check it belongs to the user and session, and redirect only to an allow-listed URL |
| Consumer continues after a `null` event model; lock released only on success | Return early or dead-letter; release the lock in `finally` |
| Copy-pasted log messages ("Failed to create user" in a payment trigger) | A specific message for each operation, with a correlation ID |
| Raw event payload or request body logged on failure | Log IDs and the event type only (see `security-owasp`) |
| A "billable" provider call (for example forcing a new report) exposed with no extra authorization or rate limit | A separate policy, a per-user or per-tenant rate limit, and an audit entry |
| Several modules each building the same client-credentials client | One named client for each audience and scope set |

## Testing

Tests never call real providers.

* **Unit tests** cover mappers, error mapping, idempotency and state transitions against the adapter interface, using fakes. Provider clients are not mocked at the HTTP level here.
* **Adapter tests** run the real adapter against a stub HTTP handler or WireMock.Net server that replays recorded, scrubbed sandbox responses. They cover success, validation errors, 401/403, 404, 429 with `Retry-After`, 5xx, timeouts and malformed bodies.
* **Resilience tests** prove that non-idempotent commands are not retried, that the idempotency key stays the same across retries, and that timeouts produce an "unknown, reconcile" outcome.
* **Callback tests** cover:
  * a valid signature
  * an invalid or missing signature
  * an expired timestamp
  * a replayed event ID
  * duplicate delivery
  * out-of-order events
  * reconciliation when the callback disagrees with the provider API
* **Contract tests:** check generated clients and stored request/response fixtures against the provider's published spec, and fail the build when the spec changes.
* **Sandbox tests:** only in a separate, opt-in suite (for example `[Trait("Category", "Sandbox")]`) with credentials from a secret store. They are never part of the default CI run and never use production endpoints.
* **Test data:** synthetic only. No realistic personal, tax, account, card or identity data, and no recorded payloads that have not been scrubbed.

## Domain risk and approval

These decisions are never copied from another project or invented by an agent. If the requirement doesn't define one, follow "When to ask". The last column says whose decision it really is, so the user can check with that person if it isn't them.

| Domain | Decide per project, never copy | Main risk | Who should confirm | Related skill |
|---|---|---|---|---|
| PSD2 / open banking | Consent statuses and lifetimes, SCA flow, redirect and callback paths, mTLS and signing setup, account and payment models, scopes | Unauthorized access to accounts or payments; regulatory breach | Security, compliance, product owner | `indice-iam`, `security-owasp` |
| Consent and token storage | Which tokens and verifiers are stored, encryption, retention, who can read them | Token theft; replay | Security, data protection officer | `security-owasp` |
| Payments and gateways | Payment and settlement statuses, gateway response mapping, 3DS/SCA, timeouts, refunds and chargebacks, scheduled or standing payments, fees, ledger posting, reconciliation | Lost or double payments; wrong balances | Payments/ledger owner, finance, security | `security-owasp` |
| Card data | Any card data handling | PCI DSS scope | Security, compliance | `security-owasp` |
| Token / MFA providers | Token lifecycle, serial numbers, auth-code checks, resync rules | Account takeover; broken MFA | Security, IAM owner | `indice-iam` |
| KYC, registries, tax authority | Fields requested, tax-ID / IBAN / mobile matching rules, cache duration, what is stored | Wrong identity decisions; privacy breach | Compliance (KYC/AML), data protection officer, legal | `indice-cases` |
| Manual review and approvals | Case types, checkpoints, attachments, who reviews | Decisions made outside the audited workflow | Product owner, compliance | `indice-cases` |
| Notifications | Templates, message types, recipients, channels, copy | Wrong or unwanted messages; consent breach | Product owner, legal (marketing consent) | `indice-messaging` |
| CRM, documents, ERP | Field mappings, document types, accounting behaviour, what is synced and when | Corrupted master data; accounting errors | Data owner, finance (ERP) | — |
| Market data, listings, valuations | How provider data is interpreted and shown, billable calls | Misleading figures; unexpected cost | Product owner | — |
| Search and locations | Index schemas, ranking, data sources, rebuild jobs, data residency | Data leakage across tenants; residency breach | Data owner, operations | — |
| Events and workers | Event names and schemas, consumer groups, retries, dead-letter, schedules, instance counts | Lost or duplicated processing | Architecture, operations | — |
| Logging and evidence | What is logged or journaled, redaction, retention, deletion of audit data | PII or secret leakage; lost evidence | Security, data protection officer, legal | `security-owasp` |

Also never copy, in any domain: URLs, client IDs, secrets, certificates, scopes, route names, queue/hub/index names, sandbox IDs, or real customer data.

## PSD2 and open banking

Pattern: explicit registration for PSD2 storage, generated provider clients, mappers, named HTTP clients, provider-specific handlers, mutual TLS, HTTP signatures, consent services, consent repositories, and journaling decorators.

* Keep each provider client isolated behind typed services and mappers.
* Keep HTTP-signature and mTLS setup inside named client configuration, not business endpoints.
* Keep consent storage behind a repository and service layer.
* Decorate consent and product services with journal or audit behaviour instead of mixing evidence writes into generated clients.

## Payments, gateways, jobs, and journaling

Patterns: a provider gateway adapter, a transaction service, a callback or result endpoint, EF-owned order and transaction persistence, provider session creation, update, and retrieval, and event publication after completion. Payments composed through decorators: one creates or updates a scheduled job transaction when a payment cannot execute immediately; another writes journal entries for executed payment and history actions.

* Keep scheduling and job conversion outside the core payment adapter.
* Store a durable job transaction record when a payment becomes deferred work.

* Payment results arrive through callbacks. Follow "Inbound callbacks and webhooks" and reconcile with the gateway before marking anything paid.

## Token providers

Pattern: a generated WCF proxy with token lookup, details, assignment, removal, state changes, resync, and auth-code validation, behind an adapter, with explicit and auditable lifecycle operations.

Do not

Do not enable token-style MFA until it is approved (see "When to ask"). IAM and security should confirm it (see `indice-iam`).

## Government KYC, registries, and tax authority

Shapes: e-gov KYC retrieval with profile and tax-id matching, cache storage, object-journal persistence, customer-selected field filtering, and case attachment submission; tax-authority WCF services validating mobile/tax-id and IBAN/tax-id combinations with request/response logs; government-registry lookups behind provider handlers.

* Keep government, registry, and tax adapters behind services.
* Store the original provider payload and the user-selected payload separately, only when approved (see "When to ask").
when approved (see "When to ask"). Create a draft case, upload the attachments, then submit it through the Cases Manage API with a machine-to-machine client (see the `indice-cases` skill). Keep only the `caseId` and `referenceNumber` in the module.
* Write evidence through explicit journal or audit services.

## CRM, documents, market data, listings, ERP

Pattern: provider handlers plus module services that isolate external calls from endpoints; some modules publish or consume events.

* One adapter per provider surface; one module service per use case.
* Configuration-backed provider options; health checks for external dependency readiness.
* No provider models leaking into owned contracts.

## Locations and search

Pattern: EF persistence, NetTopologySuite, and search clients created from configuration. Search infrastructure is an adapter; module services own how data is queried and returned.

## Event hubs and workers

Patterns: event-hub producers and consumers plus hosted services for cross-system synchronization. Consumers parse an event envelope, validate required actor and context fields, call provider adapters, and log failures with structured data. Scheduled and queue-triggered workers: one fetches alerts from a core system into a queue; another delivers SMS, email, or push and acknowledges the core system on success.

* Keep producer and consumer registration configuration-driven; use explicit consumer factories or keys, not reflection magic.
* Keep each consumer focused on one external synchronization action.
* Separate fetch, queue, delivery, and callback or acknowledgement responsibilities.
* Configure schedules, polling interval, instance count, and queue name from configuration.
* Wrap worker operations in telemetry.
* Event schema, consumer groups, checkpoint storage, idempotency, retry policy and dead-letter behaviour come from the requirement. If they are missing, ask (see "When to ask").

User notifications (SMS, email, push, inbox) go through Indice Messaging, never directly to a provider from an integration. A worker that needs to notify users calls the Messaging Send API (`POST /api/send`) with a machine-to-machine client that has the `messages:send` scope. It uses template and type aliases rather than GUIDs, and records the returned `campaignId` (see the `indice-messaging` skill).

## Live events and SignalR

Pattern: a live-events API and UI separate from general APIs, with Azure Functions handling SignalR negotiation and targeted user messaging. Negotiation validates an access token, extracts the subject, and binds the user to a connection.

* Keep real-time UI as a separate host or shell when the feature is distinct.
bind messages to validated user identity.
* Keep target names and payloads behind typed message containers.

## Logging and observability

Pattern: Serilog, Application Insights, ELK or Logstash examples, action filters that enrich logs with user and client IP, and telemetry around worker operations.

* Put correlation, user, and context enrichment in a focused filter or middleware.
* Keep logging infrastructure separate from application modules.

What may be logged, how it is redacted, and the split between logging and audit are defined in `security-owasp` (PII and sensitive data; Audit versus logging; Payments and PCI posture). Do not restate those rules here. For integrations specifically: log the provider name, operation, correlation ID, HTTP status and duration, never request or response bodies.

## Audit and cleanup

Deletion, purge, archival and cleanup of audit or evidence stores stay blocked until retention and legal-hold rules are approved (see "When to ask"). If they aren't, follow the gated sensitive zone rule.

## SQL, seeds, identity, cases, and provider-owned artifacts

* Do not port reference SQL scripts, stored procedures, or product and workflow seed files as migrations. Treat them as a signal that provider setup may need explicit operational scripts, review notes, rollback planning, and environment ownership. Any script or migration stays within the owning module or Indice-owned product boundary and is reviewed for SQL impact.
* Do not copy identity clients, secrets, certificate blobs, scopes, claims, redirect URIs, CORS origins, or seeded users.
* Do not copy case or workflow definitions, case types, attachment names, or workflow-driven regulated decisions. Integrations use Cases through its APIs only (see `indice-cases`); case types, checkpoints and access rules are configured inside Cases, not in integration code.
* Do not copy Messaging templates, message types, recipient lists or provider settings. Integrations use Messaging through its APIs only (see `indice-messaging`).
* Never use realistic personal, tax, identity-document, payment, account, property, or customer data from references in tests, seeds, logs, docs, or examples.

## Related skills

* `security-owasp`: secrets, PII and logging redaction, audit versus logging, PCI posture, webhook and rate-limit baseline.
* `indice-cases`: manual review and back-office workflows through the Cases Manage API (machine-to-machine) and customer-facing access through the Cases My API.
* `indice-messaging`: user notifications through the Messaging Send and My APIs.
* `indice-iam`: machine-to-machine clients, scopes and token-based MFA.
* `indice-templates`: scaffolding new Indice hosts.
