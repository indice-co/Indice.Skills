# Indice Messaging reference

Lookup tables for `SKILL.md` and `setup.md`. Verified against `Indice.Platform` `8.57.x`.

## Registration entry points

| Call | On | Package | Does |
| --- | --- | --- | --- |
| `AddMessaging(Action<MessageEndpointOptions>)` | `IServiceCollection` | `Messages.AspNetCore` | management + inbox services, authorization policy, validators, `CampaignsDbContext`, translations |
| `AddMessageManagement(...)` / `AddMessageInbox(...)` | `IServiceCollection` | `Messages.AspNetCore` | either half on its own |
| `MapMessaging()` | `IEndpointRouteBuilder` | `Messages.AspNetCore` | `MapMessagingInbox()` + `MapMessagingManagement()` |
| `UseMessagesUI(Action<CampaignUIOptions>)` | `IApplicationBuilder` | `Messages.UI` | serves the embedded SPA |
| `AddMediaLibrary(...)` / `MapMediaLibrary()` | services / routes | `Media.AspNetCore` | media library API and `MediaDbContext` |
| `AddMessageFunctions(Action<MessageOptions>)` | `IHostApplicationBuilder` | `Messages.Worker.Azure` | Functions triggers and handlers (`ConfigureMessageFunctions` is the `IHostBuilder` form) |
| `AddMessageJobs(Action<MessageJobsOptions>)` | `WorkerHostBuilder` | `Messages.Worker` | the same handlers on `Indice.Hosting` |
| `UseEventDispatcherHosting()` | `MessageEndpointOptions` | `Messages.Worker` | API-side dispatcher for the in-process worker |

## API options (`MessageEndpointOptions`)

| Option | Default | Notes |
| --- | --- | --- |
| `PathPrefix` | `/` | the template sets `/api` |
| `RequiredScope` | `messages` | scope required by management endpoints |
| `DatabaseSchema` | `cmp` | must match the worker |
| `ConfigureDbContext` | SQL Server on `ConnectionStrings:MessagesDb` | the XML doc mentions `CampaignsDbConnection`; the code reads `MessagesDb` |
| `UserClaimType` | `sub` | the claim that becomes `RecipientId` |
| `ManagementGroupName` / `InboxGroupName` | `messages` / `my` | OpenAPI document names. The send API is always `send` |
| `FileUploadLimit` | 6 MB | campaign attachments |
| `MapTranslations` | `true` | maps `{prefix}/msg-i18n.{lang}.json` and `{prefix}/languages` |
| `AnalyticsOptions.Enabled` | `true` | event capture for the dashboard |

`Use*` methods on the API options: `UseFilesLocal`, `UseFilesAzure` (container
`messaging`), `UseEventDispatcherAzure`, `UseEventDispatcherAzureServiceBus`,
`UseEventDispatcherHosting`, `UseIdentityContactResolver`, `UseContactResolver<T>`,
`UseMediaLibrary`, `UseMultiTenancy(accessLevel)`.

Defaults when none is called: no-op event dispatcher, no-op file service, no-op contact
resolver.

## UI options (`CampaignUIOptions`)

| Option | Default |
| --- | --- |
| `ClientId` | `messaging-ui` |
| `Scope` | `offline_access messages media` (the SPA adds `openid profile role email phone`) |
| `ApiBase` | `/api` |
| `PathPrefix` | `/` (host root) |
| `Authority`, `Host` | none, set them |
| `DocumentTitle` | `Messaging UI` |
| `EnableMediaLibrary` | `false` |
| `MaxFileSize` | 10 MB |
| `AcceptableFileExtensions` | `.png, .jpg, .gif, .webp` (media uploads) |

These are injected into the SPA's `index.html` at request time, so one build serves every
environment.

## Worker options

Shared (`MessageWorkerOptions`):

| Option | Default |
| --- | --- |
| `ContactRetainPeriodInDays` | `1` |
| `DatabaseCleanUpOptions.Enabled` | `false` |
| `DatabaseCleanUpOptions.RetentionDaysForInbox` | `180` |
| `DatabaseCleanUpOptions.RetentionDaysForOther` | `120` |
| `DatabaseCleanUpOptions.DeletionBatchSize` | `10` |

Functions (`MessageOptions`): `ConfigureDbContext`, `DatabaseSchema` (`cmp`),
`CampaignStatisticOptions.Enabled` (`true`), `FunctionDisablePredicate` (Service Bus
triggers disabled by default; `WithServiceBusTriggers()` flips it).

In-process (`MessageJobsOptions`): `ConfigureDbContext`, `DatabaseSchema`,
`QueuePollingInterval` (300 ms), `QueueMaxPollingInterval` (5000 ms),
`DatabaseCleanUpCronExpression` (`0 0 2 * * ?`, Quartz), `Analytics.Enabled`.

`Use*` methods on the worker options: `UseEventDispatcherAzure`,
`UseEventDispatcherAzureServiceBus`, `WithServiceBusTriggers`, `UseFilesLocal`,
`UseFilesAzure`, `UsePushNotificationServiceAzure`, `UseEmailService` (by configuration)
or `UseEmailServiceSmtp|SparkPost|SendGrid|Brevo|WeMail`, `UseSmsService` (by
configuration) or `UseSmsServiceApifon|ApifonIM|YubotoOmni|YubotoOmniViber|Vonage|Twilio`,
`UseIdentityContactResolver`, `UseContactResolver<T>`.

## Configuration keys

| Key | Host | Purpose |
| --- | --- | --- |
| `ConnectionStrings:MessagesDb` | both | campaigns and media database |
| `ConnectionStrings:StorageConnection` | both | Storage Queues and blobs |
| `ConnectionStrings:ServiceBusConnection` | both | only with the Service Bus transport |
| `ConnectionStrings:PushNotificationsConnection` | worker | Azure Notification Hubs |
| `General:Authority` | both | Identity Server |
| `General:Host` | API | public URL of the host |
| `General:Api:ResourceName` | API | API resource name, `messages` |
| `General:Api:Secrets:Introspection` | API | API resource secret |
| `General:Api:Secrets:ClientId` / `ClientSecret` | both | contact resolver client |
| `Email:Provider` and provider settings | worker | email |
| `Sms:Provider` and provider settings | worker | SMS and Viber |
| `ENVIRONMENT` | worker (app setting) | queue name prefix |
| `MessageJobsOptions:DatabaseCleanUpCronExpression` | worker (app setting) | clean-up timer, NCRONTAB |
| `AzureWebJobsStorage`, `FUNCTIONS_WORKER_RUNTIME=dotnet-isolated` | worker (app setting) | Functions runtime |

## Providers

`Email:Provider`, exact case, comma-separated for several: `Smtp` (default when the key is
missing), `SparkPost`, `SendGrid`, `Brevo`, `AzureCommunicationServices`, `WeMail`, `None`.
An unknown value registers the no-op service, so a typo sends nothing and raises nothing.

`Sms:Provider`, case-insensitive, required: `yuboto` / `yuboto_omni`, `yuboto_viber`
(Viber), `apifon`, `apifon_im`, `twilio`, `vonage`, `smsup`, `kapatel`, `mstat`, `none`.

Push: Azure Notification Hubs only (APNS and FCM behind it).

Inbox: no provider, served from the database.

## Queues and events

Constants in `Indice.Features.Messages.Core.EventNames`. The physical queue is
`{environment}-{name}`, lower-case.

| Queue | Raised when | Handler |
| --- | --- | --- |
| `campaign-created` | a campaign is published | fan out to contacts, or broadcast push for a global campaign |
| `campaign-resolve-message` | per contact | resolve, render, persist the inbox message, pick channels |
| `campaign-send-email` | per contact with email allowed | email provider |
| `campaign-send-sms` | per contact with SMS allowed | SMS provider |
| `campaign-send-push-notification` | per contact with push allowed, or broadcast | Notification Hubs |
| `my-messages-mark-all-read` / `my-messages-mark-all-unread` | inbox bulk action | bulk update |
| `contacts-merge` | contacts merged in the UI | reassign lists, messages, events |

Timer: `MessagingDatabaseCleanUp`.

Storage Queue payloads are gzip-compressed envelopes. Service Bus payloads are not
compressed and the trigger functions carry a `servicebus-` name prefix.

Messaging registers its file service, push service and event dispatcher as keyed services
(`Messages:FileServiceKey`, `Messages:PushNotificationServiceKey`,
`Messages:EventDispatcherServiceKey`). Use the `Use*` methods, which target the right key.
A plain `AddFiles(...)` or `AddEventDispatcherAzure(...)` in the host does not replace them.

## Endpoints

`{p}` is `PathPrefix`. All use the `Bearer` scheme.

| Group | Routes | Authorization |
| --- | --- | --- |
| Inbox (`my`) | `GET {p}/my/messages`, `GET|DELETE {p}/my/messages/{messageId}`, `PUT …/{messageId}/read`, `PUT …/{messageId}/unread`, `PUT {p}/my/messages/all/read`, `PUT …/all/unread`, `GET {p}/messages/types`, `GET|PUT {p}/my/preferences` | any authenticated user; rows are scoped to the caller's `UserClaimType` |
| Attachments | `GET {p}/messages/attachments/{fileGuid}.{format}` | anonymous |
| Tracking | `GET {p}/_tracking/messages/cta/{trackingCode}` | anonymous; records the click, redirects to the action link |
| Management (`messages`) | `{p}/campaigns`, `{p}/contacts`, `{p}/distribution-lists` (with `/{distributionListId}/contacts`, `/{distributionListId}/import`, `/{distributionListId}/export`), `{p}/message-senders`, `{p}/message-types`, `{p}/templates` (with `/partials`), `{p}/analytics` | `RequiredScope` and campaign manager |
| Send (`send`) | `POST {p}/send` | scope `messages:send` |
| Translations | `GET {p}/msg-i18n.{lang}.json`, `GET {p}/languages` | |

`POST {p}/send` takes a `SendRequest`: a campaign creation request that is always
published. Recipients are given as `RecipientIds` (resolved through the contact resolver),
inline `Recipients` (anonymous contacts with email or phone), or `RecipientListId`.
`TypeId`, `RecipientListId` and `MessageTemplateId` accept a GUID or an alias. `Data` is
free JSON exposed to the template.

## Authorization

- Policy `BeCampaignManager` (`MessagesApi.Policies`): authenticated on `Bearer`, has
  `RequiredScope`, and is a system client, or has the admin flag, or has the
  `CampaignManager` role (`BasicRoleNames.CampaignManager`).
- With `UseMultiTenancy(accessLevel)` the same policy name requires tenant membership at
  that access level instead of the role.
- Send: the token must carry scope `messages:send`.
- Inbox: any authenticated user.

## Handlebars context

Both the title and the body of each channel are compiled. Email and inbox content is
HTML-encoded, SMS is plain text.

| Variable | Content |
| --- | --- |
| `id` | campaign id |
| `title` | campaign title |
| `type`, `classification` | message type name and classification |
| `actionLink.href`, `actionLink.text` | the CTA; `href` is the tracking URL, relative (`_tracking/messages/cta/…`) |
| `mediaBaseHref` | base URL for media library assets |
| `now` | UTC timestamp |
| `contact` | the resolved contact, camel-cased: `contact.firstName`, `lastName`, `fullName`, `email`, `phoneNumber`, `recipientId`, … |
| `data` | the campaign's `Data` JSON |

Composition: `{{> alias}}` includes a `Partial`; `{{#> alias}}…{{/alias}}` wraps content
in a `Layout`, which places it with `{{> @partial-block}}`. Partials inherit the caller's
context. A missing alias, or one with no content for the channel being rendered, renders
as empty rather than failing. The generated project's `Templates.md` has full examples.

## Enums worth knowing

- `MessageChannelKind` (flags): `None = 0`, `Inbox = 1`, `PushNotification = 2`,
  `Email = 4`, `SMS = 8`.
- `TemplateType`: `Full = 0`, `Partial = 1`, `Layout = 2`.
- `ContactChannelKind` (a contact's preference, flags): `Any = 0`, `Email = 1`, `SMS = 2`,
  `PushNotification = 4`.
