# Task 01: New resource in a feature library

**Target:** `Indice.Platform`, `src/Indice.Features.Messages.AspNetCore`
**Applicable rubric sections:** Return types, Structure, Feature library, Metadata, Routing
**Not applicable:** Product API section (18–20)

---

Paste the block below verbatim into a fresh session. Nothing else, no hints
about conventions, no pointers to sibling files.

---

In `src/Indice.Features.Messages.AspNetCore`, add a new **message tags** resource to the
management API. A tag has an `Id` (Guid), a `Name`, a `Description`, and a
`CreatedAt`. It needs:

- list tags, with paging, sorting and a free-text search
- get one tag by id
- create a tag
- update a tag
- delete a tag
- list the campaigns currently using a given tag

It should sit alongside the other management resources and show up in the same
OpenAPI document and generated client as they do. Requires the same scope and
management permission as distribution lists.

Add the service layer too: assume a store/persistence method exists for each
operation and call it. You do not need to implement persistence.

---

## What this task is probing

Every convention an agent cannot infer without reading sibling code:

- the two-file split and the `Microsoft.AspNetCore.Routing` namespace (11, 15, 16)
- prefix from `IOptions<MessageManagementOptions>` rather than `"/message-tags"` (14)
- `ResultSet<MessageTag>` for the paged list, and `ResultSet<Campaign>` for the
  campaigns-using-a-tag endpoint: a sub-collection that can grow is still paged (5, 6)
- `WithName(nameof(...))` + `CreatedAtRoute` on the create endpoint (4, 21)
- registration in `MapMessagingManagement()` rather than the host (13)

A baseline agent will usually produce working, idiomatic-for-ASP.NET code here
that gets most structural checks wrong. That gap is the measurement.
