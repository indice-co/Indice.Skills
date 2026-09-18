---
name: indice-messaging
description: >
  Use when a task touches Indice Messaging: hosting the Messaging API and
  management UI, delivery workers, campaigns, templates, inbox, distribution
  lists, contact resolution, email/SMS/push providers, or the Messaging IAM,
  database, and storage setup. Defines the host and worker boundary, what the
  package owns, the template model, and what must never be copied.
---

# Indice Messaging

## Boundary

Messaging is a platform capability. Adopting it is an explicit, approved decision that must resolve: API, UI, and worker topology; providers and channels; templates, campaigns, and inbox taxonomy; contact resolution; delivery evidence; retention; and operations. Until then, do not enable real sends, templates, campaigns, inbox behaviour, distribution lists, contact resolution, provider configuration, retry policy, or notification evidence.

The Messaging product owns its provider schema, templates, inbox state, campaigns, delivery provider stores, and media artifacts inside the platform boundary. Application modules must not become the source of truth for any of these. Delivery execution belongs in workers, never in business modules or UI hosts.

## Two deployable surfaces

1. **API and UI host**: composes the Messaging APIs, management UI, Media Library, avatars, OpenAPI, health checks, cache, and static assets.
2. **Delivery worker**: a separate .NET isolated Azure Functions app that composes message processing and delivery providers.

Keep them separate. Templates: `dotnet new indice.messaging`, `indice.messaging.solution`, `indice.messaging.workers`, generated into a scratch location. The workers template defaults to net9.0, so pass `--Framework net10.0` or realign afterward.

## API and UI host

Packages: `Indice.Features.Messages.AspNetCore`, `Indice.Features.Messages.UI`, plus `Indice.Features.Media.AspNetCore`.

Template shape:

1. `IndiceWebApplicationBuilder.CreateBuilder(args)`, then `AddApplicationLocalization`, `AddApplicationCache`, `AddApplicationOpenApi`.
2. `AddAvatars()` and `AddDatabaseDeveloperPageExceptionFilter()` before product setup.
3. `AddMediaLibrary`: `Scope = GetApiResourceName()`, `PathPrefix = "/api"`, DbContext from `MessagesDb` with retry-on-failure, `UseFilesAzure()` or `UseFilesLocal()`.
4. `AddMessaging`: `RequiredScope = GetApiResourceName()`, `PathPrefix = "/api"`, DbContext from `MessagesDb`, file and event providers, `UseIdentityContactResolver` against the IAM authority with client credentials.
5. `AddWebServiceDefaults()` after Media Library and Messaging; application services and extra health checks follow.
6. Runtime: output cache, Swagger or Scalar in development, `UseMessagesUI`, `MapAvatars`, `MapMediaLibrary`, `MapMessaging`, OpenAPI, `MapHealthCheckDefaults()`.

`UseMessagesUI` mounts the embedded management UI with authority, host, client ID, scope, media-library enablement, document title, and static-file options. Health checks cover the IAM authority, `MessagesDb`, and blob storage when `StorageConnection` is configured. Keep UI client IDs, scopes, authority, host, schema, and storage choices in configuration.

## IAM contract

Template shape: management API scope `messages`; media scope `media`; admin UI client `messaging-ui` using authorization code flow; API resources `identity`, `messages`, `media`; identity resources `openid`, `profile`, `email`, `role`, `offline_access`; claims on `messages` and `media`: `admin`, `email`, `given_name`, `family_name`, `name`, `phone_number`, `role`, `sub`.

These are the template's shape only. Your client IDs, scopes, claims, resources, consent, contactability, and admin access come from your own approved IAM security contract (see the `indice-iam` skill).

## Worker

* `FunctionsApplication.CreateBuilder(args)`; registers worker OpenTelemetry, function health checks, application services, extra health checks, and `AddMessageFunctions`.
* `AddMessageFunctions` composes Azure event dispatch, push notifications, Azure files, email, SMS, IAM contact resolution, and database cleanup options. Push is an optional extension point.
* Reads `appsettings.json` from the script root because the function runs out of process, and uses the same message database schema.
* `host.json` sets queue `batchSize`, `maxDequeueCount`, `maxPollingInterval`, `messageEncoding`, `newBatchThreshold`, `visibilityTimeout`, and Application Insights sampling and `telemetryMode`.
* `local.settings.json` is local-only with Azurite-compatible `AzureWebJobsStorage`. Real storage, provider credentials, worker client secrets, and cleanup schedules live in approved configuration or secret stores.

Real provider setup requires approved secrets, sender identities, channel enablement, retry and fallback behaviour, suppression and consent behaviour, and monitoring. Local and test workers stay dev-safe and never send real notifications unless the environment and recipient model are explicitly approved.

## Contact resolution

Messaging resolves contacts through the identity contact resolver using client credentials from API secret configuration. Claims for commercial consent, locale, and communication preferences come from IAM. IAM stays the source of truth for contact identity and preference claims; do not duplicate contact data or consent rules in module-owned tables. Consent, suppression, preference, locale, and recipient selection are product decisions.

## Template model

* Template `Type` is `Full`, `Partial`, or `Layout`. Campaigns bind only to `Full` templates.
* `Partial` and `Layout` templates require a unique `Alias`, used as a Handlebars lookup key.
* Content is channel-keyed (`Email`, `Sms`, `PushNotification`, `Inbox`); the renderer resolves partial and layout content for the active channel.
* Layouts use `{{> @partial-block}}`; full templates can wrap content with a selected layout.

Templates, campaigns, inbox taxonomy, merge fields, copy, recipient groups, and channel payloads are product behaviour. They need approved copy, localization, consent and contactability, evidence, retention, and tests before they enter source. SQL seed and migration scripts for Messaging are reviewed as provider-owned or application-owned according to the agreed boundary.

## Operations

Reference hosts use SQL Server health checks for the message database, optional blob storage health checks, Azure file storage for assets, the Azure event dispatcher, a cache package, OpenTelemetry for workers, and CI pipelines that build the API/UI and worker images separately. Production storage, telemetry, queueing, event dispatch, and cleanup jobs need approved operations and security inputs. Delivery evidence, retries, dead-letter handling, cleanup, retention, purge, legal hold, archival, and export must be defined before production use.

## Do not copy

From any reference project: templates, aliases, campaign and inbox taxonomy, copy, merge fields, recipient semantics, sender names, channel choices, provider settings, notification journeys; client IDs, scopes, claims, authority and endpoint URLs, registry and pipeline values, connection strings, API secrets, SMTP, SMS, or provider credentials, storage keys, data-protection paths; SQL scripts as application-owned migrations without ownership, review notes, rollback, data impact, and evidence.
