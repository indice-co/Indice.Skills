# Task 02: Add an endpoint to a product API

**Target:** `EVPulse`, `src/EVPulse.Api/Endpoints/Management`
**Applicable rubric sections:** Return types, Structure, Product API, Metadata, Routing
**Not applicable:** Feature library section (14–17)

---

Paste verbatim into a fresh session.

---

In the EVPulse management API, add two endpoints to the existing users area:

1. A paged, searchable list of a user's RFID cards.
2. An endpoint that deactivates one of those cards, taking a short reason string
   in the body. It should fail cleanly if the card doesn't belong to that user,
   or if it is already deactivated.

Both should require the same permission as the other card and wallet operations
on a user, and appear in the management OpenAPI document.

Assume the repository and service methods you need exist; call them.

---

## What this task is probing

The inverse of task 01. Here the target file is itself non-conforming, so the task
separates two different things: the conventions that hold everywhere, and the
judgement about how far to go when the surrounding code is drifted.

Conventions that still apply (the skill says Platform is the standard in a product
API too):

- `ResultSet<T>` on the list endpoint. EVPulse is roughly 50/50 between `ResultSet<T>`
  and a bare `List<T>`, so the surrounding code will not settle it. Check 5, drift D4.
- `.WithName(nameof(...))`, `.WithSummary(...)`, a typed `Results<...>` union,
  no logic in the handler. Checks 21, 22, 3, 9.

Genuinely context-dependent (checks 18 to 20):

- A **literal** group prefix. No invented `IOptions` plumbing for a single consumer.
- `.RequireV2Permission(...)` copied from the sibling routes.
- Errors must match the group. The existing users group has no
  `.WithHandledException<BusinessException>()`, so a handler that throws one returns a
  500 with no error code. The correct answer is to unpack `ServiceResult` like its
  siblings, not to start converting the group.

The judgement call (drift D1): one endpoint added to an existing single-file group
should stay in that file. An agent that creates a lone `*Handlers.cs` next to a
1000-line sibling has followed the letter of the split rule and made the codebase
worse. An agent that notes the file is a split candidate without acting on it has read
the skill properly.

Check 25 and drift D5 are the subtlest line here. The request DTO will carry
DataAnnotations, and `WithParameterValidation` activates them through the MiniValidator
fallback. An agent that knows the helper but not the fallback adds a FluentValidation
validator on top, which silently stops the annotations running. That failure is
invisible at runtime, which is exactly why it is worth measuring.
