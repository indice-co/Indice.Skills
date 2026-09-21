# Task 02: Add endpoints to a product API

**Target:** any product API built on Indice.Platform. Instantiate this against the one you work on.
**Applicable rubric sections:** Return types, Structure, Product API, Metadata, Routing, plus the drift checks
**Not applicable:** Feature library section (14 to 17)

This is the task that distinguishes the skill from the codebase, so it is the one
worth running everywhere. Tasks 01 and 03 exercise a clean reference library and
will look much the same in any product. This one does not: its result depends on
how far your product has drifted, which is different in each.

---

## Instantiating it

**1. Pick the target.** An endpoint area that already exists and already has
siblings: a resource group with several routes on it, ideally one where list and
mutation endpoints already live. Do not pick a greenfield area; the point is to
see what the agent copies.

**2. Measure the control first**, before running either arm:

```
./score.py <path to that endpoint folder> --control --label "CONTROL: <product> <area>"
```

Read the raw counts, not the verdicts. They tell you what an agent imitating its
neighbours would produce. The skill can only beat imitation on lines where the
control is already wrong, so the control predicts which rubric lines can move at
all. Record it beside your results; **it is not transferable between products.**

**3. Write the task.** Two endpoints, phrased in your product's own domain terms:

- one **paged, searchable list** scoped to a parent entity
- one **mutation** that must fail cleanly in two distinct ways

Say that both must carry the same permission as the neighbouring operations and
appear in the same OpenAPI document. End with: *"Assume the repository and service
methods you need exist; call them."* That keeps the run about endpoint shape
rather than persistence.

**4. Run both arms** per the top-level README, in fresh sessions, output to a
scratch directory rather than the repo.

## What to watch for

The three **context-dependent** checks (18 to 20). These are where a skill can do
damage by over-generalising, so a correct answer here matters as much as the
universal checks:

- the group prefix should stay a **literal**; no `IOptions` plumbing invented for
  a single consumer
- the product's **own permission helper**, applied the way sibling routes apply it
- errors must **match the group**. If the group has no
  `.WithHandledException<BusinessException>()`, a handler that throws one returns a
  500 with no error code. The correct answer is to match the surrounding idiom and
  flag the group as a conversion candidate, not to convert one handler.

Then the **drift checks** (D1 to D5). Score each as *followed Platform* / *copied
the drift* / *n/a*. Copying drift is not a failure where the skill says to match
the file; count it anyway, because the ratio across products is the interesting
number.

Two lines are worth particular attention because they are invisible at runtime:

- **D5 / check 25.** If your request DTOs carry DataAnnotations and the project
  registers no FluentValidation validators, `WithParameterValidation<T>` is
  working through the MiniValidator fallback. An agent that knows the helper but
  not the fallback adds a validator on top, giving one request two validation
  layers and silently stopping the annotations.
- **Check 22.** Whether `.WithSummary(...)` appears. If your control shows few or
  none, this is a line imitation cannot supply, so it is a clean read on whether
  the skill contributed anything.

## Reference instantiation

Run on 2026-09-18 against EVPulse, management API, users area. Control: 56 files,
341 endpoints, `WithSummary` 0, untyped `Results.*` 19, `IResult` 14, bare
`Ok<List<...>>` 35 against 48 `ResultSet<T>`, `WithName("literal")` 9 against 329
`nameof`. Task: list a user's RFID cards (paged, searchable); deactivate one with
a reason in the body, failing if the card is not that user's or is already
deactivated. See the results table in the README.
