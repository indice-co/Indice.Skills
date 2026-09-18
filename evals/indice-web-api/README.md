# Eval: `indice-web-api`

Does the skill change what an agent produces? This harness answers that with a
mechanical score rather than an impression.

`indice-web-api` was chosen as the pilot skill because its conventions are
greppable. "Did it return `TypedResults.Ok` or `Results.Ok`?" needs no judgement
call, so two people scoring the same output get the same number.

## Arms

| Arm              | Agent context                                                         |
| ---------------- | --------------------------------------------------------------------- |
| **A — baseline** | No skill. The repo and whatever context the session normally carries. |
| **B — skill**    | `common/indice-web-api/SKILL.md` loaded.                              |

Run each task once per arm, in a **fresh session**. The agent must not have seen
the other arm's run, and must not have the rubric. Scoring the work is our job,
not the agent's.

## Running

1. Check out the target repo at a known commit. Note it in the results table.
2. Start a fresh session in that repo.
3. Arm B only: load the skill.
4. Paste the task file verbatim. No follow-up coaching, no corrections. The
   point is what the agent does unaided.
5. Save the diff.
6. Score against `rubric.md`. Checks that don't apply to the task are `n/a` and
   drop out of the denominator.

## Tasks

| File                       | Target                          | Shape                                 |
| -------------------------- | ------------------------------- | ------------------------------------- |
| `tasks/01-new-resource.md` | Indice.Platform feature library | Build a full CRUD resource            |
| `tasks/02-add-endpoint.md` | A product API (see note)        | Add one endpoint to an existing group |
| `tasks/03-review.md`       | Either                          | Review a diff seeded with violations  |

Task 2 is written against EVPulse, because that is where the drift the skill warns
about is easiest to find. **It needs access to that repo.** If you do not have it,
substitute your own product API: pick a resource group that already exists, ask for one
list endpoint and one mutating endpoint, and score the same rubric lines. The drift
checks (D1 to D5) are written as shapes precisely so they transfer. Tasks 1 and 3 need
only Indice.Platform and the diff in the task file, which every team can run.

Task 3 is scored differently: the score is violations correctly identified out of
those seeded, minus false positives. It tests whether the skill helps an agent
_recognise_ our conventions, not just reproduce them, which is the more common
real use, since most endpoint work is review.

## Conditions actually tested

Worth stating precisely, because it changes what the numbers mean.

- **Task 02 ran against a pristine clone of EVPulse `develop`**, cloned fresh for the
  purpose and verified clean before and after (`git status --porcelain` empty). Tasks 01
  and 03 ran against a clean Indice.Platform checkout. No agent wrote to either repo.
- **Both arms carried identical ambient context**, differing only in whether the skill was
  loaded. Whatever standing project context a session normally has was present in both, so
  it cannot account for any difference between them.
- **Neither arm was given endpoint conventions by anything except the skill.** Verified for
  the baseline arm: it drew every convention it applied from reading source files, and
  nothing in its starting context described `TypedResults`, `ResultSet<T>`,
  `WithName`/`WithSummary`, the Api/Handlers split or route-group structure.

So **arm A is not a clean room.** It is "the project's normal working context, plus repo
access, minus the skill", which is the realistic comparison, since that is what a
developer's session looks like. What the baseline arm demonstrates is how much of the
convention is recoverable by reading the code.

When reproducing this, set the session's working directory to the repo under test, so each
task runs with that project's own context and not another's.

## Results

Fill in on each run. Keep old rows. A skill that regresses after an edit should
be visible.

| Date       | Skill rev             | Task | Arm A          | Arm B          | Notes                                                                                                                                                                |
| ---------- | --------------------- | ---- | -------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-09-18 | 266-line rev, pre-tag | 01   | 27/27          | 27/27          | Output structurally identical. Only diffs: `string.Empty` vs `""`, doc-comment wrapping, summary wording.                                                            |
| 2026-09-18 | same                  | 02   | 10/11 + 3/3    | 11/11 + 3/3    | Only rubric gap: `WithSummary` (A 0, B 2) against 0/341 in sibling code. Drift D1: A copied the local single-file shape, B split.                                    |
| 2026-09-18 | same                  | 03   | 8/8 hits, 0 FP | 8/8 hits, 1 FP | Arm B asserted `Map*` must return `RouteGroupBuilder`. The reference library is split 29 to 24 between the two forms, so both are idiomatic. Arm A hedged correctly. |

### Tasks 01 and 03: the clean-codebase case

**The skill changed nothing measurable about correctness.** On task 01 both arms
independently produced the Api/Handlers split, the `IOptions` prefix, `ResultSet<T>`,
`WithName(nameof(...))`, `CreatedAtRoute`, `WithHandledException` and FluentValidation
validators. The two outputs differ only in `string.Empty` vs `""`, doc-comment wrapping
and the wording of three summaries. The baseline agent's own summary said it modelled the
work on the existing `DistributionLists` resource.

That is the finding: **a codebase this internally consistent is its own skill.** An agent
with repo access recovers the conventions without being told them.

On task 03 the baseline was marginally better: both caught all eight seeded violations,
but the skill arm added a false positive the baseline avoided, asserting a `Map*` return
type the reference library does not actually standardise.

### Task 02: the drifted-codebase case

Control, measured across the 56 existing files and 341 endpoints of the target area:
`WithSummary` 0, untyped `Results.*` 19, `IResult` 14, bare `Ok<List<...>>` 35 against 48
`ResultSet<T>`, `WithName("literal")` 9 against 329 `nameof`. An agent imitating its
neighbours here inherits all of that.

Both arms nonetheless got the universal conventions right, and both got the three
context-dependent calls right: literal prefix, the product's own permission helper on all
four routes, and neither threw a `BusinessException` into a group that has no
`WithHandledException` to catch it. That last one is the failure the skill warns about and
neither arm walked into it.

Two differences:

- **`WithSummary`.** Skill arm added it on both endpoints. Baseline added none, matching
  all 341 siblings. This is the one place in the whole harness where the skill beat
  imitation on a point imitation could not have supplied.
- **Drift D1.** Both created a new file. The skill arm split it into `...Api.cs` +
  `...Handlers.cs`, the baseline produced a single `...Endpoints.cs` like its neighbours.
  By the rule as written ("new resource or file: always split") the skill arm is correct.

### Cost

| Run | Baseline                      | With skill         |
| --- | ----------------------------- | ------------------ |
| 01  | 103,084 tok / 32 calls / 238s | 88,347 / 27 / 227s |
| 02  | 85,219 / 26 / 179s            | 95,245 / 32 / 230s |
| 03  | 66,597 / 15 / 125s            | 58,994 / 5 / 82s   |

Cheaper with the skill on two runs, dearer on one, and on task 02 dearer on all three
measures. **There is no cost trend here.** At n=1 per cell these numbers are noise, and
the token argument from the top-level README is untested by this pilot rather than
supported by it.

### Overall

**Across three runs the skill's measured effect is small and concentrated in one place.**
It is zero on a clean, internally consistent codebase, slightly negative on review (one
false positive), and on a drifted product API it supplies two things the surrounding code
cannot: `WithSummary`, which no sibling endpoint has, and the Api/Handlers split for a new
file.

So the honest case for this skill is narrow: **it is worth having where the codebase would
teach an agent the wrong thing, and worth little where the codebase already teaches the
right thing.** That is a useful finding for the catalogue as a whole, because it predicts
which future skills will pay: not the ones describing what a clean repo already
demonstrates, but the ones encoding a standard the code has drifted away from.

**Caveats.** n=1 per cell. Both arms could read the reference library, and task 03's prompt
pointed at it explicitly, so this measures _skill versus reading the reference
implementation_, not _skill versus nothing_. Both arms ran on the same model as the session
that authored the skill. The two task-02 findings are the ones worth re-running first,
because they are the only ones where a mechanism is visible rather than just a number: the
sibling code demonstrably cannot supply either answer.

## Reading the result

- **B clearly above A**: the skill carries knowledge the agent lacks. Keep it,
  and check _which_ rubric lines moved. The ones that didn't are dead weight in
  the skill and should be cut.
- **B ≈ A**: The agent already infers our conventions from surrounding code, or
  the skill never loaded. Check the second possibility first: an unloaded skill
  scores exactly like no skill. If it did load, the honest conclusion is that this
  content belongs in a short instructions file, not a skill. And that is a
  useful result for the wider initiative, not a failed experiment.
- **B below A**: the skill is misleading somewhere. Find the rubric line that
  regressed and fix that section.

Whatever the outcome, record it. The point of the pilot is to learn whether
skills earn their keep, and a negative result that we act on is worth more than
a positive one we assumed.
