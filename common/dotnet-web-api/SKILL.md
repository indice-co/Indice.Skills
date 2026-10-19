---
name: dotnet-web-api
description: >
  Use when adding or changing ASP.NET Core endpoints: module-owned minimal API
  route groups, route and versioning shape, DTO-only contracts, HTTP method
  choice, server-side validation, ProblemDetails and status codes, pagination,
  idempotency, authorization and scoping, external callbacks and webhooks,
  audit and logging, and cross-module access.
---

# Web API patterns

Endpoints are module-owned, DTO-only, server-authoritative, paginated, auditable, and tenant-aware.

## Ownership and style

* Each module owns its endpoints under its own `Endpoints/` folder and exposes a single registrar, for example `public static IEndpointRouteBuilder MapOrdersEndpoints(this IEndpointRouteBuilder app)`.
* The API host only calls each module's registrar. It contains no business logic.
* Default style is minimal API endpoint groups using `RouteGroupBuilder`, one group per module or feature area, with consistent naming, authorization, validation, and error mapping.
* Controllers only if an architecture decision changes the platform style. Never mix styles without approval.

## Routes and versioning

Preferred shape: `/api/v1/{module}/{resource}`, for example `/api/v1/orders`, `/api/v1/orders/{orderId}`, `/api/v1/backoffice/orders/{orderId}/approve`.

* Include the API version in public routes. Use plural resource names and typed route parameters.
* Do not expose internal table names or module internals.
* Action-style routes only for commands that do not map cleanly to resource updates, such as `/approve`, `/cancel`, `/submit-for-review`.
* Keep back-office routes distinct where the permission model and response shape differ from customer-facing routes.

## Requests and responses

DTOs only. Never accept or return EF entities, domain entities, persistence models, provider SDK models, unfiltered external callback payloads, or internal exception types.

* Project explicitly at the API boundary.
* Request DTOs contain only client-supplied fields; response DTOs contain only approved contract fields. No over-posting.
* Do not accept server-owned fields from the client: status, tenant ID, fee or tax amounts, KYC decisions, audit fields, ledger facts. Server-authoritative values are calculated, resolved, or confirmed server-side.
* OpenAPI is the source of truth for generated clients. Every endpoint has a summary and description.
* Keep DTOs versioned and backward-compatible once consumed.

## HTTP methods

| Method | Use for |
| --- | --- |
| `GET` | Read-only retrieval |
| `POST` | Commands, creation, non-idempotent intent, external callbacks, operations requiring an idempotency key |
| `PUT` | Full replacement where the client supplies the full approved representation |
| `PATCH` | Partial update where explicitly supported and validated |
| `DELETE` | Only where deletion is approved; regulated evidence usually needs cancellation or reversal instead |

For regulated and financial records, prefer explicit commands over destructive updates, for example `POST /api/v1/payments/callbacks/{provider}` or `POST /api/v1/orders/{orderId}/approve`.

## Validation

Server-side validation is the source of truth; UI validation is convenience. Use FluentValidation or the approved approach. Validate input shape, allowed values, state transitions, tenant scope, command permissions, and idempotency key presence where required. Never trust client-provided calculations or eligibility flags. Failures return ProblemDetails with field-level errors where possible.

## Errors

All errors use ProblemDetails in one consistent shape.

| Status | Meaning |
| --- | --- |
| `400` | Malformed or invalid request shape |
| `401` | Unauthenticated |
| `403` | Authenticated but forbidden |
| `404` | Not found, where revealing absence is allowed |
| `409` | State conflict, concurrency conflict, duplicate command, invalid state transition |
| `422` | Semantically valid request failing business validation, only if adopted consistently |
| `429` | Rate limited |
| `500` | Unexpected server failure only |

Include `type`, `title`, `status`, `detail` where safe, a `traceId` or correlation reference, and field errors for validation. Never leak secrets, raw provider errors, internal exception details, sensitive PII, or whether a sensitive record exists when anti-enumeration applies.

## Lists

Pagination is mandatory. Page-based for back-office grids; cursor-based for high-volume feeds or event-style lists. Every list endpoint defines default and maximum page size, allowed sort and filter fields (allow-lists, never arbitrary client field names bound into queries), default sort, response shape, and total-count behaviour. Filtering and sorting are server-side. Never return all rows for client-side filtering.

```csharp
public sealed record PagedResult<T>(IReadOnlyList<T> Items, int PageNumber, int PageSize, int? TotalCount, bool HasNextPage);
public sealed record CursorResult<T>(IReadOnlyList<T> Items, string? NextCursor, int PageSize);
```

Check `Indice.EntityFrameworkCore` result-set helpers before writing paging code (see the `indice-packages` skill).

## Idempotency

Required for non-GET money operations, order or purchase operations, ledger postings, state lock or close commands, external callbacks, webhooks, provider callback processing, and retryable event handlers.

* Require an idempotency key wherever the client or provider can retry.
* Store the outcome where needed and return the same outcome for duplicate equivalent requests.
* Reject duplicate keys with conflicting payloads.
* Handle late and out-of-order callbacks safely.
* Never create duplicate orders, payments, ledger postings, audit records, or state transitions.

## Authorization

Enforced server-side per endpoint using Indice IAM scopes, roles, policies, and claims through approved patterns (see the `indice-iam` skill).

* Apply endpoint-level policies; check resource ownership and tenant scope where relevant.
* Reject direct-object-reference attempts. Sensitive lookups respect anti-enumeration.
* Never rely on the UI to hide unauthorized actions. For back-office APIs, return server-confirmed capabilities or allowed actions for UI rendering; the endpoint still authorizes the submitted action.

## Scoping

Scope data access by tenant where relevant.

* Never trust client-provided tenant values without authorization and server-side resolution. Resolve tenant and user scope from authenticated context.

## External callbacks and webhooks

Treat as hostile until verified: signature verification; timestamp and replay protection where the provider supports it; idempotency; safe logging; raw payload handling per approved evidence rules; provider-specific mapping isolated in infrastructure; no direct mutation of another module's tables; audit events for accepted state changes; a dead-letter or manual-review path where relevant. Never expose provider SDK models outside the owning module.

## Audit and logging

State-changing and regulated endpoints emit audit events. Use structured logging with a correlation ID and safe metadata only. Never log secrets, tokens, credentials, raw payment data, unnecessary PII, or sensitive regulatory evidence. Log external provider references only if approved and non-sensitive.

## Cross-module behaviour

Endpoint ownership follows module ownership. When an endpoint needs another module's data or behaviour, use that module's contracts interface or an approved integration event. Never query its tables, inject its DbContext, expose its internal DTOs, or duplicate its rules.

## Checklist

* Registered by its owning module; the host only wires the registrar.
* Route follows the versioned pattern; request and response are DTOs with no entity, persistence, or provider model exposed.
* Server-side validation present; ProblemDetails for errors with nothing sensitive leaked.
* Lists paginated, capped, and allow-listed for filtering and sorting.
* Idempotency for money, state-changing, callback, and retryable operations.
* Server-side authorization with ownership and tenant checks; direct-object-reference rejected; anti-enumeration respected.
* `CancellationToken` flows through async paths.
* Audit events for state-changing and regulated endpoints; structured logging with correlation ID.
* OpenAPI updated and generated clients still valid.
