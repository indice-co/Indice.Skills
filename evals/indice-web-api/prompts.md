# Prompts

The exact text fed to each arm. The task files describe *what* is being measured;
this file is what you paste. They are not the same: every run carries scaffolding
(where to write output, what not to touch) that the task files leave out, and
without it recorded the runs are not reproducible.

Two profiles:

- **Repo profile** — the agent can read a checkout and write files. What the
  recorded runs used.
- **Chat profile** — a model in a browser or an API call with no filesystem. Only
  task 03 works here, and it is the *better* control. See "Why the chat profile
  matters" at the end.

Arm B is always arm A with a preamble prepended and nothing else changed. Keep it
that way: if you reword the task for one arm, reword it for both.

---

## Arm B preamble

**Repo profile** — point at the file:

> First, read this skill file in full and follow it for the work below. It describes how your organisation builds HTTP endpoints:
>
> `<path to>/common/indice-web-api/SKILL.md`

For task 03 replace the last clause with: *"…and it is the standard you are reviewing against."*

**Chat profile** — paste the skill instead, since there is no file to read:

> Below is your organisation's skill describing how it builds HTTP endpoints. Read it in full and follow it for the work that comes after.
>
> ```markdown
> <paste the entire contents of common/indice-web-api/SKILL.md>
> ```

Do not summarise the skill when pasting. A summary is a different treatment and
will not compare against the recorded runs.

---

## Task 01 — new resource (repo profile only)

Substitute your own checkout path.

> You are working in the repository at `<path to>/Indice.Platform`.
>
> In `src/Indice.Features.Messages.AspNetCore`, add a new **message tags** resource to the management API. A tag has an `Id` (Guid), a `Name`, a `Description`, and a `CreatedAt`. It needs:
>
> - list tags, with paging, sorting and a free-text search
> - get one tag by id
> - create a tag
> - update a tag
> - delete a tag
> - list the campaigns currently using a given tag
>
> It should sit alongside the other management resources and show up in the same OpenAPI document and generated client as they do. Requires the same scope and management permission as distribution lists.
>
> Add the service layer too: assume a store/persistence method exists for each operation and call it. You do not need to implement persistence.
>
> Where files go: do NOT modify the repository, it must be left clean. Write every file you would have created into this output directory, preserving the relative path you would have used under the repo:
>
> `<output dir>`
>
> A file intended for `src/Indice.Features.Messages.AspNetCore/Endpoints/Foo.cs` goes to `<output dir>/src/Indice.Features.Messages.AspNetCore/Endpoints/Foo.cs`. For an existing file you would have edited, write the changed region to a `.patch.md` file at the same relative path, showing before/after.
>
> When done, summarise the files you produced and the decisions you made.

## Task 02 — add endpoints (repo profile only)

Instantiate per `tasks/02-add-endpoint.md`: your product, your resource area, your
two endpoints. Measure the control with `score.py --control` first. The recorded run used:

> Work in the repository at `<path to your product checkout>`.
>
> In the `<product>` management API, add two endpoints to the existing `<area>` area:
>
> 1. A paged, searchable list of `<child entity>` for a `<parent entity>`.
> 2. An endpoint that `<mutating action>`, taking `<a short field>` in the body. It should fail cleanly if `<ownership condition>`, or if `<already-in-target-state condition>`.
>
> Both should require the same permission as the other `<neighbouring>` operations, and appear in the management OpenAPI document.
>
> Assume the repository and service methods you need exist; call them.
>
> Where files go: do NOT modify the repository, it must stay clean. Write your output into this directory:
>
> `<output dir>`
>
> For a NEW file, preserve the repo-relative path you would have used. For an EXISTING file you would have edited, write the changed region to a `.patch.md` file at the same relative path, with enough before/after context to make the insertion point unambiguous.
>
> Verify with `git status` before you finish that the repository is still clean.
>
> When done, summarise the files you produced and the decisions you made.

## Task 03 — review (both profiles)

Self-contained. Paste the two code blocks from `tasks/03-review.md` verbatim
between the first line and the last.

> Review this pull request for a new feature library resource. Flag anything that does not match how we build endpoints.
>
> ```csharp
> <WidgetEndpoints.cs, verbatim from tasks/03-review.md>
> ```
>
> ```csharp
> <WidgetHandlers.cs, verbatim from tasks/03-review.md>
> ```
>
> Present your review as a numbered list of findings. For each finding, state what is wrong and what it should be instead. At the end, list every file or directory you consulted.

**Repo profile only**, add: *"Do not modify any repository."* and a path to write
the review to.

**Do not** add "you may read `<reference library>`". The recorded runs tried that
and it decided the result: the baseline read the library and scored full marks, so
the run measured the skill against looking it up rather than against not knowing.

---

## Recording a run

For each arm, capture:

- the rubric score (`rubric.md`; `score.py --profile library|product` automates about half and flags the rest `REVIEW`)
- tokens, tool calls, wall clock, if your tool reports them
- **what the agent consulted** — ask it afterwards, verbatim:

  > During your run, did you read or consult any file under `<path to Indice.Skills>`, or any other conventions document outside the repository you were working in? Yes or no. If yes, name the files.

That last step is not optional. In the recorded runs a baseline given no pointer
went looking for conventions, found this skills repo on disk, and reviewed against
the very skill it was meant to be a control for. It scored well, so nothing in the
output looked wrong; only its own account of its sources revealed it. **Discard any
baseline that consulted the skill.**

## Why the chat profile matters

The local harness could not build a true control. Three attempts at a task 03
baseline — pointed at the reference library, given no pointer, and with the skills
repo explicitly out of bounds — all scored 8/8, because the agent found a reference
on disk every time. On a developer machine "skill versus nothing" does not exist.

A chat-profile model has no filesystem. It cannot find the reference library, it
cannot find this repo, and it reviews from the diff plus whatever the skill tells
it. **That is the control the repo profile cannot produce**, and it measures the
case the skill is actually for: a reviewer reading a PR in a browser, a CI check,
an agent working somewhere else.

So run task 03 chat-profile first when trying a new tool. If the skill is worth
anything for review, that is where it shows, and the repo-profile runs already
suggest it will not show anywhere else.
