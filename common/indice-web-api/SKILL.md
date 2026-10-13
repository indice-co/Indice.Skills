---
name: indice-web-api
description: >
  Use when writing or reviewing HTTP endpoints at Indice either in an Indice.Platform
  feature library or in a product API built on one. Covers the Api/Handlers/Service
  split, route groups, TypedResults, ResultSet paging, validation, endpoint filters,
  OpenAPI metadata, and error handling. Prefer Indice.Platform primitives over new code.
---

# Indice web API conventions

## Purpose

How we build HTTP endpoints: minimal APIs only, organised per resource, with the
Indice.Platform primitives doing the repetitive work. For generic ASP.NET Core Web API
guidance the pinned `dotnet/skills` `dotnet-webapi` baseline applies. This skill only
records where Indice differs or adds to it. See `## Relationship to dotnet-webapi`,
which lists the cases where we override it.

## Guardrail

Before writing a primitive (a validation filter, a paging wrapper, an exception-to-
ProblemDetails mapper, a security-requirement helper) search Indice.Platform for it
(see the `indice-platform` skill) and say what you checked. Most of them already exist
and are listed below.

## Indice.Platform is the reference

**The conventions below are the Platform conventions, and they are the standard
everywhere: in a feature library and in a product API built on one.** Write new code this
way by default.

Product APIs deviate legitimately in exactly two places, both structural:

- **Group prefix is a literal.** A feature library is mapped into someone else's host, so
  its prefix must be relocatable. A product API is the only consumer of its own routes and
  a literal is correct.
- **Namespace is project-local.** The `Microsoft.AspNetCore.Routing` trick exists so a
  consuming host gets `routes.MapX()` without a using. A product API mapping its own
  routes does not need it.

A product's own authorization model is also fine. Where a product has a fine-grained
permission scheme that Platform has no equivalent for, keep using it. Nothing here
replaces it.

**Everything else that differs is drift, not a second convention.** See
does X" is not by itself a justification for X. `## Known drift in product APIs` says when
to match existing code anyway and when to fix it.

## Anatomy of an endpoint

Per route group:

- `<Resource>Api.cs` declares the route group and the `Map*` calls, nothing else. It should
  read as a description of the surface. `internal static class`, and in a feature library
  declared in `namespace Microsoft.AspNetCore.Routing`.
- `<Resource>Handlers.cs` is an `internal static class` of thin handler methods.
- `I<Something>Service` owns the logic, **one per route group**, not one per entity. The
  same entity served to two audiences gets two services: Cases has `IAdminCaseService` for
  the back-office group and `IMyCaseService` for the current-user one. Handlers call it and
  translate the result to a response. They hold no business logic.
- `<Request>Validator.cs`, one per request type, in its own file under `Validators/` (or
  `<Area>/Validation/`). See `## Validation`. Messages keeps
  `CreateDistributionListRequestValidator` beside the service it guards.

Never inline a lambda into a `MapGet`/`MapPost`. The route declaration names a method,
always.

> **Do not copy the older Identity handlers.** Some of them inject a `DbContext` straight
> into the handler and run LINQ there. They are the largest handler files in Platform, so
> they surface first when you grep for examples. Follow Messages/Cases/Agents instead.

## Routes and naming

Kebab-case, plural nouns (`distribution-lists`, `payment-methods`). `my/` prefixes a
current-user resource, `manage/` a back-office one (`manage/cases`, `manage/case-types`). Sub-resources nest under the parent id
(`{caseId}/attachments/{attachmentId}`). Non-CRUD actions are a verb segment
(`{userId}/block`, `{campaignId}/publish`).

**Route parameters are always `{<entity>Id}`**, never a bare `{id}`: `{caseId}`,
`{distributionListId}`, `{userId}`. The name must say what it identifies, including in
`CreatedAtRoute` route values (`new { caseId = model.Id }`). Leave the type off the route
(`{caseId}`, not `{caseId:guid}`): the handler parameter already declares it. Add a
constraint only where the handler does not type the parameter explicitly.

```csharp
// Feature library: never a literal, the host must be able to relocate it.
var options = routes.ServiceProvider.GetRequiredService<IOptions<MessageManagementOptions>>().Value;
var group = routes.MapGroup(options.PathPrefix.TrimEnd('/') + "/distribution-lists");

// Product API: a literal is correct. Do not invent IOptions plumbing for one consumer.
var group = builder.MapGroup("manage/invoices");
```

Each area gets an aggregator that composes the group mappers in order
(`MapCases()`, `MapMessaging()`, `ManagementApiExtensions.MapManagementApi()`). The host
calls the aggregator, never the individual mappers.

## Return types

**`TypedResults` only.** Not `Results.Ok(...)`, not `IResult`, not `IActionResult`. We do
not build HTTP APIs with controllers. If you are adding one, you are in the wrong pattern.

Annotate multi-outcome handlers with an explicit union. The three shapes that cover most
mutations:

```csharp
Task<Results<NoContent, NotFound, ValidationProblem>>
Task<Results<NoContent, NotFound>>
Task<Results<Ok<T>, NotFound>>
```

Created responses use the route name, never a hand-built URL:
`TypedResults.CreatedAtRoute(list, nameof(GetDistributionListById), new { distributionListId = list.Id })`.

**Collections.** `ResultSet<T>` (`{ Count, Items }`) is the default. Bind
`[AsParameters] ListOptions` and return `ResultSet<T>` for any collection that can grow,
**including a sub-collection of one parent**. Being a child of something does not make a
set small. `GET {distributionListId}/contacts` in Messages is the shape: it binds
`ListOptions` and returns `Ok<ResultSet<Contact>>`.

A plain `List<T>` is the narrow exception: a set that is fixed by definition and cannot
grow with data, such as a settings list, an enum-like lookup, or the reject reasons
configured for one case type. If you are weighing it up, page it. The cost of paging a
short list is one wrapper; the cost of not paging a long one is an endpoint that degrades
silently as data arrives.

Never return an unpaged `List<T>` from something searched or filtered.

```csharp
public static async Task<Ok<ResultSet<DistributionList>>> GetDistributionLists(
    IDistributionListService distributionListService,
    [AsParameters] ListOptions options,
    [AsParameters] DistributionListFilter filter) {
    var lists = await distributionListService.GetList(options, filter);
    return TypedResults.Ok(lists);
}
```

Bind paging and filters with `[AsParameters]`, and combine them with
`ListOptions.Create(options, filter)`.

## Group and endpoint metadata

This is not cosmetic. The OpenAPI document generated from it is what NSwag turns into the
TypeScript clients, so missing metadata ships as a broken client.

On the group: `.WithGroupName(...)` (selects the OpenAPI document), `.WithTags(...)`,
`.RequireAuthorization(...)`, `.WithOpenApiSecurityRequirement("oauth2", allowedScopes)`,
and the `.ProducesProblem(...)` codes every endpoint in it can return (401/403/500).

On each endpoint:

- `.WithName(nameof(Handlers.TheMethod))`, always `nameof`, never a string literal. This is
  what makes `CreatedAtRoute` safe.
- `.WithSummary("...")` on every endpoint.
- `.WithDescription(...)` optionally, where a longer `XXX_DESCRIPTION` const exists.
- `.Produces<T>(...)` only for responses the signature cannot express (file downloads,
  alternate content types).

Chain a second `.RequireAuthorization(...)` on a `MapX` call to tighten authorization for
one endpoint. It composes with the group policy.

## Validation

`.WithParameterValidation<TRequest>()` on the endpoint. It adds the filter **and** registers
`ProducesResponseType(400, HttpValidationProblemDetails)`, so do not add that yourself.

FluentValidation is the standard:
`public class <Request>Validator : AbstractValidator<TRequest>` in its own file under
`Validators/` or `<Area>/Validation/`, picked up by
`services.AddEndpointParameterFluentValidation(typeof(X).Assembly)`.

The filter resolves `IValidator<TRequest>` and **falls back to DataAnnotations via
MiniValidator when no validator is registered** (`EndpointParameterFluentValidator`). This
is why `.WithParameterValidation<T>()` appears to work in projects that have no validator
classes: the annotations on the DTO are doing it. Know which mechanism a request already
uses before you add anything. **Stacking a FluentValidation validator on a DTO that already
carries DataAnnotations gives one request two validation layers**, and the annotations
silently stop running as soon as the validator resolves.

## Endpoint filters

Never call `AddEndpointFilter` directly. Wrap the filter in a convention extension that
also registers the response metadata it produces. That coupling is the rule, and it is why
`WithParameterValidation` and `WithHandledException` both add a `ProducesResponseType`
alongside their filter. The ones that already exist: `WithParameterValidation<T>`,
`WithHandledException<TException>`, `WithOpenApiSecurityRequirement(...)` and
`LimitUpload(...)`. For upload specifics see the `minimal-api-file-upload` skill.

When you write a new filter, give it a `With*` extension and register its status codes
there. A raw `.AddEndpointFilter<T>()` on a group is why some product groups carry a long
hand-written list of `.ProducesProblem(...)` calls that drifts out of sync with the filters.

## Errors

Services throw `BusinessException(message, code, errors)`. The group declares
`.WithHandledException<BusinessException>()`, which converts it to a `ValidationProblem`
carrying `extensions["code"]`. Handlers do not try/catch.

```csharp
group.WithHandledException<BusinessException>()
     .ProducesProblem(StatusCodes.Status401Unauthorized)
     .ProducesProblem(StatusCodes.Status500InternalServerError);
```

> **Do not mix this into a group that does not have it.** A `BusinessException` thrown in a
> group without `.WithHandledException<BusinessException>()` is caught by nothing. It
> reaches the host exception handler and the client gets a 500 with no error code instead
> of a 400. Converting a group is all-or-nothing: add the group convention and move every
> handler in it together, or leave the group alone.

## Host defaults

`IndiceWebApplicationBuilder.CreateBuilder(args)` calls `AddMinimalApiDefaults()` for you:
camelCase JSON with the Indice converters, `JsonStringEnumConverter`, ProblemDetails with
`requestId`/`traceId`, JWT and introspection auth, CORS, localization, and the
FluentValidation scan of the entry assembly. `AddWebServiceDefaults()` adds OpenTelemetry,
health checks and HTTP resilience.

Do not reconfigure any of that inside a feature library or a per-feature extension. If a
feature needs different JSON behaviour, that is a conversation about the default, not a
local override.

## Known drift in product APIs

Patterns you will find in product repos that contradict the rules above. They are not a
product-API dialect, there is no structural reason for any of them. **Write new code the
Platform way.** Where a row says a change cannot be made piecemeal, respect that and leave
the existing code alone rather than half-converting it.

Each row is a shape, not a reference to a particular codebase. You should be able to
recognise it in whatever repo you are in.

| You will see                                                                                                                                                          | Follow instead                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Routes and handlers in one `<Feature>Endpoints.cs`, some over a thousand lines                                                                                        | Split into `<Resource>Api.cs` plus `<Resource>Handlers.cs` plus service. For a **new resource or file**, always split. For **one endpoint added to an existing single-file group**, match the file, since a lone `*Handlers.cs` beside a 1000-line sibling helps nobody, and note in the PR that the file is a split candidate. |
| Services returning a result object (`Success`, `ErrorCode`, `ErrorMessage`) that every handler unpacks by hand, mapped through a hand-written problem-details factory | `BusinessException` plus `.WithHandledException<BusinessException>()`. **Not convertible one handler at a time**, see the warning under `## Errors`. Convert a whole group or none.                                                                                                                                             |
| `.AddEndpointFilter<SomeFilter>()` applied straight onto a group                                                                                                      | Wrap it in a `With*` extension that also registers the filter's status codes.                                                                                                                                                                                                                                                   |
| `List<T>` returned from any collection that can grow, including a child collection                                                                                    | `ResultSet<T>` is the default. Bind `ListOptions`. Safe to fix in place, but it is a breaking change for generated clients, so flag it.                                                                                                                                                                                         |
| DataAnnotations on the request DTO instead of a validator class                                                                                                       | FluentValidation for new validation. Do not stack one on the other: pick the mechanism the request already uses, and if you change it, remove the other.                                                                                                                                                                        |
| Back-office groups under `admin/`, or bare `{id}` route parameters                                                                                                    | `manage/` and `{<entity>Id}` for new groups and routes. Renaming an existing route is a breaking change for every client, so leave it and add new endpoints to the group as it is.                                                                                                                                              |
| Endpoints with no `.WithSummary(...)`                                                                                                                                 | Add it. It lands in the generated client.                                                                                                                                                                                                                                                                                       |

## Relationship to `dotnet-webapi`

`dotnet/skills`' `dotnet-webapi` is the assumed baseline and we agree with most of it.
Where it conflicts with the table below, this skill wins.

| `dotnet-webapi` says                                                        | At Indice                                                                                    |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `CancellationToken` on every endpoint                                       | Only where it is actually forwarded downstream                                               |
| `TypedResults.Created($"/api/x/{id}", ...)`                                 | `TypedResults.CreatedAtRoute(model, nameof(GetEntityById), new { entityId = model.Id })`     |
| A `.http` file per project                                                  | Not an Indice practice                                                                       |
| Fall back to untyped `Results` past ~7 branches                             | Never. Annotate the union or split the endpoint                                              |
| `{Entity}ListResponse` for collections                                      | `ResultSet<T>` of the domain model                                                           |
| One static class per resource with `Map<Resource>(this WebApplication app)` | Extension is on `IEndpointRouteBuilder`, and routes are split from handlers across two files |

## Records

Use records for new types that carry data: request and response models, domain models,
events and commands, service results. Positional records where the type is small
(`public record SessionRequest(string? ExternalRefId, string? Referrer);`,
`public record CreateFolderResponse(Guid FolderId);`). Agents, Media and the SignalR proxy
contracts are the examples to follow.

Most existing Platform DTOs are classes because they were written before records existed.
That is history, not a convention. Do not copy the class shape into new code, and do not
convert an existing class to a record in passing: it changes equality semantics and is not
the change you were asked to make.


## Examples

The reference implementation is Messages' distribution lists:
`Endpoints/DistributionListsApi.cs` (the surface) and `Endpoints/DistributionListsHandlers.cs`
(thin handlers over `IDistributionListService`). Copy its shape.
`Indice.Features.Cases.Server`'s `AdminAccessRulesApi.cs` shows per-endpoint authorization
overrides on a group policy. Its routes are under `manage/`; the `Admin` in the file and
class name is not a route convention, so do not carry it into new names.

Both are in Indice.Platform, which every team can read. Prefer them over a file in your
own repo when you need a model to copy.
