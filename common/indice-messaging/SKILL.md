---
name: indice-messaging
description: >
  Use when an application integrates with an existing Indice Messaging
  deployment: sending messages from a backend (machine-to-machine) through the
  Send API, or showing a signed-in user's inbox, read state and communication
  preferences through the My API. Defines the API contracts, IAM scopes,
  client setup, boundaries and what must never be duplicated. For creating or
  hosting a Messaging service, use the `indice-templates` skill instead.
---

# Indice Messaging integration

This skill covers **consuming** Indice Messaging. It does not cover hosting it.
To scaffold a Messaging host or worker, use the `indice-templates` skill
(`indice.messaging`, `indice.messaging.Solution`, `indice.messaging.workers`).

## Contracts

The OpenAPI documents next to this file are the source of truth. Generate clients from them; do not hand-write DTOs.

| Spec | Consumer | Flow | Scope |
|---|---|---|---|
| [messaging-send.json](messaging-send.json) — *Messaging Send REST API* | Backend services and integrators (machine-to-machine) | OAuth2 client credentials | `messages:send` |
| [messaging-my.json](messaging-my.json) — *Messaging My REST API* | Signed-in end users (web, mobile, BFF) | OAuth2 authorization code + PKCE | `messages` |

The `servers`, `tokenUrl` and `authorizationUrl` values in the specs (`messaging.indice.gr`, `my.indice.gr`) are examples only. Read the Messaging base URL and the IAM authority from configuration for each environment.

Every error response is a `ProblemDetails`. Validation errors (400) are an `HttpValidationProblemDetails`. Handle 401, 403 and 500 explicitly, and never swallow them.

## IMPORTANT: use aliases, not GUIDs

> **When a field accepts either an alias or a GUID, always use the alias.**
> GUIDs are generated separately in each environment (dev, test, production), so a GUID that works in one environment breaks in the others.
> Aliases are stable, readable and the same across environments. Only fall back to a GUID if the resource has no alias. If it doesn't, ask the Messaging administrator to add one rather than hardcoding the GUID.

| Field | API | Use |
|---|---|---|
| `SendRequest.messageTemplateId` | Send | Template alias, e.g. `"order-confirmation"` |
| `SendRequest.typeId` | Send | Message type alias, e.g. `"orders"` |
| `SendRequest.recipientListId` | Send | Distribution list alias |
| `TypeId` query in `GET /api/my/messages` | My | Message type aliases |
| `MarkAsReadRequest.typeId` | My | Message type aliases |
| `UpdateMessageTypePreference.messageTypeAlias` | My | Alias only; take it from `MessageType.alias` in `GET /api/messages/types` |

- Keep aliases in configuration or named constants, for example a `MessagingAliases` class. Never put raw GUIDs in code.
- In code review, reject any hardcoded GUID passed to one of the fields above.
- The following fields really are GUIDs (`uuid` format) and should only be used as values returned by the API: `campaignId`, `Message.id`/`messageId`, `MessageType.id`, `MessageSender.id`.

## Send API (machine-to-machine)

`POST /api/send` (`SendCampaign`) creates a campaign and returns a `CreateCampaignResult` (`campaignId`, `succeeded`, `errors`). Treat `succeeded: false` as a failure even when the HTTP status is 200, and log `errors` without logging recipient PII.

The body is a `SendRequest`. It has these parts:

- **Recipients** — pick one of these:
  - `recipientIds`: IAM user IDs (`sub`). This is the preferred option; Messaging resolves contact details through IAM.
  - `recipients`: `ContactAnonymous` entries (`recipientId`, `email`, `phoneNumber`, names, `salutation`), for people who are not IAM users.
  - `recipientListId`: an existing distribution list.
  - `isGlobal: true`: everyone. Only use this when the product owner has explicitly approved it.
- **Content** — pick one of these:
  - `messageTemplateId` together with `messageTemplateChannels` (`Inbox`, `PushNotification`, `Email`, `SMS`). Use this when the content is managed in the Messaging UI.
  - `title` plus `content`. `content` is a dictionary keyed by channel, and each value is a `MessageContent` (`sender`, `title`, `body`).
- **Optional fields:**
  - `typeId`: the inbox message type or category.
  - `data`: merge fields for the template.
  - `actionLink`: a `Hyperlink` (`text`, `href`).
  - `activePeriod`: a `Period` (`from`, `to`).
  - `mediaBaseHref`.
  - `ignoreUserPreferences`: overrides the user's communication preferences. Only allowed for approved transactional or regulatory messages, never for marketing.

### Client setup (.NET)

1. In IAM, register a dedicated confidential client for the calling service. Give it the `client_credentials` grant only, and only the `messages:send` scope. Do not reuse a user-facing client. See the `indice-iam` skill.
2. Store the client ID and secret in user-secrets or Key Vault, never in `appsettings*.json`.
3. Generate a typed client (for example NSwag or Kiota) from `messaging-send.json`.
4. Wire it up with `Duende.AccessTokenManagement` so tokens are cached and refreshed automatically:

```csharp
builder.Services.AddClientCredentialsTokenManagement()
    .AddClient("messaging", client => {
        client.TokenEndpoint = new Uri($"{builder.Configuration.GetAuthority(tryInternal: true)!.TrimEnd('/')}/connect/token");
        client.ClientId = ClientId.Parse(builder.Configuration.GetApiSecret("MessagingClientId"));
        client.ClientSecret = ClientSecret.Parse(builder.Configuration.GetApiSecret("MessagingClientSecret"));
        client.Scope = Scope.Parse("messages:send");
    });

builder.Services.AddHttpClient<MessagesClient>(http => http.BaseAddress = new Uri(builder.Configuration.TryGetEndpoint("Messaging")!))
    .AddClientCredentialsTokenHandler(ClientCredentialsClientName.Parse("messaging"));
```

### Sending rules

- Send from a background step or outbox, not inline in the user's request. A delivery failure must not roll back business state, and a retry must not send the message twice. Record the `campaignId` with the business event so the send is idempotent and traceable.
- Never put secrets, OTPs, passwords or full card/account numbers in message content or `data`.
- In dev and test environments, never send to real recipients unless the environment and recipient list have been explicitly approved.

## My API (end user)

Every call is made as the signed-in user, using an authorization code + PKCE token with the `messages` scope. The API scopes all data to the token's `sub`. Never pass a user ID; the API rejects attempts to act on another user's messages.

| Operation | Endpoint | Notes |
|---|---|---|
| List inbox | `GET /api/my/messages` | Query: `Page`, `Size`, `Sort`, `Search`, `TypeId`, `ActiveFrom`, `ActiveTo`, `ShowExpired`, `IsRead`. Returns `MessageResultSet` (`count`, `items`). |
| Get message | `GET /api/my/messages/{messageId}` | Optional `channel` query. Returns `Message`; 404 if not found or not owned. |
| Delete | `DELETE /api/my/messages/{messageId}` | Soft delete; 204. |
| Mark read / unread | `PUT /api/my/messages/{messageId}/read` · `/unread` | 204. |
| Mark all read / unread | `PUT /api/my/messages/all/read` · `/all/unread` | Body `MarkAsReadRequest` uses the same filters as the list, so it can be limited to a type or period. |
| Message types | `GET /api/messages/types` | Paged list used to build category filters. |
| Get preferences | `GET /api/my/preferences` | `ContactPreference`: `locale`, `consentCommercial`, `consentCommercialDate`, per-type `communication`, `defaultChannels`. |
| Update preferences | `PUT /api/my/preferences` | Body `UpdatePreferenceRequest`; 204. |

Rules:

- Always page the list. Do not fetch everything to count unread messages; use the `IsRead=false` filter and `count`.
- `Message.content` is server-rendered HTML. Sanitize it, or render it in a sandbox. Only follow `actionLink.href` and `attachmentUrl` when they point to an allowed host.
- Store tokens in a BFF or server-side session for browser apps (see `duende-bff`). Do not keep long-lived tokens in browser storage.
- Commercial consent changes are legal records. Make them a deliberate user action, and never pre-check consent or change it on the user's behalf.

## Boundary

- Messaging owns templates, campaigns, inbox state, read state, distribution lists, delivery and provider configuration. IAM owns contact identity and consent claims. Do not copy any of these into application tables; keep only the `campaignId` or `messageId` as a reference.
- Do not call email, SMS or push providers directly from an application to get around Messaging.
- Template content, message types, recipient lists and the choice of channel are product decisions. Use **aliases** that the product owner has approved, and read them from configuration.

## Do not copy

Do not copy any of the following from a reference project or from the specs:
- client IDs, secrets or scopes beyond the ones listed here
- authority and endpoint URLs
- template IDs, type IDs or recipient list IDs
- sender names, copy or merge-field values
- provider credentials