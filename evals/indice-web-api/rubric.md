# Rubric: `indice-web-api`

Binary checks. Each is verifiable by reading or grepping the diff. None requires
a judgement call about quality. Mark `n/a` where a task cannot exercise the check
and drop it from the denominator.

Score = passed / (applicable).

## Return types

| #   | Check                                                                      | How to verify                                    |
| --- | -------------------------------------------------------------------------- | ------------------------------------------------ | -------- | ---------- | -------------------------- |
| 1   | Every handler returns `TypedResults.*`                                     | `grep -E '[^d]Results\.(Ok                       | NotFound | BadRequest | NoContent)'` finds nothing |
| 2   | No `IResult` / `IActionResult` / `ActionResult<T>` in a signature          | grep                                             |
| 3   | Multi-outcome handlers annotated `Task<Results<…>>`                        | Read each handler with more than one exit        |
| 4   | Created response uses `CreatedAtRoute` with `nameof`, not a hand-built URL | grep `CreatedAtRoute` vs `TypedResults.Created(` |
| 5   | Search/list endpoint taking `ListOptions` returns `ResultSet<T>`           | Read the list handler                            |
| 6   | No `List<T>` returned from a collection that can grow; `ResultSet<T>` is the default and `List<T>` needs a fixed-by-definition set to justify it | Read each collection return. `n/a` if the task has only one collection endpoint, already covered by check 5 |
| 7   | Paging/filter parameters bound with `[AsParameters]`                       | grep                                             |

## Structure

| #   | Check                                                                                                | How to verify                                      |
| --- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 8   | No lambda inlined into a `MapGet`/`MapPost`/…                                                        | grep `Map[A-Za-z]*\([^,]*,\s*(async )?\(`          |
| 9   | Handler holds no business logic, LINQ or `DbContext`                                                 | Read the handlers                                  |
| 10  | Logic lives in a service the handler calls                                                           | Read                                               |
| 11  | Handler class is `internal static`                                                                   | grep                                               |
| 12  | New files use the Api/Handlers split. An addition to an existing single-file group matches that file | Compare to a sibling file, then see drift check D1 |
| 13  | New group registered in the area aggregator, not in the host directly                                | Read the aggregator diff                           |

## Feature library only

| #   | Check                                                          | How to verify   |
| --- | -------------------------------------------------------------- | --------------- |
| 14  | Group prefix read from `IOptions<T>`, no literal               | grep `MapGroup` |
| 15  | `*Api.cs` declared in `namespace Microsoft.AspNetCore.Routing` | Read            |
| 16  | Routes and handlers in two files                               | `ls`            |
| 17  | No direct `AddEndpointFilter`, wrapped in a `With*` extension  | grep            |

## Product API only

Platform conventions are the standard in a product API too. Only these three are
genuinely context-dependent.

| #   | Check                                                                             | How to verify                                     |
| --- | --------------------------------------------------------------------------------- | ------------------------------------------------- |
| 18  | Group prefix is a literal, no invented `IOptions` plumbing                        | grep `MapGroup`                                   |
| 19  | The product's own permission helper applied the way sibling routes apply it       | Compare to a sibling group                        |
| 20  | Did **not** throw `BusinessException` into a group lacking `WithHandledException` | grep the group declaration. This would ship a 500 |

### Drift checks

Scored separately, because the target file may itself be non-conforming. Mark each
`followed Platform` / `copied the drift` / `n/a`. Copying drift is not a rubric failure
when the skill says to match the file, but it is worth counting.

| #   | Drift                                                                | Correct behaviour                                                     |
| --- | -------------------------------------------------------------------- | --------------------------------------------------------------------- |
| D1  | Single-file `<Feature>Endpoints.cs`                                  | New file: split. One endpoint into an existing group: match the file. |
| D2  | A result object unpacked by hand into a hand-written problem factory | Match the group. Do not half-convert it.                              |
| D3  | `.AddEndpointFilter<T>()` raw on a group                             | A new filter gets a `With*` extension.                                |
| D4  | `List<T>` from a paged, filtered endpoint                            | `ResultSet<T>`.                                                       |
| D5  | DataAnnotations where a validator would be added                     | Do not stack both on one request.                                     |

## Metadata and validation

| #   | Check                                                                                  | How to verify                                                   |
| --- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| 21  | `.WithName(nameof(Handler))` on every endpoint — never a string literal                | grep `WithName("` finds nothing                                 |
| 22  | `.WithSummary(...)` on every endpoint                                                  | Count vs endpoint count                                         |
| 23  | Group carries `WithGroupName` / `WithTags` / `ProducesProblem`                         | Read the group                                                  |
| 24  | `.ProducesResponseType(400, …)` not hand-added next to `WithParameterValidation`       | grep for the redundant pair                                     |
| 25  | One validation mechanism per request, never both stacked                               | Read the DTO and check for a sibling validator class            |
| 26  | Host defaults not reconfigured (no JSON/CORS/auth/ProblemDetails setup in the feature) | grep `ConfigureHttpJsonOptions`, `AddCors`, `AddProblemDetails` |

## Routing

| #   | Check                                                       | How to verify |
| --- | ----------------------------------------------------------- | ------------- |
| 27  | Route segments kebab-case, plural for collections           | Read          |
| 28  | Current-user routes under `my/`, back-office under `admin/` | Read          |

---

## Task 3 scoring

Task 3 uses the same checks, inverted: the diff under review is seeded with
violations, and the score is

```
(violations correctly identified) − (false positives)
─────────────────────────────────────────────────────
              violations seeded
```

Record false positives separately. An agent that flags six real violations and
invents four is not the same as one that flags six cleanly, and the difference
matters more for review work than for authoring.
