---
name: indice-messaging
description: >
  Use when a task touches Indice Messaging (the Indice.Features.Messages.* packages):
  explaining what the product is and how a campaign becomes a delivered message, standing
  up a new Messaging API/UI host and delivery worker (from the `indice.messaging` dotnet
  templates or by hand), wiring AddMessaging / MapMessaging / UseMessagesUI /
  AddMessageFunctions, the Identity Server clients and scopes it needs, queues, email/SMS/push
  providers, contact resolution, Handlebars templates, the inbox or the send API, or debugging
  "the campaign was published but nothing was sent". Prefer the package over new code.
---

# Indice Messaging

## Purpose

What Indice Messaging is, how its pieces fit, and how to stand it up in a new solution
without guessing. Two companion files hold the detail, read them when the task needs it:

- [`setup.md`](setup.md): step-by-step for a new solution (templates, both `Program.cs`
  files, Identity Server registrations, database, local run, smoke test).
- [`reference.md`](reference.md): option defaults, configuration keys, endpoints, queue
  names, provider names, authorization rules, Handlebars context.

Everything here was checked against `Indice.Platform` (packages `8.57.x`) and the
`Indice.DotNet.Templates` messaging templates. If the code disagrees, the code wins: the
sources to read are listed under `## Read deeper`.

## Guardrail

Messaging is a product you compose, not code you write. Before adding a queue, a
"notification service", an email sender, an inbox table, or a template renderer to an
application, check whether Messaging already does it and say what you checked. Application
code talks to Messaging through its HTTP API (`POST {prefix}/send`) or its extension
interfaces. It does not write to the `cmp` schema.

## What it is

Campaign-based multichannel messaging, shipped as NuGet packages the client hosts on their
own infrastructure. A **campaign** is the unit of sending. It fans out to up to four
**channels** (`Inbox`, `PushNotification`, `Email`, `SMS`) per recipient, according to the
campaign's channels, the message type, and each contact's preferences. Marketing broadcasts
and transactional messages (OTP, receipt, alert) use the same pipeline: a transactional
message is a campaign created already published through the send API.

| Package | Contributes |
| --- | --- |
| `Indice.Features.Messages.Core` | `CampaignsDbContext` (schema `cmp`), models, services, validators, job handlers, options, `IContactResolver` |
| `Indice.Features.Messages.AspNetCore` | `AddMessaging()`, `MapMessaging()`, authorization, the endpoints. This is the server project, there is no `Messages.Server` |
| `Indice.Features.Messages.UI` | `UseMessagesUI()`: the Angular management SPA, embedded and served by the API host |
| `Indice.Features.Messages.Worker.Azure` | `AddMessageFunctions()`: Azure Functions (isolated) queue, Service Bus and timer triggers |
| `Indice.Features.Messages.Worker` | `AddMessageJobs()`: the same handlers in-process on `Indice.Hosting` (Quartz), no Azure needed |
| `Indice.Features.Media.AspNetCore` | `AddMediaLibrary()` / `MapMediaLibrary()`: the media library the UI uses for images (`MediaDbContext`, schema `media`) |

All of them multi-target `net8.0;net9.0;net10.0`. Keep every `Indice.*` reference in a
host on the same version.

## How a message gets delivered

```
Management UI  --publish-->  API host  --enqueue-->  campaign-created
System caller  --POST /send->                              |
                                                     Worker: load the distribution list,
                                                     one event per contact
                                                           v
                                                  campaign-resolve-message
                                                           |
                                    Worker: resolve contact, render Handlebars per channel,
                                    persist the inbox Message, compute allowed channels
                                                           v
                    campaign-send-email | campaign-send-sms | campaign-send-push-notification
                                                           |
                                              Worker: call the provider
```

The API host only validates, stores and enqueues. Resolving, rendering and sending happen
in the worker. Two deployables, one queue transport, one database.

Rules of the flow that are easy to get wrong:

- Nothing is enqueued until the campaign is `Published`. The send API forces it to `true`.
- The inbox `Message` row is written for every resolved recipient. Email, SMS and push are
  dispatched only for the channels `Contact.GetAvailableChannels(...)` returns: campaign
  channels, intersected with the contact's preferences for that message type, minus what
  the contact cannot receive (no email, no phone, anonymous).
  `IgnoreUserPreferences` skips the preference step for genuine system messages.
- A global campaign (`IsGlobal`) is not fanned out per contact. If it includes push it is
  broadcast once.
- A start date in the future rides the queue's visibility delay. Past 7 days the worker
  re-enqueues in 5-day hops (Azure Storage Queue limit).

## Domain glossary

- **Campaign**: title, per-channel content, target channels, optional action link (CTA),
  active period, type, distribution list, attachment, `Data` (free JSON for templates).
- **Message**: one campaign materialised for one recipient. This is what the inbox lists.
- **Contact**: a recipient. `RecipientId` is the correlation key to the system of record
  (the Identity `sub` by default). Anonymous contacts have only an email or phone.
- **Distribution list**: a reusable audience. CSV import and export. A campaign sent to
  ad-hoc recipients gets a system-generated list.
- **Message type**: a category with a classification. Contacts set channel preferences
  per type.
- **Message sender**: a "from" identity per channel. The worker seeds a default email
  sender from the configured email provider on first start.
- **Template**: per-channel Handlebars content. `Full` is what a campaign binds to.
  `Partial` and `Layout` are fragments referenced by alias (`{{> alias}}`,
  `{{#> alias}}…{{/alias}}`) and require a unique `Alias`.
- **Contact resolver** (`IContactResolver`): where contact data and consent come from.
  Default is a no-op. `UseIdentityContactResolver` reads them from Indice Identity.

## Setting it up

Follow [`setup.md`](setup.md). The shape, so you can judge a request before opening it:

1. Generate the two hosts: `dotnet new indice.messaging` (API + UI) and
   `dotnet new indice.messaging.workers` (Functions worker), or
   `dotnet new indice.messaging.Solution` for both.
2. Register in Identity Server: the `messages` API resource (scopes `messages`,
   `messages:send`) and `media` scope, the `messaging-ui` SPA client, a client-credentials
   client for contact resolution, and the `CampaignManager` role for operators.
3. Point both hosts at the same `MessagesDb` and the same `StorageConnection`, with the
   same environment name.
4. Pick providers in the worker's configuration (`Email:Provider`, `Sms:Provider`).
5. Create the database (automatic in Development only), run both hosts, publish a test
   campaign, watch the queues drain.

## What bites

Each of these is silent or confusing when it happens. Check them first when debugging.

- **No dispatcher, no delivery.** `AddMessaging()` defaults to a no-op event dispatcher,
  no-op file service and no-op contact resolver. Without `UseEventDispatcherAzure()` (or
  the Service Bus or in-process variant) publishing succeeds and nothing is ever enqueued.
- **Queue names carry the environment.** The API writes to `{environment}-campaign-created`
  using its host environment name, lower-cased. The Functions worker listens on
  `%ENVIRONMENT%-campaign-created`. The API's environment, the worker's host environment
  and the worker's `ENVIRONMENT` app setting must be the same word, or messages pile up in
  a queue nobody reads.
- **Both sides must choose the same transport.** Storage Queues on the API with
  `.WithServiceBusTriggers()` on the worker (or the reverse) delivers nothing. The worker
  enables one trigger set and disables the other.
- **The database is created only in Development.** A hosted service runs `EnsureCreated`
  for `CampaignsDbContext` and creates the media tables, and only when the environment is
  `Development`. `EnsureCreated` also does nothing if the database already contains tables,
  so do not point `MessagesDb` at a database another product already populated. Everywhere
  else, ship EF migrations from the host (see `setup.md`).
- **The timer needs its setting even when clean-up is off.** The Functions clean-up trigger
  binds `%MessageJobsOptions:DatabaseCleanUpCronExpression%`. The app setting must exist in
  every environment (`MessageJobsOptions__DatabaseCleanUpCronExpression` as an environment
  variable). `DatabaseCleanUpOptions.Enabled` defaults to `false`.
- **`Sms:Provider` is mandatory once `UseSmsService(configuration)` is called.** It throws
  at startup if the key is missing. Use `none` to wire SMS off. Email falls back to `Smtp`
  when `Email:Provider` is absent. Email provider names are case-sensitive, SMS names are not.
- **The contact resolver client needs Identity scopes.** `ContactResolverIdentity` requests
  a client-credentials token with scope `identity identity:users` and calls the Identity
  `api/users` endpoints. A client without those scopes, or without rights to read users,
  fails at fan-out, not at startup.
- **A custom recipient claim is not carried to the Functions worker.** The worker's
  `UseIdentityContactResolver` copies only base address, client id and secret. If
  `UserClaimType` is not `sub`, also
  `services.Configure<ContactResolverIdentityOptions>(o => o.UserClaimType = ...)` in the worker.
- **Scope alone is not enough for management.** Management endpoints require the API scope
  and one of: the admin flag, the `CampaignManager` role, a system client. A user with only
  the scope gets 403.
- **`/send` needs `messages:send` specifically.** The `messages` scope does not open it.
- **`EnableMediaLibrary = true` is separate from `MapMediaLibrary()`.** The first shows the
  UI, the second serves the API. Set both or neither.
- **Push is not optional once wired.** `UsePushNotificationServiceAzure()` needs
  `ConnectionStrings:PushNotificationsConnection` and a notification hub path. Remove the
  call if the solution has no push channel.
- **Resolved contacts are cached for 1 day by default** (`ContactRetainPeriodInDays`). A
  consent change in Identity is not seen by the worker until the period passes.

## Extension points

Add behaviour here, not by forking handlers or writing to the tables:

- `IContactResolver`, registered with `options.UseContactResolver<T>()` on both the API and
  the worker, when contacts live in a CRM or another system of record.
- `ICampaignJobHandler<TEvent>`: registered with `TryAdd`, so a host registration made
  before `AddMessageFunctions` / `AddMessageJobs` replaces the default handler for that event.
- `IEmailService`, `ISmsService`, `IPushNotificationService`: choose by configuration, or
  register your own implementation.
- `Partial` and `Layout` templates for shared content, managed in the UI.
- `UseMultiTenancy(accessLevel)` on the API options for tenant isolation.

## Do / Do not

- Do keep the API host and the worker as separate deployables that share `MessagesDb`, the
  storage account, the schema name and the environment name.
- Do pick one worker substrate per environment: Azure Functions or the in-process worker.
- Do keep secrets (`General:Api:Secrets:*`, provider keys, connection strings) in user
  secrets or a vault. The template's `appsettings.json` values are placeholders.
- Do not carry the template's placeholder senders, client secrets, authority URLs or
  `TestMode` values into a real environment. Do not send through a real provider from a
  development environment unless the recipients are yours.
- Do not reconfigure JSON, validation, auth or Problem Details for these endpoints. They
  come from `IndiceWebApplicationBuilder` (see the `indice-web-api` skill).
- Do not duplicate contact, consent or preference data in application tables. Resolve it.

## Read deeper

- Generated project: `Product.md` (capabilities and flows), `Templates.md` (template
  authoring with worked examples), `README.md` (Identity resources, migrations).
- `Indice.Platform/src/Indice.Features.Messages.AspNetCore/MessageFeatureExtensions.cs`:
  everything `AddMessaging` registers and every `Use*` option.
- `Indice.Platform/src/Indice.Features.Messages.Worker.Azure/HostBuilderExtensions.cs`,
  `QueueTriggers.cs`, `CronTriggers.cs`: the Functions worker.
- `Indice.Platform/src/Indice.Features.Messages.Worker/WorkerHostBuilderExtensions.cs`:
  the in-process worker.
- `Indice.Platform/src/Indice.Features.Messages.Core/Constants.cs`: scopes, policies,
  queue names, keyed-service names.
- `Indice.DotNet.Templates/src/Indice.Messaging` and `Indice.Messaging.Workers`: the
  template sources.
