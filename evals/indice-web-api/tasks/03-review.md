# Task 03: Review a diff

**Target:** any Indice.Platform feature library (the diff is self-contained)
**Scoring:** see "Task 3 scoring" in `rubric.md`: hits minus false positives, over 8

---

Paste everything between the rules into a fresh session.

---

Review this pull request for a new feature library resource. Flag anything that
does not match how we build endpoints.

```csharp
// src/Indice.Features.Widgets.AspNetCore/Endpoints/WidgetEndpoints.cs
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;

namespace Indice.Features.Widgets.AspNetCore.Endpoints;

public static class WidgetEndpoints
{
    public static IEndpointRouteBuilder MapWidgets(this IEndpointRouteBuilder routes) {
        var group = routes.MapGroup("/api/widgetItems")
             .WithTags("Widgets");

        group.RequireAuthorization();

        group.MapGet("", async (IWidgetService service, int page, int size) => {
            var widgets = await service.GetList(page, size);
            return Results.Ok(widgets);
        })
        .WithName("GetWidgets");

        group.MapGet("{widgetId}", WidgetHandlers.GetWidgetById)
             .WithName("GetWidgetById");

        group.MapPost("", WidgetHandlers.CreateWidget)
             .WithName("CreateWidget")
             .WithParameterValidation<CreateWidgetRequest>()
             .ProducesResponseType(StatusCodes.Status400BadRequest, typeof(HttpValidationProblemDetails));

        group.MapDelete("{widgetId}", WidgetHandlers.DeleteWidget)
             .WithName("DeleteWidget");

        return routes;
    }
}
```

```csharp
// src/Indice.Features.Widgets.AspNetCore/Endpoints/WidgetHandlers.cs
namespace Indice.Features.Widgets.AspNetCore.Endpoints;

public static class WidgetHandlers
{
    public static async Task<IResult> GetWidgetById(WidgetDbContext db, Guid widgetId) {
        var widget = await db.Widgets
            .Where(x => x.Id == widgetId && !x.IsArchived)
            .Select(x => new Widget { Id = x.Id, Name = x.Name, Owner = x.Owner.DisplayName })
            .FirstOrDefaultAsync();
        if (widget == null) {
            return Results.NotFound();
        }
        return Results.Ok(widget);
    }

    public static async Task<Created<Widget>> CreateWidget(IWidgetService service, CreateWidgetRequest request) {
        var widget = await service.Create(request);
        return TypedResults.Created($"/api/widgetItems/{widget.Id}", widget);
    }

    public static async Task<NoContent> DeleteWidget(IWidgetService service, Guid widgetId) {
        await service.Delete(widgetId);
        return TypedResults.NoContent();
    }
}
```

---

## Seeded violations (8)

Do not show this list to the agent.

| #   | Violation                                                                                                                                  | Rubric  |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| 1   | Group prefix is the literal `"/api/widgetItems"`: a feature library reads it from `IOptions<T>`                                            | 14      |
| 2   | Route segment is camelCase and not the resource's plural name. Should be kebab-case `widgets`                                              | 27      |
| 3   | The list endpoint is an inlined lambda instead of a named handler                                                                          | 8       |
| 4   | `Results.Ok` / `Results.NotFound` / `Task<IResult>` instead of `TypedResults` and a typed union                                            | 1, 2, 3 |
| 5   | List endpoint takes loose `int page, int size` and returns a bare collection. Should be `[AsParameters] ListOptions` → `ResultSet<Widget>` | 5, 7    |
| 6   | `WithName("GetWidgets")` etc. are string literals, not `nameof(...)`                                                                       | 21      |
| 7   | `TypedResults.Created` with a hand-built URL instead of `CreatedAtRoute(nameof(GetWidgetById), …)`                                         | 4       |
| 8   | `WidgetHandlers.GetWidgetById` queries `WidgetDbContext` directly. Logic belongs in `IWidgetService`                                       | 9, 10   |

Also present but **not** counted, because they are judgement calls rather than
rule violations. Count them as false positives only if the agent asserts them as
errors:

- `ProducesResponseType(400, …)` next to `WithParameterValidation` is redundant
  (the extension adds it). Credit as a hit if flagged. It is check 24.
- No `.WithSummary(...)` anywhere (check 22).
- Classes are `public` rather than `internal` (check 11).
- `MapWidgets` returns `routes` rather than the group: both appear in Platform.

## What this task is probing

Recognition rather than production. Most endpoint work in practice is review, and
an agent that writes correct code but cannot spot an incorrect PR is only half
useful. The false-positive count matters here as much as the hit count: a review
that flags four imaginary problems alongside six real ones costs the reviewer
more than it saves.
