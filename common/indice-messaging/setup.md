# Setting up Indice Messaging in a new solution

Read `SKILL.md` first. This file is the procedure. Option defaults and key names are in
`reference.md`.

The target is two projects that share one database and one storage account:

| Project | Kind | Template |
| --- | --- | --- |
| `<Name>.Messaging` | ASP.NET Core host: management API, inbox API, send API, embedded UI, media library | `indice.messaging` |
| `<Name>.Messaging.Workers` | .NET isolated Azure Functions v4: queue and timer triggers that deliver | `indice.messaging.workers` |

An existing Indice Identity Server is assumed. Messaging authenticates against it and, in
the default setup, resolves contacts from it.

## 1. Generate the projects

```powershell
dotnet new install Indice.DotNet.Templates.Web   # once; `dotnet new list indice` to confirm
dotnet new indice.messaging         -n Acme.Messaging         -F net10.0
dotnet new indice.messaging.workers -n Acme.Messaging.Workers
# or both at once:
dotnet new indice.messaging.Solution -n Acme.Messaging -F net10.0
```

- `-n` replaces the `Indice.Messaging` name everywhere, namespaces included.
- `-F|--Framework` accepts `net8.0`, `net9.0`, `net10.0`. The API template defaults to
  `net10.0`. On `net8.0` the host uses Swashbuckle, on later frameworks built-in OpenAPI
  with Scalar.
- The workers template's `--Framework` switch is out of step with its project file at the
  time of writing. Open the generated `.csproj` and confirm `<TargetFramework>` is what you
  want, and that it matches the API project.
- The template generates a GUID into `General:Api:Secrets:Introspection`. That value must
  be registered as the API resource secret in Identity Server (step 3).
- Generate into the solution folder, then add both projects to the solution. Confirm every
  `Indice.*` package reference is on the same version as the rest of the solution.

Adding Messaging to a host that already exists is the same wiring without the template:
reference `Indice.Features.Messages.AspNetCore`, `Indice.Features.Messages.UI` and
`Indice.Features.Media.AspNetCore`, then apply step 2.

## 2. The API host

This is the template's `Program.cs`, trimmed to what matters.

```csharp
var builder = IndiceWebApplicationBuilder.CreateBuilder(args);

builder.AddApplicationLocalization();   // template-local extensions
builder.AddApplicationCache();
builder.AddApplicationOpenApi();

builder.Services.AddAvatars();
builder.Services.AddDatabaseDeveloperPageExceptionFilter();

builder.Services.AddMediaLibrary(options => {
    options.Scope = builder.Configuration.GetApiResourceName()!;
    options.PathPrefix = "/api";
    options.ConfigureDbContext = (serviceProvider, db) =>
        db.UseSqlServer(builder.Configuration.GetConnectionString("MessagesDb"), sql => {
            sql.MigrationsAssembly(typeof(MediaDbContext).Assembly.GetName().Name);
            sql.EnableRetryOnFailure();
        });
    options.UseFilesAzure();            // or UseFilesLocal() for development
});

builder.Services.AddMessaging(options => {
    options.ConfigureDbContext = (serviceProvider, db) =>
        db.UseSqlServer(builder.Configuration.GetConnectionString("MessagesDb"));
    options.RequiredScope = builder.Configuration.GetApiResourceName()!;   // "messages"
    options.PathPrefix = "/api";
    options.UseFilesAzure();            // attachments; or UseFilesLocal()
    options.UseEventDispatcherAzure();  // Storage Queues. Without a dispatcher nothing is enqueued
    options.UseIdentityContactResolver(resolver => {
        resolver.BaseAddress = new Uri(builder.Configuration.GetAuthority(tryInternal: true)!);
        resolver.ClientId = builder.Configuration.GetApiSecret("ClientId");
        resolver.ClientSecret = builder.Configuration.GetApiSecret("ClientSecret");
        resolver.ClaimsToResolve = [
            BasicClaimTypes.ConsentCommercialDate, BasicClaimTypes.ConsentCommercial,
            BasicClaimTypes.Locale, BasicClaimTypes.CommunicationPreferences
        ];
    });
});
builder.AddWebServiceDefaults();        // after the two feature registrations
builder.AddApplicationServices();
builder.AddExtraHealthChecks();         // Identity authority, MessagesDb, blob storage

var app = builder.Build();
app.UseOutputCache();
app.UseMessagesUI(options => {
    options.Authority = builder.Configuration.GetAuthority();
    options.Host = builder.Configuration.GetHost();
    options.EnableMediaLibrary = true;  // only together with MapMediaLibrary()
});
app.MapAvatars();
app.MapMediaLibrary();
app.MapMessaging();                     // inbox + tracking + management + send + translations
app.MapOpenApi();
app.MapHealthCheckDefaults();
app.Run();
```

Decisions to make here, not later:

- **Path prefix.** `/api` in the template. `UseMessagesUI`'s `ApiBase` defaults to `/api`
  too. If you change one, change the other, and use the same prefix for the media library.
- **Where the UI is served.** Host root by default. Set `options.PathPrefix` on
  `UseMessagesUI` to move it. The redirect URIs in step 3 follow it.
- **Only part of the surface.** A host that should expose just the end-user inbox uses
  `AddMessageInbox()` + `MapMessagingInbox()`. A back-office-only host uses
  `AddMessageManagement()` + `MapMessagingManagement()`. `AddMessaging()` is both.
- **Transport.** `UseEventDispatcherAzure()` (Storage Queues, connection string
  `StorageConnection`) or `UseEventDispatcherAzureServiceBus()` (connection string
  `ServiceBusConnection`). The worker must make the matching choice.
- **Contact source.** Identity as above, `options.UseContactResolver<T>()` for your own, or
  none if every campaign targets distribution-list contacts that already carry email and phone.

Configuration the API host needs (`appsettings.json` for shape, secrets elsewhere):

```jsonc
{
  "ConnectionStrings": {
    "MessagesDb": "…",                       // SQL Server
    "StorageConnection": "UseDevelopmentStorage=true"   // queues + blobs; Azurite locally
  },
  "General": {
    "Authority": "https://identity.example", // the Identity Server
    "Host": "https://messaging.example",     // this host's public URL
    "Api": {
      "ResourceName": "messages",            // API resource name = required scope
      "Secrets": {
        "Introspection": "<api resource secret>",
        "ClientId": "<contact resolver client id>",
        "ClientSecret": "<contact resolver client secret>"
      }
    }
  }
}
```

## 3. Identity Server registrations

Register these on the Identity Server that `General:Authority` points to. The names are
the package defaults. If you rename one, change the matching option.

| What | Value | Used by |
| --- | --- | --- |
| API resource | `messages`, secret = `General:Api:Secrets:Introspection` | token validation and introspection on the API host |
| Scopes on it | `messages` (management), `messages:send` (send API), `media` (requested by the UI) | |
| User claims on the resource | `sub`, `name`, `given_name`, `family_name`, `email`, `phone_number`, `role`, `admin` | authorization and audit fields |
| SPA client | `messaging-ui`, authorization code + PKCE, no secret | the management UI |
| Its scopes | `openid profile email phone role offline_access messages media` | |
| Its redirect URIs | `{Host}/auth-callback`, `{Host}/auth-renew`; post-logout `{Host}/logged-out`; CORS origin `{Host}` | with the UI path prefix inserted after `{Host}` if you set one |
| Service client | client credentials, scopes `identity identity:users`, allowed to read users | `UseIdentityContactResolver` on the API and on the worker |
| Sender clients | client credentials, scope `messages:send` | any system that calls `POST /api/send` |
| Role | `CampaignManager` (or the admin flag) on each operator | management endpoints |

The template uses `messages-worker` as the service client id for both hosts. One client
for both is fine. Its id and secret go in `General:Api:Secrets:ClientId` /
`ClientSecret` of each host.

## 4. The worker host

```csharp
var builder = FunctionsApplication.CreateBuilder(args);
builder.Services.AddWorkerServiceOpenTelemetry(builder.Environment);
builder.Services.AddFunctionHealthChecks();
builder.AddApplicationServices();       // template-local: cache, files, dispatcher
builder.Services.AddExtraHealthChecks(builder.Configuration);

builder.AddMessageFunctions(options => {
    options.UseEventDispatcherAzure()               // must match the API's transport
           .UsePushNotificationServiceAzure()       // remove if there is no push channel
           .UseFilesAzure()
           .UseEmailService(builder.Configuration)  // picks by Email:Provider
           .UseSmsService(builder.Configuration)    // picks by Sms:Provider (required)
           .UseIdentityContactResolver(resolver => {
               resolver.BaseAddress = new Uri(builder.Configuration.GetAuthority(tryInternal: true)!);
               resolver.ClientId = builder.Configuration.GetApiSecret("ClientId");
               resolver.ClientSecret = builder.Configuration.GetApiSecret("ClientSecret");
           });
    options.DatabaseCleanUpOptions.Enabled = true;
    options.DatabaseCleanUpOptions.RetentionDaysForInbox = 180;
    options.DatabaseCleanUpOptions.RetentionDaysForOther = 120;
});
builder.Build().Run();
```

For Service Bus: `options.UseEventDispatcherAzureServiceBus().WithServiceBusTriggers()`
here and `options.UseEventDispatcherAzureServiceBus()` on the API.

If the database schema is not `cmp`, or the store is not SQL Server on `MessagesDb`, set
`options.DatabaseSchema` / `options.ConfigureDbContext` here to the same values as the API.

Worker configuration:

```jsonc
// appsettings.json (copied to output; the template sets CopyToOutputDirectory)
{
  "ConnectionStrings": {
    "MessagesDb": "…",                         // same database as the API
    "StorageConnection": "UseDevelopmentStorage=true",   // same account as the API
    "PushNotificationsConnection": "…"         // only with push
  },
  "General": {
    "Authority": "https://identity.example",
    "Api": { "Secrets": { "ClientId": "…", "ClientSecret": "…" } }
  },
  "Email": { "Provider": "Smtp", "Sender": "…", "SenderName": "…", "SmtpHost": "…", "SmtpPort": 587, "UseSSL": true, "Username": "…", "Password": "…" },
  "Sms":   { "Provider": "none" }
}
```

```jsonc
// local.settings.json (local only, never published)
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet-isolated",
    "ENVIRONMENT": "Development",
    "MessageJobsOptions:DatabaseCleanUpCronExpression": "0 0 2 * * *"
  }
}
```

In a deployed Function App the last two are app settings. `ENVIRONMENT` must equal the API
host's environment name. The cron expression is NCRONTAB with six fields and must be
present even if clean-up is disabled. `host.json` in the template tunes the queue trigger
(`batchSize` 16, `maxDequeueCount` 5, `visibilityTimeout` 30s, `messageEncoding` base64).
Keep `messageEncoding` as generated: the dispatcher and the triggers agree on it.

To host the worker in Container Apps, the generated worker `README.md` has the container
properties to add to the `.csproj`. Check the base image tag matches the target framework.

### Alternative: no Azure, worker in-process

For a single-process deployment, skip the Functions project. Reference
`Indice.Features.Messages.Worker` in the API host and run the same handlers on
`Indice.Hosting`:

```csharp
builder.Services.AddMessaging(options => {
    // … as above, but:
    options.UseEventDispatcherHosting();          // instead of UseEventDispatcherAzure()
});
builder.Services.AddWorkerHost(options => options.UseStoreRelational<TaskDbContext>(db =>
            db.UseSqlServer(builder.Configuration.GetConnectionString("MessagesDb"))))
       .AddMessageJobs(options => {
           options.UseEmailService(builder.Configuration)
                  .UseSmsService(builder.Configuration);
           options.DatabaseCleanUpOptions.Enabled = true;
       });
```

Treat this block as a sketch and confirm the store and lock-manager calls against
`Indice.Hosting/WorkerHostConfiguration.cs`. The queue is then a database table, polling
defaults to 300 ms, and the clean-up cron is a Quartz expression (`0 0 2 * * ?`). Do not
also deploy the Functions worker for the same environment.

## 5. Database

- Both `CampaignsDbContext` (schema `cmp`) and `MediaDbContext` (schema `media`) live in
  the `MessagesDb` database.
- **Development:** the API host creates the database and tables on start. Use a database
  dedicated to Messaging: creation is skipped when the database already has tables.
- **Every other environment:** nothing is created. Add migrations to the host project:

```csharp
var migrationsAssembly = typeof(Program).Assembly.GetName().Name;
// inside AddMessaging:
options.ConfigureDbContext = (serviceProvider, db) =>
    db.UseSqlServer(builder.Configuration.GetConnectionString("MessagesDb"), sql => {
        sql.MigrationsAssembly(migrationsAssembly);
        sql.MigrationsHistoryTable($"__EFMigrationsHistory_{nameof(CampaignsDbContext)}");
        sql.EnableRetryOnFailure();
    });
// inside AddMediaLibrary: the same, with nameof(MediaDbContext)
```

```powershell
dotnet ef migrations add Initial --context CampaignsDbContext --project <host.csproj>
dotnet ef migrations add Initial --context MediaDbContext     --project <host.csproj>
dotnet ef database update --context CampaignsDbContext --project <host.csproj>
dotnet ef database update --context MediaDbContext     --project <host.csproj>
```

  The separate history tables are what let two contexts share one database. The generated
  `README.md` lists `migrations add` twice where it means `database update`.
- The worker never creates schema. It expects the tables to exist.

## 6. Run locally and smoke-test

1. Start Azurite (queues and blobs) and make sure SQL Server LocalDB or equivalent is up.
2. Run the Identity Server the hosts point to.
3. Run the API host, then the worker (`func start` or F5).
4. Open the API host URL. The UI redirects to Identity. Sign in as a user with the
   `CampaignManager` role.
5. Create a distribution list with one contact you own, create a campaign targeting it
   with the `Inbox` and `Email` channels, and publish.
6. Expect, in order: a message in `development-campaign-created`, the worker logging
   `campaign-created` then `campaign-resolve-message` then `campaign-send-email`, a row in
   `cmp` for the message, and the email arriving (or the SMS provider logging in
   `TestMode`).
7. Call `GET /api/my/messages` as the recipient to see the inbox copy.

If step 6 stalls, go through `## What bites` in `SKILL.md` top to bottom. The first three
entries cover almost every "published but not sent".

## 7. Before a real environment

- Secrets out of `appsettings.json`: introspection secret, client secret, provider keys,
  connection strings.
- Real sender identities per channel (Message senders in the UI, provider `Sender`).
- `Sms:TestMode` off only where real sends are intended.
- Migrations applied by the deployment, not by the host.
- `ENVIRONMENT` and `MessageJobsOptions__DatabaseCleanUpCronExpression` set on the worker.
- Retention values chosen deliberately: clean-up deletes campaigns and their messages
  older than `RetentionDaysForInbox` / `RetentionDaysForOther`.
- Dead-letter handling decided: after `maxDequeueCount` attempts a message moves to the
  `-poison` queue and nothing in the package reprocesses it.
