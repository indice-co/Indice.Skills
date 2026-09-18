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

Reference integration projects are an architecture and implementation-style source only. They inform boundaries, host and module composition, adapter shape, logging, and worker composition. They never define product behaviour, and they are scrubbed of secrets, certificates, provider identifiers, and deployment values, so they are not expected to build.

## Boundaries to carry forward

Separate host, module, adapter, generated client, mapper, service, decorator, and worker:

* The host is a composition root. It wires common platform services first, then each integration module through focused `AddX` and `MapX` extension methods.
* Integration modules are explicit, small, and separately registered. Each owns its endpoint mapping, options, validators, service interfaces, provider clients, and background or event consumers.
* Provider clients are generated or typed where useful but always hidden behind owned adapters, mappers, and service interfaces. Generated SDKs, SOAP or WCF proxies, and provider models never appear in public API contracts, module contracts, audit contracts, or durable domain records.
* Module services map provider behaviour into owned DTOs and facts, and own mapping, error handling, and orchestration.
* Explicit sandbox or mock versus production or real provider wiring.
* Decorators for journaling, job scheduling, and evidence cross-cuts where the ordering is explicit.
* Module persistence stays separate where provider or product persistence is approved. Dedicated repositories for provider consent or session state only when approved.
* Separate hosts for distinct product surfaces such as live-event UI and API, and for worker concerns.
* Provider endpoints, credentials, scopes, API keys, merchant IDs, and base URLs come from approved configuration or secret stores and fail closed when missing. Never checked-in appsettings or test fixtures.
* Financial, identity-document, KYC/AML, tax, token/MFA, PSD2, CRM, compliance-impacting, logging and evidence, and real-time event behaviour need explicit approval before implementation.

## Module registration pattern

Each integration module: configures its API options from code and configuration; registers validators with FluentValidation; registers endpoint explorer and OpenAPI support; registers services behind interfaces; registers provider clients and handlers through `HttpClient`; registers event producers and consumers from configuration; maps endpoints through a module-level `MapX` method.

Use the shape, not the values. Never copy route names, scopes, authorization values, request/response models, or provider option names.

## PSD2 and open banking

Pattern: explicit registration for PSD2 storage, generated provider clients, mappers, named HTTP clients, provider-specific handlers, mutual TLS, HTTP signatures, consent services, consent repositories, and journaling decorators.

* Keep each provider client isolated behind typed services and mappers.
* Keep HTTP-signature and mTLS setup inside named client configuration, not business endpoints.
* Keep consent storage behind a repository and service layer.
* Decorate consent and product services with journal or audit behaviour instead of mixing evidence writes into generated clients.

Never copy: provider APIs, generated SDKs, scopes, account, payment, or card models, consent status mappings, SCA behaviour, token lifetimes, redirect and callback paths, certificate header names, signing algorithms, mTLS behaviour, sandbox IDs, or endpoint semantics. Consent schema fields such as access tokens, refresh tokens, PKCE verifiers, SCA method, redirect URI, and status values need explicit approval of storage, encryption, retention, redaction, and ownership. Request/response logging or snapshots with headers and bodies need approved redaction and retention rules.

## Payments, gateways, jobs, and journaling

Patterns: a provider gateway adapter, a transaction service, a callback or result endpoint, EF-owned order and transaction persistence, provider session creation, update, and retrieval, and event publication after completion. Payments composed through decorators: one creates or updates a scheduled job transaction when a payment cannot execute immediately; another writes journal entries for executed payment and history actions.

* Keep scheduling and job conversion outside the core payment adapter.
* Store a durable job transaction record when a payment becomes deferred work.
* Keep worker execution paths separate from immediate user-request execution.

This is a cautionary reference, not a template. Never copy: payment types, status machines, gateway response mapping, 3DS or SCA behaviour, card data handling, timeout windows, redirect paths, settlement states, refund or chargeback assumptions, schedule semantics, immediate, post-dated, or standing-order behaviour, localization, job descriptions, journal reason text, fee or expense behaviour, payment-complete event names, ledger interaction, reconciliation, or validation rules. These belong to the payments and ledger design.

## Token providers

Pattern: a generated WCF proxy with token lookup, details, assignment, removal, state changes, resync, and auth-code validation, behind an adapter, with explicit and auditable lifecycle operations.

Never copy: operation semantics, serial-number handling, auth-code behaviour, state values, resync rules, identifiers, endpoint URLs, binding settings, or proxy contracts. Do not enable token-style MFA without approved IAM, security, and evidence inputs.

## Government KYC, registries, and tax authority

Shapes: e-gov KYC retrieval with profile and tax-id matching, cache storage, object-journal persistence, customer-selected field filtering, and case attachment submission; tax-authority WCF services validating mobile/tax-id and IBAN/tax-id combinations with request/response logs; government-registry lookups behind provider handlers.

* Keep government, registry, and tax adapters behind services.
* Store the original provider payload and the user-selected payload separately, only when approved.
* Use a case or workflow boundary for manual review or update requests, when approved.
* Write evidence through explicit journal or audit services.

Never copy: KYC scopes, field taxonomy, tax-id matching behaviour, cache duration, case type names, attachment names, PDF or email behaviour, request/response contracts, registry meaning, IBAN or mobile validation semantics, or logging payloads. These need KYC/AML, privacy, legal, case-management, and provider-governance approval.

## CRM, documents, market data, listings, ERP

Pattern: provider handlers plus module services that isolate external calls from endpoints; some modules publish or consume events.

* One adapter per provider surface; one module service per use case.
* Configuration-backed provider options; health checks for external dependency readiness where approved.
* No provider models leaking into owned contracts.

Never copy: request/response semantics, authentication headers, identifiers, taxonomy, document types, CRM field names, ERP accounting behaviour, or market and listing data interpretation.

## Locations and search

Pattern: EF persistence, NetTopologySuite, and search clients created from configuration. Search infrastructure is an adapter; module services own how data is queried and returned.

Never copy: index names, index schemas, query behaviour, keys, data sources, or ranking assumptions. Search ownership, rebuild jobs, data residency, retention, and operational evidence need approval.

## Event hubs and workers

Patterns: event-hub producers and consumers plus hosted services for cross-system synchronization. Consumers parse an event envelope, validate required actor and context fields, call provider adapters, and log failures with structured data. Scheduled and queue-triggered workers: one fetches alerts from a core system into a queue; another delivers SMS, email, or push and acknowledges the core system on success.

* Keep producer and consumer registration configuration-driven; use explicit consumer factories or keys, not reflection magic.
* Keep each consumer focused on one external synchronization action.
* Separate fetch, queue, delivery, and callback or acknowledgement responsibilities.
* Configure schedules, polling interval, instance count, and queue name from approved configuration.
* Wrap worker operations in telemetry.
* Event schema, consumer groups, checkpoint storage, idempotency, retry policy, dead-letter behaviour, evidence, and operations ownership are approved inputs.

Never copy: event, topic, queue, or hub names, consumer groups, action semantics, payload schemas, retry behaviour, alert channels, delivery copy, polling intervals, instance counts, callback behaviour, delivery evidence, recipient semantics, provider settings, or telemetry thresholds. Delivery belongs in the messaging and worker boundary (see the `indice-messaging` skill).

## Live events and SignalR

Pattern: a live-events API and UI separate from general APIs, with Azure Functions handling SignalR negotiation and targeted user messaging. Negotiation validates an access token, extracts the subject, and binds the user to a connection.

* Keep real-time UI as a separate host or shell when the feature is distinct.
* Protect negotiation endpoints and bind messages to validated user identity.
* Keep target names and payloads behind typed message containers.

Never copy: CORS policy, routes, token validation details, hub or target names, voting or sign-in flows, media behaviour, SMS copy, or message payload semantics.

## Logging and observability

Pattern: Serilog, Application Insights, ELK or Logstash examples, action filters that enrich logs with user and client IP, and telemetry around worker operations.

* Put correlation, user, and context enrichment in a focused filter or middleware.
* Keep logging infrastructure separate from application modules.

Caution: reference projects log serialized payment or transfer request payloads and tax-authority request/response bodies. Do not. Logs must not include secrets, tokens, raw payment data, unnecessary PII, government or tax payloads, KYC evidence, card or account numbers, or regulated evidence unless an approved design defines redaction, retention, access, and immutable evidence rules.

## Audit and cleanup

Learn only the separation between audit service, audit endpoints, EF context, and hosted cleanup worker. Deletion, purge, archival, retention, and cleanup of audit or evidence stores are regulated and stay blocked until retention and legal-hold rules are approved.

## SQL, seeds, identity, cases, and provider-owned artifacts

* Do not port reference SQL scripts, stored procedures, or product and workflow seed files as migrations. Treat them as a signal that provider setup may need explicit operational scripts, review notes, rollback planning, and environment ownership. Any script or migration stays within the owning module or Indice-owned product boundary and is reviewed for SQL impact.
* Do not copy identity clients, secrets, certificate blobs, scopes, claims, redirect URIs, CORS origins, or seeded users.
* Do not copy case or workflow definitions, case types, attachment names, or workflow-driven regulated decisions.
* Never use realistic personal, tax, identity-document, payment, account, property, or customer data from references in tests, seeds, logs, docs, or examples.
