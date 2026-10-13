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
3. Paste the prompt for that task and arm from `prompts.md`. That file, not the
   task file, is what you paste: the task files say what is being measured, the
   prompts carry the scaffolding the runs actually used.
4. No follow-up coaching, no corrections. The point is what the agent does unaided.
5. Save the output.
6. Ask the agent what it consulted (the question is in `prompts.md`) and discard
   any baseline that found the skill. This check is not optional! See the control
   problem on task 03 below.
7. Score against `rubric.md`. `score.py` does the greppable half and flags the rest `REVIEW`. Checks that
   don't apply are `n/a` and drop out of the denominator.

`prompts.md` also carries a chat profile for models with no filesystem access,
which is the only way to get a genuine baseline on task 03.

## Tasks

| File                       | Target                               | Shape                                  |
| -------------------------- | ------------------------------------ | -------------------------------------- |
| `tasks/01-new-resource.md` | Indice.Platform feature library      | Build a full CRUD resource             |
| `tasks/02-add-endpoint.md` | Any product API (you instantiate it) | Add two endpoints to an existing group |
| `tasks/03-review.md`       | Either                               | Review a diff seeded with violations   |

Tasks 1 and 3 are fixed: they run against Indice.Platform and against a self-contained
diff, so every team runs the same thing and results are comparable.

**Task 2 is a template you instantiate against your own product**, because its result
depends on how far that product has drifted, and that differs everywhere. The task file
has the recipe. Run `score.py <area> --control` against your target area first to get the control: the
skill can only beat imitation on lines where the control is already wrong, so the control
tells you in advance which rubric lines can move at all. Controls do not transfer between
products, so record yours beside your results.

**Task 2 is the one worth running in every product.** Tasks 1 and 3 largely re-measure the
reference library and will look similar wherever they run.

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

## Comparing runs: what is and is not comparable

Read this before putting a second harness's numbers next to a first's.

**Scores are only comparable when the instrument is named.** `rubric.md` has 28
numbered checks plus 5 drift checks. Task 01 and 03 are feature-library cases, so
checks 18 to 20 are `n/a` and **25 apply**. Task 02 is a product-API case, so 14 to
17 are `n/a`. Always report as `n/25` or `n/24` with the instrument stated, never a
bare fraction. A score derived from a helper script is on that script's scale, not
the rubric's, and the two must not be mixed in one column.

**Token and wall-clock numbers do not compare across harnesses, at all.** The
tool and system-prompt schema is re-sent on every call, so a host with a large MCP
surface can spend an order of magnitude more than a lean one for identical work.
Different hosts also count differently: a per-subagent total and a sum of
`input_tokens + output_tokens` across calls are not the same measurement. Treat
cost as a **within-run ratio only**, baseline against skill, same host, same model,
same day. A cross-harness cost table is meaningless and should not be built.

**Record the conditions with every row**: host, model, date, instrument, and
whether the run compiled the result. Two rows without those are not evidence of a
trend.

## Results

Fill in on each run. Keep old rows. A skill that regresses after an edit should
be visible.

| Date       | Skill rev             | Task                           | Arm A          | Arm B             | Notes                                                                                                                                                                                                                                                                                                                 |
| ---------- | --------------------- | ------------------------------ | -------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-09-18 | 266-line rev, pre-tag | 01                             | 27/27          | 27/27             | Output structurally identical. Only diffs: `string.Empty` vs `""`, doc-comment wrapping, summary wording.                                                                                                                                                                                                             |
| 2026-09-18 | same                  | 02                             | 10/11 + 3/3    | 11/11 + 3/3       | Only rubric gap: `WithSummary` (A 0, B 2) against 0/341 in sibling code. Drift D1: A copied the local single-file shape, B split.                                                                                                                                                                                     |
| 2026-09-18 | same                  | 03                             | 8/8 hits, 0 FP | 8/8 hits, 1 FP    | Arm B asserted `Map*` must return `RouteGroupBuilder`. The reference library is split 29 to 24 between the two forms, so both are idiomatic. Arm A hedged correctly.                                                                                                                                                  |
| 2026-09-18 | same                  | 01 (repeat)                    | 27/27          | 27/27             | Reproduces.                                                                                                                                                                                                                                                                                                           |
| 2026-09-18 | same                  | 02 (repeat)                    | 10/11 + 3/3    | 11/11 + 3/3       | Reproduces: same single gap, same D1 split.                                                                                                                                                                                                                                                                           |
| 2026-09-18 | same                  | 03 (repeat, isolated baseline) | 8/8 hits       | 8/8 hits + extras | Baseline scored 8/8 again, having found the reference library unaided. See below.                                                                                                                                                                                                                                     |
| 2026-09-21 | 266-line rev, d33e9cd | 02                             | 14/17          | 17/17             | Re-run against EVPulse`develop` @ `5a88a16b`, output-directory variant (agents wrote to a scratch dir, repo verified clean before/after). See "2026-09-21 re-run" below.                                                                                                                                              |
| 2026-09-21 | same                  | 01                             | 25/25          | 25/25             | Re-run, output-directory variant. Structurally identical again. Both arms paged the campaigns-using-a-tag child collection, which is correct.                                                                                                                                                                         |
| 2026-09-21 | same                  | 03                             | 5/8 hits, 0 FP | 8/8 hits, 0 FP    | Re-run as isolated background sub-agents (model: claude-sonnet-5). Baseline missed the kebab-case naming call, the loose-params-instead-of-`ListOptions`/`ResultSet` call, and the handler-owned `DbContext`/LINQ call. Skill arm caught all 8 cleanly, no false positive this time (reverses the 2026-09-18 result). |
| 2026-09-21 | same                  | 01                             | 25/25          | 25/25             | Sub-agent model **claude-opus-5**. Same as the sonnet-5 run, including the paged campaigns-per-tag child collection.                                                                                                                                                                                                  |
| 2026-09-21 | same                  | 02                             | 16/17          | 17/17             | Sub-agent model **claude-opus-5**, EVPulse `develop` @ `5a88a16b`. Baseline this time kept business logic out of the handler (no LINQ leak, unlike the sonnet-5 baseline) — only rubric gap is `WithSummary` (A 0, B 2), same as every other run of this task.                                                        |
| 2026-09-21 | same                  | 03                             | 8/8 hits, 1 FP | 8/8 hits, 1 FP    | Sub-agent model **claude-opus-5**. Both arms caught all 8 seeded violations this time (opus-5 baseline is markedly stronger than sonnet-5's baseline here). Each added one false positive of its own — see "2026-09-21 re-run, claude-opus-5" below. A tie on this task at this model tier.                           |
| 2026-09-21 | 266-line rev          | 01                             | **24/24**      | **24/24**         | rubric.md, profile=library. Identical.                                                                                                                                                                                                                               |
| 2026-09-21 | 266-line rev          | 02                             | **19/21**      | **21/21**         | rubric.md, profile=product. A failed 12 (new file, not split) and 22 (`WithSummary` 0/2). Drift D1: A copied, B followed.                                                                                                                                                                                             |
| 2026-09-21b | c677a58, collection rule settled | 01 | **25/25** | **25/25** | `score.py --profile library`. Sub-agent model **claude-opus-5**. Skill rev now inverts check 6: `ResultSet<Campaign>` on the campaigns-per-tag endpoint is correct, not a bounded-`List<T>` exception. Both arms produced it; identical structurally to every prior task-01 run. See "2026-09-21b re-run" below. |
| 2026-09-21b | same | 02 | **20/21** | **21/21** | `score.py --profile product`, EVPulse `2c05e62d`. Sub-agent model **claude-opus-5**. Only gap: `WithSummary` (A 0/2, B 2/2) — the same single gap every run of this task has found, on every skill rev, every model. |
| 2026-09-21b | same | 03 | 8/8 hits, 0 FP | 8/8 hits, 1 FP | Scored by hand (task 3 has no `.cs` output for `score.py` to read). Sub-agent model **claude-opus-5**. Baseline caught all 8 unaided and added no false positive this time. Skill arm also caught all 8 but repeated the recurring `RouteGroupBuilder`-return false positive (present in the 2026-09-18 and prior opus-5 runs too). |

**Denominators differ by instrument and are not interchangeable.** The `/17` and `/25` rows
were scored against a hand-selected applicable set; the `/21` and `/24` rows against
`score.py`, which derives the `n/a` set from the profile. Compare a row only with another
row scored the same way. The `/24` and `/21` rows are the ones `score.py` reproduces.

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

### The control problem on task 03

Task 03 was run three times under three different baseline conditions, trying to construct
a genuine "skill versus nothing" comparison. The baseline scored 8/8 every time:

| Baseline condition                       | What it did                                                  | Score |
| ---------------------------------------- | ------------------------------------------------------------ | ----- |
| Told it could read the reference library | Read it, 15 tool calls                                       | 8/8   |
| No pointer given                         | Searched, found this skills repo, reviewed against the skill | 8/8   |
| Skills repo explicitly out of bounds     | Searched, found the reference library unaided                | 8/8   |

**A "skill versus nothing" control is not constructible on a machine that has the reference
implementation on disk.** Remove the pointer and the agent goes looking. Whatever it finds
first, it uses. The second condition is the sharpest illustration: given no guidance at
all, the agent discovered this repository and reviewed against the very skill it was
supposed to be a control for. That run is void as a measurement, but it is a fair
demonstration that a discoverable skill gets used.

The practical conclusion for review work: **locally, the skill adds nothing, because
locally the reference is always available.** Its value for review is confined to the cases
where the code is not at hand, and those are common: a PR read in a browser, a CI check, an
agent working in a different repository. None of them are what this harness measures, and
measuring them would need a genuinely isolated environment.

### 2026-09-21 re-run: task 02, EVPulse, background sub-agents

Repeated task 02 with the exact scenario in `tasks/02-add-endpoint.md` (users area, RFID
cards list + deactivate), against a fresh EVPulse `develop` checkout at `5a88a16b`, clean
before and after (`git status --porcelain` empty both times, verified by the agents and by
us). Both arms ran as isolated background sub-agents, each pointed at the repo and an
output-only scratch directory, never at each other. Arm B's preamble pointed at
`common/indice-web-api/SKILL.md` in full, per the prompt template. Both arms confirmed in
their sign-off answer whether they'd consulted anything under `Indice.Skills`: baseline
**no**, skill arm **yes, only the one file it was pointed at**.

Baseline (arm A) added the two endpoints into the existing `UsersPaymentsEndpoints.cs`
group (correctly matching D1: one endpoint into an existing single-file group should stay
in that file). It reused `PartnerAccountPermissionV2.UserProfileCardsAndWallet`, returned
`ResultSet<T>` from the list endpoint, used `nameof` for `WithName`, and did not throw a
`BusinessException` into the unhandled group. Two rubric misses: no `WithSummary` on
either endpoint (matching all 341 siblings), and the deactivate handler put the
ownership/already-deactivated checks directly in the handler as inline LINQ over
`user.Tags` — a handler doing business logic (checks 9 and 10), not delegating that
decision to the service the way its own neighbours in the same file do.

Skill arm (B) added a new `UsersRfidCardsEndpoints.cs`, registered from the aggregator,
with `.WithSummary(...)` on both endpoints and a handler that does nothing but call
`IUserProfileServiceManagement.SearchRfidCardsForUser` /
`.DeactivateRfidCardForUser` and unpack the `ServiceResult` — no LINQ, no ownership check
in the handler. Both arms used DataAnnotations on the request DTO plus
`.WithParameterValidation<T>()` and did not stack a FluentValidation validator on top
(neither walked into the D5 trap). Drift D1 is a partial pass for B: it made a new file as
the rule for "new resource or file" says to, but did not split routes from handlers into
two files the way the reference implementation does — one file holding both, which is
neither the sibling shape nor the full split.

Rubric score, applicable checks only (1,2,3,5,7,8,9,10,11,12,19,20,21,22,24,25,27 = 17):
**baseline 14/17, skill arm 17/17**. The three misses are `WithSummary` (both endpoints)
and the handler-side LINQ ownership check, which is a new finding this run did not see
last time: on task 02 the skill arm's thin-handler discipline held under drift where the
baseline's did not, on top of the `WithSummary` gap already recorded on 2026-09-18.

### 2026-09-21 re-run: task 01, Indice.Platform, background sub-agents

Repeated task 01 (message tags in `Indice.Features.Messages.AspNetCore`) the same way, as
two isolated background sub-agents writing only to a scratch output directory, repo
verified clean before and after. Sign-off answers matched expectations: baseline **no**
consultation of `Indice.Skills`, skill arm **yes**, only the one file it was pointed at.

The result reproduces 2026-09-18 almost exactly: the two `MessageTagsApi.cs` files are
identical except for parameter order in the handler signatures and doc-comment wording, and
both independently produced the `IOptions<MessageManagementOptions>` prefix, the
`Microsoft.AspNetCore.Routing` namespace, `WithHandledException<BusinessException>`,
`WithName(nameof(...))`, and `ResultSet<MessageTag>` on the main list. Reused evidence for
"a consistent codebase is its own skill."

Both arms bound `[AsParameters] ListOptions` to the campaigns-using-a-tag endpoint and
returned `ResultSet<Campaign>`, the correct shape for a child collection that can grow.

Score: **25/25 applicable checks, both arms** (18–20 n/a, feature library only).

### 2026-09-21 re-run: task 03, review, background sub-agents

Repeated task 03 (the seeded `WidgetEndpoints`/`WidgetHandlers` review) as two isolated
background sub-agents, each writing its review to a scratch file, neither told the other's
result or the rubric. Sign-off: baseline **no** consultation outside the repo it was
working in, skill arm **yes**, `SKILL.md` only.

This run reverses the 2026-09-18 result. Baseline caught 5 of the 8 seeded violations
(hard-coded prefix, inlined lambda, untyped `Results.*`/`IResult`, string-literal
`WithName`, hand-built `Created(...)` URL) but **missed three**: it never called out the
camelCase-not-kebab-case route segment, never flagged the loose `int page, int size`
parameters that should bind `[AsParameters] ListOptions` and return `ResultSet<Widget>`,
and never noticed `GetWidgetById` queries `WidgetDbContext` directly instead of going
through `IWidgetService` — arguably the most load-bearing violation in the seed, since it's
the one the skill spends a whole callout box on ("Do not copy the older Identity
handlers... inject a DbContext straight into the handler"). No false positives, but 3/8
misses is a real gap.

Skill arm caught all 8 cleanly — including the DbContext/LINQ violation and the naming
convention — with zero false positives (unlike 2026-09-18, where the skill arm asserted a
`Map*`-return-type rule the reference library doesn't actually enforce). Score: **baseline
5/8 hits 0 FP, skill arm 8/8 hits 0 FP.**

This is the one place across both runs where the skill clearly outperformed the baseline
on both correctness and cost (see below) with no offsetting false positive, and it is a
review task — the use case the harness's own author flagged as "the more common real use."

### 2026-09-21 re-run, claude-opus-5: all three tasks

Repeated all three tasks a third time, same isolated-background-sub-agent method, same
output-directory-only variant, same repos and commits (`Indice.Platform` @ `1b9e0e8e`,
EVPulse `develop` @ `5a88a16b`, both verified clean before and after), but with the
sub-agent `model` explicitly set to `claude-opus-5` instead of the session default
(`claude-sonnet-5`) used for every run above. All six sign-off answers matched
expectations: both baselines **no**, both skill arms **yes, `SKILL.md` only**.

**Task 01 (message tags).** Same result as sonnet-5: structurally identical output, both
arms independently correct on the `IOptions` prefix, the `Microsoft.AspNetCore.Routing`
namespace, `WithHandledException<BusinessException>`, `WithName(nameof(...))`, and
`ResultSet<MessageTag>` on the main list, and both arms again paged the campaigns-per-tag
child collection. Score: 25/25 both arms, same as sonnet-5.

**Task 02 (EVPulse RFID cards).** The opus-5 baseline is a materially better baseline than
the sonnet-5 one was: it added the two endpoints as a new `UsersRfidCardsEndpoints.cs`
sub-group file (matching the shape of existing sibling sub-groups like
`UsersPaymentsEndpoints.cs` — a defensible D1 call, not a rubric failure), used
`ResultSet<RfidCard>`, `nameof`, DataAnnotations without stacking a validator, and —
unlike the sonnet-5 baseline — kept the ownership/already-deactivated check **out of the
handler** entirely, unpacking a `ServiceResult` from the service exactly like its
siblings. The only rubric gap left is `WithSummary` (A: 0, B: 2 — the same single gap
found on every run of this task, sonnet or opus, skill or no skill). Score: **baseline
16/17, skill arm 17/17.** The skill's measurable edge on this task shrank from 3 points
(sonnet-5) to 1 point (opus-5), because a stronger model made the same correct call the
skill states about keeping business logic out of the handler, without being told.

**Task 03 (review).** The clearest model effect in the whole harness. The opus-5 baseline
caught **all 8** seeded violations unaided — including the kebab-case naming call, the
`ListOptions`/`ResultSet` call, and the `DbContext`/LINQ-in-handler call that the
sonnet-5 baseline missed entirely — plus 15 additional, mostly correct observations
(missing group metadata, missing `WithHandledException`, non-compiling
`ProducesResponseType` overload, missing usings). One of those extra observations is a
genuine false positive: it asserts the project should be renamed from
`Indice.Features.Widgets.AspNetCore` to `...Widgets.Server` because "new server-side
features live in `*.Server`" — but `.AspNetCore` is still the live convention for Messages
and Media, so this is asserted too strongly as a defect. The skill arm also caught all 8,
plus its own false positive — the same one flagged on 2026-09-18: asserting `MapWidgets`
must return `RouteGroupBuilder`, when the reference library is split roughly evenly
between that and `IEndpointRouteBuilder`. Score: **baseline 8/8 hits 1 FP, skill arm 8/8
hits 1 FP — a tie.** With a stronger model, the skill's task-03 advantage (sonnet-5: 8/8
vs 5/8) disappears entirely; the model's own thoroughness closes the gap the skill filled
for the weaker model.

**Token/call/wall-clock, opus-5** (same measurement method as before, per-agent, summed
`input_tokens + output_tokens`):

| Task | Arm      | LLM calls | Total tok | Wall clock |
| ---- | -------- | --------- | --------- | ---------- |
| 01   | Baseline | 30        | 1,801,203 | 303s       |
| 01   | Skill    | 36        | 1,891,695 | 276s       |
| 02   | Baseline | 25        | 1,248,653 | 208s       |
| 02   | Skill    | 17        | 855,086   | 140s       |
| 03   | Baseline | 10        | 334,326   | 111s       |
| 03   | Skill    | 8         | 265,737   | 95s        |

Same "no consistent direction" pattern as sonnet-5: skill cheaper on 02 and 03 (fewer
calls, fewer tokens, less wall clock), dearer on 01 by calls and tokens (though marginally
_faster_ in wall clock despite more calls — shorter individual turns). Opus-5 runs used
noticeably more tokens per call than sonnet-5 did on the same tasks (e.g. task 02
baseline: 1.25M tokens over 25 calls here vs 1.47M over 29 calls for sonnet-5 — similar
total, similar call count, comparable cost) while being visibly more thorough on task 03
in particular. **This is one data point per cell, on one day; it is not a claim that
opus-5 is cheaper or more expensive than sonnet-5 in general**, only a record of what this
specific harness run cost.

### 2026-09-21b re-run: skill rev `c677a58`, all three tasks, `score.py`

A teammate pushed `c677a58` ("Settle the collection rule and make eval runs reproducible")
the same day, which changed three things worth separating from every row above: the
collection rule (§ "Collections" in `SKILL.md`) now says `ResultSet<T>` is the default for
*any* collection that can grow, including a child of one parent — the old rule's
`List<T>`-for-bounded-sub-collections exception is gone, and rubric check 6 is inverted to
match; `score.py` replaced hand-scoring for tasks 01/02, deriving the applicable set from
`--profile library|product` and printing `PASS`/`FAIL`/`REVIEW`/`NA` per check; and run
outputs now live under `evals/indice-web-api/runs/` (gitignored) instead of an external
scratch directory. Repeated all three tasks again, sub-agent model **claude-opus-5**,
against `Indice.Platform` @ `1b9e0e8e` and a fresh `EVPulse` @ `2c05e62d` (one unrelated,
pre-existing local modification — a dev-only `app-settings.manifest.json` authority URL —
was stashed before the run and restored after; it was not part of any arm's diff). Both
repos verified clean before and after with `git status --porcelain`. All six sign-off
answers matched expectations: both task-01 baselines and the task-02/03 baselines said
**no** consultation outside their target repo; all three skill arms said **yes**,
`SKILL.md` only.

Two of the six sub-agent calls (task 01 baseline, task 01 skill) and one more (task 03
baseline) hit a mid-run quota error and had to be restarted; the restarted agents picked up
any partial output already on disk in their own scratch directory and finished from there.
Token/call totals below sum **both** the failed attempt and the completed retry for those
three, since both legitimately spent tokens getting to the final artifact — the wall-clock
column reports only the completed attempt's own elapsed time, since the failed attempt's
duration before erroring was not captured.

**Task 01 (message tags).** `score.py --profile library` on both arms: every check
auto-decided `PASS` except three genuine judgement calls (3, 12, 28) plus check
5/6/9/10/13, all resolved by reading the diff. Handlers are thin in both arms (no
`DbContext`, no LINQ, everything delegates to `IMessageTagService`), the list endpoint
returns `Ok<ResultSet<MessageTag>>`, and — the point of this re-run — **both arms now
correctly return `Ok<ResultSet<Campaign>>`, not `List<Campaign>`, for the campaigns-by-tag
endpoint**, matching the settled rule. Score: **25/25 both arms.** Structurally the two
outputs are close to identical again (same route shape, same `IOptions` prefix, same
`WithHandledException<BusinessException>`), reproducing the "consistent codebase teaches
its own conventions" finding from every prior task-01 run regardless of skill, rev, or
model.

**Task 02 (EVPulse RFID cards).** `score.py --profile product`: baseline created a new
single-file `UsersRfidCardsEndpoints.cs` matching the established local shape of every
other users sub-group (`UsersPaymentsEndpoints.cs`, `UsersReportsEndpoints.cs` — none of
which are split in this product), used `ResultSet<RfidCard>`, `nameof`, and kept the
ownership/already-deactivated checks in the assumed service layer, not the handler — a
correct call this run, unlike the sonnet-5 baseline eight days earlier. Skill arm split
into `UsersRfidCardsApi.cs` + `UsersRfidCardsHandlers.cs` and added `.WithSummary(...)` on
both endpoints. The only rubric gap, on either arm, is `WithSummary`: baseline 0/2, skill
2/2 — the single finding every run of this task has produced, unchanged since 2026-09-18.
Score: **baseline 20/21, skill arm 21/21** (`score.py`'s applicable set for this task
profile, resolving all `REVIEW` checks by hand).

**Task 03 (review).** Hand-scored per `rubric.md`'s "Task 3 scoring" (score.py has no
`.cs` output to read for a review task). Baseline caught all 8 seeded violations —
including the `DbContext`/LINQ-in-handler call and the kebab-case naming call that the
sonnet-5 baseline missed on 2026-09-21 — and, unlike the first opus-5 run three hours
earlier, added **zero** false positives this time: no invented `.Server`-naming claim.
Skill arm also caught all 8, but repeated the one false positive that has now appeared in
three separate runs of this task (2026-09-18, opus-5 run 1, and this run): asserting
`MapWidgets` must return `RouteGroupBuilder`, a claim the task file itself says is false
(the reference library is split roughly evenly between both return types). Score:
**baseline 8/8 hits, 0 FP — skill arm 8/8 hits, 1 FP.** This reverses the "tie" result from
the same-day-earlier opus-5 run: this time the baseline is strictly cleaner than the skill
arm on precision, because the recurring false positive is attached to the skill's own
content, not to model variance — a stronger baseline avoiding an invented claim it was
never told to make, while the skill-primed arm repeats a claim the skill's own reference
implementation contradicts.

**Token/call/wall-clock** (measured the same way as every other 2026-09-21 row: summed
`input_tokens + output_tokens` per agent from the runtime's usage log, `model=claude-opus-5`
confirmed for every call):

| Task | Arm      | LLM calls | Total tok | Wall clock | Note                      |
| ---- | -------- | --------- | --------- | ---------- | -------------------------- |
| 01   | Baseline | 51        | 2,383,054 | 279s       | sums a failed attempt (20 calls, 887,731 tok) + the completed retry |
| 01   | Skill    | 49        | 2,380,734 | 159s       | sums a failed attempt (26 calls, 1,245,960 tok) + the completed retry |
| 02   | Baseline | 27        | 1,195,798 | 152s       | completed on the first attempt |
| 02   | Skill    | 23        | 1,198,569 | 151s       | completed on the first attempt |
| 03   | Baseline | 19        | 613,463   | 84s        | sums a failed attempt (10 calls, 334,018 tok) + the completed retry |
| 03   | Skill    | 6         | 172,238   | 58s        | completed on the first attempt |

Task 01 is now a near-exact tie on tokens (2.383M vs 2.381M) and close on calls (51 vs 49)
— both figures inflated by the same failed-attempt-plus-retry pattern on both arms, so the
totals are not a clean read on relative cost this time; discount this row more than the
others. Task 02 skill arm used marginally *more* tokens than baseline (1.199M vs 1.196M)
despite fewer calls (23 vs 27) — shorter search, longer individual turns, netting out
close to even; wall clock is a near tie (151s vs 152s). Task 03 is the one clean
comparison, unaffected by any retry: skill arm cheaper on every measure (6 calls vs 19,
172k tokens vs 613k, 58s vs 84s) while being the one place its score was strictly worse (1
FP). **The retried-attempt totals on tasks 01 and 03-baseline are a real accounting choice,
not noise to be corrected out**: those tokens were actually spent reaching the artifact
that was scored, so excluding them would understate what this run cost, even though a
quota interruption is not something either arm's design caused.

### Cost

| Run                      | Baseline                        | With skill          |
| ------------------------ | ------------------------------- | ------------------- |
| 01                       | 103,084 tok / 32 calls / 238s   | 88,347 / 27 / 227s  |
| 02                       | 85,219 / 26 / 179s              | 95,245 / 32 / 230s  |
| 03                       | 66,597 / 15 / 125s              | 58,994 / 5 / 82s    |
| 02 (2026-09-21, EVPulse) | 1,473,319 tok / 29 calls / 444s | 482,700 / 10 / 117s |

**2026-09-21b (skill rev `c677a58`, sub-agent claude-opus-5, includes retried-attempt
tokens on 3 of 6 cells — see the run's own section above for which):**

| Task | Baseline                     | With skill                   |
| ---- | ----------------------------- | ----------------------------- |
| 01   | 2,383,054 tok / 51 calls / 279s | 2,380,734 / 49 / 159s        |
| 02   | 1,195,798 / 27 / 152s          | 1,198,569 / 23 / 151s         |
| 03   | 613,463 / 19 / 84s             | 172,238 / 6 / 58s             |

Rows from different hosts do not compare; see "Comparing runs" above. Within the
2026-09-18 host: cheaper with the skill on two runs, dearer on one, and on task 02 dearer
on all three measures. **There is no cost trend here.** At n=1 per cell these numbers are noise, and
the token argument from the top-level README is untested by this pilot rather than
supported by it.

The one ratio worth keeping from that host is task 02, which ran twice with consistent
deltas: roughly +12% tokens and +20 to +29% wall clock for the skill arm, buying
`WithSummary` on both endpoints and the Api/Handlers split. A ratio transfers between
hosts. An absolute does not. Note the other host's task-02 ratio runs the opposite way,
which is itself the point: one number per cell decides nothing.

**2026-09-21 re-run, token detail.** The 2026-09-18 rows come from the host's per-subagent
completion metadata; the rows below are a sum of per-call `input_tokens + output_tokens`.
Different measurements on hosts with very different tool schemas, so they do not compare.
The 2026-09-21 row is measured directly from the
runtime's per-agent usage log, keyed by the sub-agent's own id. **`input_tokens` already
includes `cache_read_tokens` and `cache_write_tokens` as components, not as additions** —
verified row by row (e.g. one call logged `input_tokens=19966`, `cache_read_tokens=10752`,
with the remainder being the turn's fresh tokens). Total tokens per call is therefore
`input_tokens + output_tokens`, nothing else added on top:

| Arm      | LLM calls | Input tok | Output tok | Total tok | Wall clock |
| -------- | --------- | --------- | ---------- | --------- | ---------- |
| Baseline | 29        | 1,458,502 | 14,817     | 1,473,319 | 444s       |
| Skill    | 10        | 471,948   | 10,752     | 482,700   | 117s       |

On this run the skill arm used roughly a third of the calls, a third of the tokens, and a
quarter of the wall clock of the baseline — the token ratio (3.05x) tracks the call ratio
(2.9x) almost exactly, i.e. the gap is explained by call count, not by longer individual
calls. The baseline spent its extra turns re-deriving where to put the new code and how
the existing group's error handling worked (grepping siblings, reading the permission
enum, checking whether the group had `WithHandledException`) — exactly the search the
skill short-circuits by stating the answer. This is one run, on one task, on one repo; it
is a data point for "the skill can be cheaper when it saves a search," not a general cost
claim.

**Same measurement, tasks 01 and 03 (2026-09-21):**

| Task | Arm      | LLM calls | Input tok | Output tok | Total tok | Wall clock |
| ---- | -------- | --------- | --------- | ---------- | --------- | ---------- |
| 01   | Baseline | 22        | 928,410   | 14,611     | 943,021   | 183s       |
| 01   | Skill    | 27        | 1,500,341 | 25,596     | 1,525,937 | 382s       |
| 03   | Baseline | 10        | 256,156   | 4,795      | 260,951   | 54s        |
| 03   | Skill    | 6         | 109,635   | 3,380      | 113,015   | 44s        |

Task 01 goes the other way: the skill arm was **more** expensive on every measure (1.6x the
calls, tokens and wall clock), for a score tied 25/25 — it read the same sibling files the
baseline did, plus `SKILL.md`, plus in this run it also ran an isolated build of
`Messages.Core`/`Messages.AspNetCore` to check the generated code compiled, which the
baseline did not do. Task 03 goes the same direction as task 02: skill arm cheaper on
every measure (0.55x the calls and tokens) _and_ higher-scoring. **No consistent cost
direction across four task/arm pairs measured this way**: cheaper-and-better (03),
cheaper-and-equal (02), dearer-and-equal (01 by rubric, though the skill arm did strictly
more verification work). The only two tasks where the skill arm was ever dearer are the
two where nothing distinguished the score.

**Same measurement, all three tasks, sub-agent model claude-opus-5 (2026-09-21):**

| Task | Arm      | LLM calls | Input tok | Output tok | Total tok | Wall clock |
| ---- | -------- | --------- | --------- | ---------- | --------- | ---------- |
| 01   | Baseline | 30        | 1,778,238 | 22,965     | 1,801,203 | 303s       |
| 01   | Skill    | 36        | 1,872,960 | 18,735     | 1,891,695 | 276s       |
| 02   | Baseline | 25        | 1,237,166 | 11,487     | 1,248,653 | 208s       |
| 02   | Skill    | 17        | 844,100   | 10,986     | 855,086   | 140s       |
| 03   | Baseline | 10        | 326,435   | 7,891      | 334,326   | 111s       |
| 03   | Skill    | 8         | 259,039   | 6,698      | 265,737   | 95s        |

Opus-5 repeats the same pattern seen with sonnet-5: skill arm cheaper on tasks 02 and 03
(fewer calls, fewer tokens), dearer on task 01 by calls and tokens (though marginally
_faster_ in wall clock, meaning shorter individual turns). Combined across both models,
four of six task/arm comparisons run in the skill's favour on cost, two do not, and the
two "dearer" cases are the only ones without a rubric difference to justify the extra
spend either way — the same shape as the sonnet-5-only result, just with double the
sample.

### Requirements for a run to count

- **Keep the arm outputs until scoring is finished.** They are working files, not
  artefacts to commit. A score that cannot be re-derived from them before they are
  discarded has to be re-run, not patched.
- **Score with `score.py` against `rubric.md`**, and resolve every `REVIEW` check by
  reading the diff. Record the resulting `n/25` or `n/24` with the profile, never a bare
  fraction.
- **Ask each arm what it consulted**, and discard a baseline that found the skill. The
  prompt for this is in `prompts.md`. A contaminated baseline scores well, so nothing in
  the output reveals it.
- **Check that the code compiles.** Every rubric check is a convention check, so an arm
  can score full marks on code that does not build. Record the build as its own pass/fail,
  and run it for both arms or neither, since it costs real tokens.
- **Record host, model and date on the row.** Scores compare across hosts; token and
  wall-clock numbers do not.

### Overall

**Across three runs the skill's measured effect is small and concentrated in one place.**
It is zero on a clean, internally consistent codebase, slightly negative on review (one
false positive), and on a drifted product API it supplies two things the surrounding code
cannot: `WithSummary`, which no sibling endpoint has, and the Api/Handlers split for a new
file.

**The 2026-09-21 re-runs corroborate this on task 02, split on task 01, and reverse on task 03.** Task 02: same `WithSummary` gap, plus a new instance of the same failure mode — the
baseline put a business check inline in the handler as LINQ, on a drifted file, exactly
what "handlers hold no business logic" warns against. Task 01: tied again. Task 03: the skill arm went from
"marginally worse" (2026-09-18: equal hits, one extra false positive) to "clearly better"
(2026-09-21: 8/8 vs 5/8, no false positive on either side) — the baseline missed the one
violation the skill calls out by name (`DbContext` in a handler), which is the strongest
single result in either run for "the skill carries knowledge worth having."

So the honest case for this skill is narrow: **it is worth having where the codebase would
teach an agent the wrong thing, and worth little where the codebase already teaches the
right thing.** That is a useful finding for the catalogue as a whole, because it predicts
which future skills will pay: not the ones describing what a clean repo already
demonstrates, but the ones encoding a standard the code has drifted away from.

**The claude-opus-5 re-run adds a second axis: model strength narrows the skill's
advantage.** Same-day, same tasks, same repos, stronger sub-agent model:

- Task 01: identical result to sonnet-5 (25/25 both arms) —
  model-independent.
- Task 02: the skill's edge shrank from 3 rubric points (sonnet-5: 14/17 vs 17/17) to 1
  (opus-5: 16/17 vs 17/17), because the stronger baseline stopped putting business logic
  in the handler on its own. `WithSummary` is the only gap left on any model.
- Task 03: the skill's edge **disappeared and the false positive did not**. Sonnet-5
  baseline: 5/8 hits. Opus-5 baseline: 8/8 hits, unaided — it caught the `DbContext`/LINQ
  violation, the naming convention, everything the skill exists to supply, purely by being
  more thorough about reading sibling code. Both opus-5 arms also produced one false
  positive apiece (the baseline invented a project-naming rule, the skill arm repeated
  2026-09-18's `RouteGroupBuilder`-return claim), so the tie is 8/8-minus-1 on both sides.

Put together: **this skill's measured value is not just codebase-dependent, it is also
model-dependent, and the two interact.** It helps most exactly where a weaker model, on a
drifted codebase, would otherwise imitate the drift or miss a violation a stronger model
would have caught by reading more carefully. As sub-agent models get better at reading
surrounding code unaided, the ceiling this specific skill raises gets easier to reach
without it — which is a reason to keep re-running this harness as models change, not a
reason to drop the skill; task 02's `WithSummary` gap and the false positives on task 03
both persisted regardless of model.

**Caveats.** n≤2 per cell even after the re-run (n=1 on 2026-09-18, n=1 on 2026-09-21, not
pooled — different model/session conditions each day, so treat them as two separate small
samples, not four observations of one distribution). Both arms could read the reference
library, and task 03's prompt pointed at it explicitly, so this measures _skill versus
reading the reference implementation_, not _skill versus nothing_. Both arms in the same
run were on the same model. The task-02 and task-03 findings are the ones worth trusting
first, because they are the only ones where a mechanism is visible rather than just a
number: the sibling code demonstrably cannot supply either answer, and the skill visibly
does.

**The 2026-09-21b re-run (`c677a58`, opus-5, n=3) is now the third independent measurement
and holds the same shape as the first two.** Task 01: tied again, now 25/25 both arms under
the settled collection rule (the earlier 24/25 and 25/25 splits were an artefact of the old
rule's ambiguity on the campaigns-per-tag endpoint, not a real difference — see the rev's
commit message). Task 02: same single `WithSummary` gap it has found on every rev, every
model, every day this task has been run — the most reproducible single finding in the whole
harness. Task 03: baseline hit 8/8 with **no** false positive this time (better than the
same-day-earlier opus-5 run, where it invented a project-naming claim), while the skill arm
repeated its own recurring false positive for the third time across three separate runs —
the one place in the harness where a specific defect is attributable to the skill's content
rather than to model variance, and worth fixing in `SKILL.md` directly rather than re-running
around. Token/call totals on two of three tasks this run include a failed, quota-interrupted
attempt summed with its retry (flagged per-cell above); treat those two rows as noisier than
usual, and treat task 03's clean numbers (no retry on either arm) as the more trustworthy cost
comparison from this run.

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
