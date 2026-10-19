---
name: indice-templates
description: >
  Use Indice.DotNet.Templates.Web to scaffold a new web project.
  The templates cover Identity (Razor Pages), Messaging (API, workers, full solution),
  Cases, Minimal API, REST API (MVC) and Azure Functions workers.
---

# Indice templates

Use this skill when creating a new Indice-based service. Scaffold from the template, then customize it.
Do not hand-write the host from scratch.

> Checked against `Indice.DotNet.Templates.Web` **8.53.0**
> (source: https://github.com/indice-co/Indice.DotNet.Templates).
> If the installed version is different, check short names and options with `dotnet new <short-name> --help`
> before relying on this file.

## Install, update and remove

```powershell
dotnet new install Indice.DotNet.Templates.Web          # install the latest version
dotnet new install Indice.DotNet.Templates.Web::8.53.0  # install a specific version
dotnet new update                                       # update installed template packages
dotnet new list indice                                  # confirm which templates are installed
dotnet new uninstall Indice.DotNet.Templates.Web        # remove the package
```

## Available templates

| Short name | Purpose | Main Indice packages | Template-specific options |
|---|---|---|---|
| `indice.identity.pages` | Identity server (IAM) with Razor Pages UI and Admin UI | `Indice.Features.Identity.Server`, `.UI`, `.AdminUI`, `Indice.Features.ActivityLogs`, `Indice.AspNetCore.Authentication.Apple`, `.GovGr` | `-F`, `-s`, `-ai`, `-aik`, `-ep`, `-he`, `-sp`, `-oa`, `-od`, `-on` |
| `indice.minimalapi` | ASP.NET Core Minimal API (Endpoints/Services) | `Indice.AspNetCore`, `Indice.AspNetCore.Builder` | `-F` |
| `indice.restapi.mvc` | ASP.NET Core MVC REST API (Controllers/Models/Services) | `Indice.AspNetCore.Builder` | `-F` |
| `indice.messaging` | Messaging (campaigns/messages) API and UI host | `Indice.Features.Messages.AspNetCore`, `.UI`, `Indice.Features.Media.AspNetCore` | `-F` |
| `indice.messaging.workers` | Azure Functions workers for Messaging | `Indice.Functions.Builder`, `Indice.Features.Messages.Worker.Azure` | `-F` (default **net9.0**) |
| `indice.messaging.Solution` | Messaging API plus worker as one solution | Both of the above | `-F`, `-in` |
| `indice.cases` | Cases (case management and workflows) host | `Indice.Features.Cases.Server`, `.UI`, `.Workflows` | `-F` |
| `indice.workers` | Generic Azure Functions worker host | `Indice.Functions.Builder` | `-F` |


### Template options

- `-F|--Framework` — `net8.0` | `net9.0` | `net10.0`. The default is `net10.0`, except for `indice.messaging.workers`, which defaults to `net9.0`. Always set `-F` explicitly to match the solution.
- `-in|--includeWorker` (`indice.messaging.Solution`) — bool, default `true`.
- Identity (`indice.identity.pages`) only:
  - `-s|--api-scope` — the API resource/scope to protect (default `api1`).
  - `-ai|--app-insights-disabled` — turns off Application Insights (default `false`).
  - `-aik|--app-insights-instrumentation-key` — the default is a placeholder. Never commit a real key; use configuration or secrets.
  - `-ep|--email-provider` — `"Razor SMTP"` (default) | `Sparkpost`.
  - `-he|--host-envirnoment` — `"Microsoft Azure"` (default) | `"On Premise"`. The misspelling is the option's real name.
  - `-sp|--sms-provider` — `"Yuboto Omni"` (default) | `Yuboto` | `Apifon`.
  - `-on|--organization-name`, `-od|--organization-domain`, `-oa|--organization-address` — always set these. The defaults are Indice's own values.

Common `dotnet new` options: `-n` (name; this replaces the template's source name in namespaces and project names), `-o` (output folder), `--dry-run` and `--force`.

## Workflow

1. Run `dotnet new list indice` to confirm the template is installed and check its version.
2. Pick the narrowest template that fits the need. Compose Indice features (IAM, Messaging, Cases) instead of reimplementing them.
3. Preview the output before generating anything:
   `dotnet new <short-name> -n <Company.Product.Service> -o src/<Company.Product.Service> -F net10.0 --dry-run`
4. Run the same command without `--dry-run`. Only use `--force` when the user has explicitly agreed to overwrite existing files.
5. Add the project to the solution: `dotnet sln add src/<Company.Product.Service>`.
6. Replace placeholders before committing. This includes organization values, instrumentation keys, connection strings, client secrets and signing settings. Keep secrets in user-secrets or Key Vault, not in `appsettings*.json`.
7. Verify: run `dotnet restore` and `dotnet build`, then start the host locally and check that it starts and that Swagger/UI endpoints respond.

## Examples

```powershell
dotnet new indice.identity.pages -n Contoso.Identity -o src/Contoso.Identity -F net10.0 -on Contoso -od contoso.com -oa "1 Main St, Athens" -s contoso-api -ep Sparkpost -sp Apifon
dotnet new indice.minimalapi -n Contoso.Orders.Api -o src/Contoso.Orders.Api -F net10.0
dotnet new indice.messaging.Solution -n Contoso.Messaging -o src/Contoso.Messaging -F net10.0 -in false
dotnet new indice.cases -n Contoso.Cases -o src/Contoso.Cases -F net10.0
```

## Rules

- Never invent template short names or options. If unsure, check `dotnet new <short-name> --help`.
- Keep the Indice package versions the template generates. Upgrade them together (all `Indice.*` packages at the same version), not one at a time.
- Projects generated with `indice.identity.pages` must follow the `indice-iam` skill. Generated APIs must follow the backend engineering rules and the `security-owasp` skill.
