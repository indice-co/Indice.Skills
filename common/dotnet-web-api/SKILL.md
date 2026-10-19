---
name: dotnet-web-api
description: >
  Use when writing or reviewing ASP.NET Core HTTP endpoints at Indice, either in an
  Indice.Platform feature library or in a product API built on one: the
  Api/Handlers/Service split, routes, TypedResults, ResultSet paging, validation,
  endpoint filters, OpenAPI metadata, errors, request/response boundaries, and
  authorization. Prefer Indice.Platform primitives over new code.
---
# Web API conventions

## Purpose

Minimal APIs only, organised per resource, with Indice.Platform primitives doing the repetitive work. For generic ASP.NET Core guidance the pinned `dotnet/skills` `dotnet-webapi` baseline applies; this skill records where Indice differs or adds to it (see `## Relationship to dotnet-webapi`).

## Guardrail

Before writing a primitive (a validation filter, a paging wrapper, an exception-to-ProblemDetails mapper, a security-requirement helper), search Indice.Platform for it (see the `indice-platform` skill) and say what you checked. Most already exist and are listed below.

## Platform conventions are the standard

The conventions below apply everywhere: in a feature library and in a product API built on one. Product APIs legitimately differ in exactly two structural places:

* **Group prefix is a literal.** A feature library is mapped into someone else's host, so its prefix must be relocatable. A product API is the only consumer of its own routes, so a literal is correct.
* **Namespace is project-local.** Feature libraries declare route mappers in `namespace Microsoft.AspNetCore.Routing` so a consuming host gets `routes.MapX()` without a using. A product API mapping its own routes does not need it.

A product's own fine-grained authorization model is fine where Platform has no equivalent.

Everything else that differs is drift, not a second convention (see `## Known drift in product APIs`). "The file next to it does X" is not by itself a justification for X.

## Anatomy of an endpoint

Per route group:

* `<Resource>Api.cs` declares the route group and the `Map*` calls, nothing else. `internal static class`; in a feature library, declared in `namespace Microsoft.AspNetCore.Routing`.
* `<Resource>Handlers.cs` is an `internal static class` of thin handler methods that call the service and translate its result to a response. No business logic, LINQ, or `DbContext` in handlers.
* `I<Something>Service` owns the logic, **one per route group**, not one per entity. The same entity served to two audiences gets two services (Cases: `IAdminCaseService` for the back-office group, `IMyCaseService` for the current-user one).
* `<Request>Validator.cs`, one per request type, in its own file under `Validators/` (or `<Area>/Validation/`).

Never inline a lambda into a `MapGet`/`MapPost`; the route declaration always names a method.

> **Do not copy the older Identity handlers.** Some inject a `DbContext` straight into the handler and run LINQ there. Follow Messages, Cases, or Agents instead.

## Routes and naming

* Kebab-case, plural nouns (`distribution-lists`, `payment-methods`). `my/` prefixes a current-user resource, `manage/` a back-office one (`manage/cases`).
* Sub-resources nest under the parent id (`{caseId}/attachments/{attachmentId}`). Non-CRUD actions are a verb segment (`{userId}/block`, `{campaignId}/publish`).
* Route parameters are always `{<entity>Id}`, never a bare `{id}`, including in `CreatedAtRoute` route values. Leave the type off the route (`{caseId}`, not `{caseId:guid}`); add a constraint only where the handler does not type the parameter.
* Do not expose table names or internal structure in routes. Follow the repository's existing versioning scheme; do not introduce one in passing.

```csharp
// Feature library: never a literal, the host must be able to relocate it.
var options = routes.ServiceProvider.GetRequiredService<IOptions<MessageManagementOptions>>().Value;
var group = routes.MapGroup(options.PathPrefix.TrimEnd('/') + "/distribution-lists");

// Product API: a literal is correct. Do not invent IOptions plumbing for one consumer.
var group = builder.MapGroup("manage/invoices");
```

Each area gets an aggregator that composes the group mappers in order (`MapCases()`, `MapMessaging()`). The host calls the aggregator, never the individual mappers.

## HTTP methods

* `GET` is read-only. `POST` creates or runs a command (verb segment). `PUT` replaces the full representation. `PATCH` only where partial update is explicitly supported and validated.
* `DELETE` only where deletion is allowed. When records must be kept, use an explicit command (`{orderId}/cancel`) instead.

## Requests and responses

* Accept and return API models, never EF entities, persistence models, provider SDK models, raw callback payloads, or exception types. Project in the service.
* Request models contain only client-supplied fields. Never accept server-owned values (status, owner or tenant, audit fields, calculated amounts); resolve or compute them server-side. No over-posting.
* Once generated clients consume a contract, change it only in backward-compatible ways; renames and removals are breaking.

## Return types

**`TypedResults` only.** Not `Results.Ok(...)`, not `IResult`, not `IActionResult`. No controllers.

Annotate multi-outcome handlers with an explicit union:

```csharp
Task<Results<NoContent, NotFound, ValidationProblem>>
Task<Results<NoContent, NotFound>>
Task<Results<Ok<T>, NotFound>>
```

Created responses use the route name, never a hand-built URL: `TypedResults.CreatedAtRoute(list, nameof(GetDistributionListById), new { distributionListId = list.Id })`.

## Lists

`ResultSet<T>` (`{ Count, Items }`) is the default for any collection that can grow, **including a sub-collection of one parent**. Bind `[AsParameters] ListOptions` (and `[AsParameters]` filters, combined with `ListOptions.Create(options, filter)`), and page with `ToResultSetAsync` in the service.

A plain `List<T>` is only for sets fixed by definition (a settings list, an enum-like lookup). If in doubt, page it. Never return an unpaged `List<T>` from something searched or filtered.

```csharp
public static async Task<Ok<ResultSet<DistributionList>>> GetDistributionLists(
    IDistributionListService distributionListService,
    [AsParameters] ListOptions options,
    [AsParameters] DistributionListFilter filter) {
    var lists = await distributionListService.GetList(options, filter);
    return TypedResults.Ok(lists);
}
```

Paging safety, enforced in the service:

* `ListOptions.Size` has no maximum. Clamp it.
* `Sort` and `FilterClause` member paths are translated into expressions as-is. Allow-list them, and map API names to entity paths with `AddSortRedirect`. Never bind arbitrary client field names into queries.
* Define a stable default sort. Project before paging. Never return all rows for client-side filtering.

## Group and endpoint metadata

The OpenAPI document generated from this metadata is what NSwag turns into TypeScript clients, so missing metadata ships as a broken client.

On the group: `.WithGroupName(...)`, `.WithTags(...)`, `.RequireAuthorization(...)`, `.WithOpenApiSecurityRequirement("oauth2", allowedScopes)`, and the `.ProducesProblem(...)` codes every endpoint in it can return (401/403/500).

On each endpoint:

* `.WithName(nameof(Handlers.TheMethod))`, always `nameof`. This is what makes `CreatedAtRoute` safe.
* `.WithSummary("...")` on every endpoint; `.WithDescription(...)` where a longer description exists.
* `.Produces<T>(...)` only for responses the signature cannot express (file downloads, alternate content types).

## Validation

Server-side validation is the source of truth; UI validation is convenience. Never trust client-provided calculations or flags.

* `.WithParameterValidation<TRequest>()` on the endpoint. It adds the filter **and** registers `ProducesResponseType(400, HttpValidationProblemDetails)`; do not add that yourself.
* FluentValidation is the standard: `public class <Request>Validator : AbstractValidator<TRequest>`, registered with `services.AddEndpointParameterFluentValidation(typeof(X).Assembly)`.
* The filter falls back to DataAnnotations (MiniValidator) when no validator is registered. Check which mechanism a request already uses. Do not stack both: annotations silently stop running once a validator resolves.

## Endpoint filters

Never call `AddEndpointFilter` directly. Wrap the filter in a `With*` convention extension that also registers the response metadata it produces, as `WithParameterValidation<T>`, `WithHandledException<TException>`, `WithOpenApiSecurityRequirement(...)`, and `LimitUpload(...)` do. A raw `.AddEndpointFilter<T>()` is why some groups carry a hand-written `.ProducesProblem(...)` list that drifts out of sync.

## Errors

Services throw `BusinessException(message, code, errors)`. The group declares `.WithHandledException<BusinessException>()`, which converts it to a `400` `ValidationProblem` carrying `extensions["code"]`. Handlers do not try/catch.

```csharp
group.WithHandledException<BusinessException>()
     .ProducesProblem(StatusCodes.Status401Unauthorized)
     .ProducesProblem(StatusCodes.Status500InternalServerError);
```

* Missing resources return `TypedResults.NotFound()` through the handler's union.
* `BusinessException` always maps to `400`. For a state or concurrency conflict that must be `409`, return `Conflict` in the union or throw a dedicated exception type handled with `WithHandledException<TException>(StatusCodes.Status409Conflict)`.
* Never leak secrets, raw provider errors, exception details, or PII. Where revealing that a record exists is unsafe, return `404` rather than `403`.

> **Do not mix this into a group that does not have it.** A `BusinessException` in a group without `.WithHandledException<BusinessException>()` reaches the host exception handler, and the client gets a `500` with no error code. Convert a whole group or leave it alone.

## Authorization

* Authorize server-side on the group with `.RequireAuthorization(...)`; chain a second `.RequireAuthorization(...)` on an endpoint to tighten it. Use Indice IAM scopes and policies (see the `indice-iam` skill).
* Check resource ownership in the service and reject direct-object-reference attempts.
* In multi-tenant systems, resolve tenant and user scope from the authenticated context, never from client input.
* Hidden or disabled UI is not authorization; the endpoint always authorizes the submitted action.

## Retries and callbacks

Apply when the operation has side effects and the client or a provider can retry it.

* Require an idempotency key. Return the same outcome for a duplicate equivalent request; reject a reused key with a different payload.
* Treat external callbacks and webhooks as hostile until verified: signature check, plus timestamp or replay protection where the provider supports it. Keep provider models in infrastructure (see the `regulated-integrations` skill).

## Host defaults

`IndiceWebApplicationBuilder.CreateBuilder(args)` calls `AddMinimalApiDefaults()`: camelCase JSON with the Indice converters, `JsonStringEnumConverter`, ProblemDetails with `requestId`/`traceId`, JWT and introspection auth, CORS, localization, and the FluentValidation scan of the entry assembly. `AddWebServiceDefaults()` adds OpenTelemetry, health checks, and HTTP resilience.

Do not reconfigure any of that inside a feature library or a per-feature extension. A feature that needs different JSON behaviour is a conversation about the default, not a local override.

## Known drift in product APIs

Shapes found in product repos that contradict the rules above. Write new code the Platform way; where a row says a change cannot be made piecemeal, leave existing code alone rather than half-converting it.

| You will see                                                                                                                                           | Follow instead                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Routes and handlers in one`<Feature>Endpoints.cs`, sometimes over a thousand lines                                                                   | Split into`<Resource>Api.cs` + `<Resource>Handlers.cs` + service. For a **new resource or file**, always split. For **one endpoint added to an existing single-file group**, match the file and note in the PR that it is a split candidate. |
| Services returning a result object (`Success`, `ErrorCode`, `ErrorMessage`) unpacked by hand and mapped through a custom problem-details factory | `BusinessException` + `.WithHandledException<BusinessException>()`. Convert a whole group or none (see `## Errors`).                                                                                                                                   |
| `.AddEndpointFilter<SomeFilter>()` directly on a group                                                                                               | A`With*` extension that also registers the filter's status codes.                                                                                                                                                                                          |
| `List<T>` from a collection that can grow, including a child collection                                                                              | `ResultSet<T>` with `ListOptions`. Safe to fix, but breaking for generated clients, so flag it.                                                                                                                                                          |
| DataAnnotations on the request instead of a validator class                                                                                            | FluentValidation for new validation. Do not stack both; if you change mechanism, remove the other.                                                                                                                                                           |
| Back-office groups under`admin/`, or bare `{id}` parameters                                                                                        | `manage/` and `{<entity>Id}` for new groups and routes. Renaming existing routes breaks clients; leave them.                                                                                                                                             |
| Endpoints without`.WithSummary(...)`                                                                                                                 | Add it. It lands in the generated client.                                                                                                                                                                                                                    |

## Relationship to `dotnet-webapi`

`dotnet/skills`' `dotnet-webapi` is the assumed baseline. Where it conflicts with the table below, this skill wins.

| `dotnet-webapi` says                                                       | At Indice                                                                                  |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `CancellationToken` on every endpoint                                      | Only where it is actually forwarded downstream                                             |
| `TypedResults.Created($"/api/x/{id}", ...)`                                | `TypedResults.CreatedAtRoute(model, nameof(GetEntityById), new { entityId = model.Id })` |
| A`.http` file per project                                                  | Not an Indice practice                                                                     |
| Fall back to untyped`Results` past ~7 branches                             | Never. Annotate the union or split the endpoint                                            |
| `{Entity}ListResponse` for collections                                     | `ResultSet<T>` of the API model                                                          |
| One static class per resource with`Map<Resource>(this WebApplication app)` | Extension on`IEndpointRouteBuilder`, routes split from handlers across two files         |

## Records

Use records for new data-carrying types: request and response models, events, commands, service results. Positional records where the type is small (`public record CreateFolderResponse(Guid FolderId);`). Most existing Platform DTOs are classes for historical reasons; do not copy that shape into new code, and do not convert an existing class to a record in passing (it changes equality semantics).

## Do / Do not

* **Do** name the endpoint `nameof(TheHandler)` and let `CreatedAtRoute` use it.
* **Do** put the `.ProducesProblem(...)` codes on the group, once.
* **Do** check which validation mechanism a request already uses before adding one.
* **Do** clamp page size and allow-list sort and filter fields.
* **Do not** inline a lambda into a route declaration.
* **Do not** put business logic, LINQ, or a `DbContext` in a handler.
* **Do not** return `IResult`, `IActionResult`, untyped `Results.*`, or EF entities.
* **Do not** hardcode a group prefix in a feature library, or plumb an `IOptions` prefix through a product API with no second consumer.
* **Do not** reconfigure JSON, auth, CORS, or ProblemDetails inside a feature.
* **Do not** log secrets, tokens, or unnecessary PII.
* **Do not** treat a pattern as correct because the file next to it does it; check `## Known drift in product APIs` first.

## Examples

The reference implementation is Messages' distribution lists in Indice.Platform: `Endpoints/DistributionListsApi.cs` (the surface) and `Endpoints/DistributionListsHandlers.cs` (thin handlers over `IDistributionListService`). `Indice.Features.Cases.Server`'s `AdminAccessRulesApi.cs` shows per-endpoint authorization overrides on a group policy. Prefer these over a file in a product repo when you need a model to copy.
