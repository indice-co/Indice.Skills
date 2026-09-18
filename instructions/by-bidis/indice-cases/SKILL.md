---
name: indice-cases
description: >
  Use when a task touches Indice Cases or workflows: hosting the Cases server,
  UI, and workflow designer, case types, checkpoints, access rules, workflow
  definitions, custom activities, extension endpoints, or the Cases IAM and
  database setup. Defines the host boundary, what the package owns, and what
  must never be copied from reference projects.
---

# Indice Cases and workflows

## Boundary

Cases and workflow are a platform capability, not logic buried inside a regulated business module. Adopting them is an explicit, approved decision that must resolve: workflow designer access, case-management API and UI, workflow definitions, the actor model, evidence, callbacks, SLA, retention, and operational ownership. Until that decision exists, do not introduce a Cases host, case types, workflow definitions, workflow-driven maker-checker, or workflow-driven regulated decisions.

Indice packages own core Cases persistence, APIs, UI assets, workflow runtime, and generated workflow infrastructure. The application owns thin adapters, approved extension endpoints, and module contracts.

## Host composition

A standalone ASP.NET Core host composes `Indice.Features.Cases.Server`, `Indice.Features.Cases.UI`, and `Indice.Features.Cases.Workflows`. The `indice.cases` template is the baseline (`dotnet new indice.cases -n <Scratch> --Framework net10.0`, generated into a scratch location, never over existing source).

Template shape:

1. `IndiceWebApplicationBuilder.CreateBuilder(args)`, then `AddApplicationLocalization`, `AddApplicationCache`, `AddApplicationOpenApi`.
2. `AddWebServiceDefaults()` before the Cases calls.
3. `AddCaseServer(options => options.PathPrefix = "/api")` owns the Cases API surface.
4. `AddCasesWorkflow` with `RegisterAuthentication = true`; SMTP binds from `Elsa:Smtp`; workflow assembly loading is an explicit opt-in.
5. Application services and extra health checks after the product calls.
6. Runtime: `UseCasesWorkflow()`, `UseCasesUI()`, `MapCases()`, OpenAPI, `MapHealthCheckDefaults()`, then local extension endpoints.

Workflow UI client, required scope, group claim type, authority, host, language, and SMTP are host options, not scattered through feature code. Health checks cover the IAM authority, `CasesDb`, and blob storage when `StorageConnection` is configured.

Keep application wrappers small and configuration-driven. Prefer package composition and explicit options over copying provider internals.

## IAM contract

The template's IAM shape: API scope `cases`; admin UI and workflow designer client `cases-ui` using authorization code flow; identity resources `openid`, `profile`, `email`, `role`, `cases`, `offline_access`; claims on the `cases` scope: `role`, `email`, `name`, `sub`, `given_name`, `family_name`.

Treat these as the template's shape only. Your client IDs, scopes, role names, claims, actor mappings, and designer access come from your own approved IAM security contract (see the `indice-iam` skill).

## Database and migrations

* `CasesDb` backs the Cases provider store.
* The workflow (Elsa) store key appears as `WorkflowDb` in generated `appsettings.json` and `WorkflowDB` in the README. Match the key the generated host and package option actually use.
* Migration snippets set the migrations assembly to the host assembly and use separate EF migrations history tables for `CasesDbContext` and `ElsaContext`.
* Provider-owned Cases and workflow migrations are allowed inside the Cases host boundary. Application-owned regulated schemas still need their own migration review.

## Localization

`AddCaseServer(...)` registers the Cases translation graph and `MapCases(...)` maps translation endpoints: `GET {prefix}/cases-i18n.{lang}.json` and `GET {prefix}/languages`, excluded from OpenAPI and output-cached. The template supports `en` and `el` with `el` as default culture. Non-standard hosts must configure localization resources (`Resources`) before relying on Cases i18n. Override translations through package-supported resource registration, never by copying Angular assets.

## Authorization

* Route groups require authenticated bearer tokens and approved scopes.
* Administrative extension routes add `RequireCasesAccess(CasesAccessLevel.Manage)`.
* Customer-facing case routes add ownership checks such as `RequireCasesOwnershipAccess`.
* Operational searches may add role or system-client assertions on top of scope checks.
* UI visibility and route guards are never sufficient. Server-side Cases authorization is required. Extra rules go through `AddCaseAuthorizationService<T>`.

## Extension endpoints

Typical thin endpoints around Cases: draft case creation that updates case data and applies access rules; submission and assignment helpers; checkpoint-type and access-rule lookup; current-assignee declaration; customer-owned case list, create, update, submit, attachment, and request-list; external workflow callback and cancel.

Extension endpoints are integration contracts. Each needs explicit DTOs, ProblemDetails, OpenAPI summaries, cancellation tokens, tenant scoping where relevant, server-side authorization, audit expectations, and tests.

## Generated clients and adapters

Keep generated clients under proxy folders (for example `Proxies/Identity`, `Proxies/Cases`) and consume them behind handwritten services or workflow activities. Machine-to-machine calls use client-credentials token management; named `HttpClient` registrations isolate base addresses. Never expose generated or provider models as application domain contracts. Fail closed when a required endpoint, authority, client ID, client secret, or scope is missing.

## Case types, seeds, and workflow definitions

Reference pattern: an `IDbCaseTypeSeed` interface standardizes case type metadata, allowed creator roles, checkpoint types, schema, layout, translations, tags, and config; a hosted seeder discovers seed classes and upserts provider-owned case types and checkpoint metadata; workflow JSON files carry the business journeys, timers, HTTP endpoints, cancellation paths, notifications, checkpoint submissions, and JavaScript or Liquid expressions; deployment uses manual export, import, and publish steps.

Rules:

* Case types, workflow definitions, checkpoint states, timers, notifications, and access rules are product behaviour. Never copy or adapt them from a reference.
* If seeding is adopted, make it deterministic, environment-safe, auditable, and backed by migration and review notes.
* Workflow definition deployment needs explicit promotion, import/export, publication, rollback, and evidence rules. Treat workflows as auditable product artifacts, not just code. Keep definitions and case types out of source until they are approved, versioned, promotable, and testable.

## Custom activities

Typical activities: an HTTP request activity using named clients and designer inputs; role-assignment validation; notifications to access-rule users and groups.

Activities are executable business and integration logic and must be approved. Named clients, allowed relative URLs, headers, body handling, retry behaviour, failure outcomes, and logging redaction need explicit governance. Activities that call application modules use approved contracts and never reach into another module's internals.

## Operations

Reference hosts use health checks for SQL, the OpenID Connect authority, and blob storage; a Redis cache package; the Azure event dispatcher; a no-op email service; container and CI metadata; and SQL bootstrap material for provider-owned workflow storage. Production providers, storage, event dispatch, SMTP and notification channels, and worker operations require approved security and operations inputs. No checked-in connection strings, secrets, registry names, or production endpoints.

## Do not copy

From any reference project: case types, checkpoint codes, workflow JSON, timers, role names, claims, scopes, client IDs, route taxonomy, customer journeys, notifications, callback semantics, cancellation behaviour, legal or product copy, access-rule defaults; generated API contracts as public contracts; SQL scripts, provider database names, registry and pipeline values, endpoint URLs, client secrets, certificate guidance, runbook values; any workflow-driven regulated decision behaviour.
