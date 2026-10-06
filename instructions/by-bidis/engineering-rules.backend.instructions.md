---
applyTo: "**/*.cs"
---
# AI engineering rules: backend

Scoped companion to [`engineering-rules.instructions.md`](engineering-rules.instructions.md). The core file's precedence, definitions, and non-overridable rules apply here.

## API rules

* Never return EF entities from APIs. Always project to DTOs.
* Never create unbounded list endpoints. Pagination is mandatory; make filtering and sorting explicit.
* Use ProblemDetails for errors.
* Contracts match the approved requirement. Do not add convenience fields, expose internal IDs, or leak whether sensitive records exist unless the requirement allows it.
* Every exposed endpoint has an OpenAPI summary and description covering what it does, who uses it, scope/auth/idempotency requirements, and when it is used. Illustrative shape:

```csharp
/// <summary>Lists the caller's open orders.</summary>
/// <remarks>Used by the customer portal order list. Requires scope <c>orders:read</c>. Read-only and safe to retry.</remarks>
```

## Data and database rules

* Each module owns its own schema and persistence. Do not access, join across, or write to the tables, entities, repositories, or internals of another module. Use contract interfaces, application services, or approved integration events.
* Use a `Money` value object; store amounts with currency. Use typed IDs (for example `readonly record struct OrderId(Guid Value);`) instead of raw `Guid` or `int` parameters.
* Prefer append-only evidence for regulated and financial records. Do not overwrite regulatory evidence unless correction behaviour is explicitly required.
* Schema changes need a DB migration with review notes covering SQL, indexes, constraints, destructive operations, lock risk, rollback, and data impact. Never create destructive database migrations without explicit human approval.
* Add indexes intentionally and document why.

## .NET conventions

* Use the repository's `Result<T>` for expected outcomes instead of exceptions for control flow; follow the existing `Result<T>` type and its usage in the module rather than introducing a new one.
* Use file-scoped namespaces.
