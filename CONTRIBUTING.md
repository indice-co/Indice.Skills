# Contributing to Indice.Skills

This repository is the single source of truth for Indice's shared AI skills,
instructions, and prompt templates.

## How to contribute
1. Open a PR against `main`.
2. Every PR that touches a skill updates its front-matter `description` (this is
   what the agent uses to decide when to load it) and, where relevant, `CHANGELOG.md`.
3. `CODEOWNERS` routes the PR to the owner of that domain (.NET, Angular, Azure,
   Indice libraries).

## Review bar
A skill is merged only if it is:
- **Accurate**: verified against the current library / framework version.
- **Concise**: skills are read by the model on every load, so brevity saves tokens.
- **Non-overlapping**: it does not restate an existing skill or an imported baseline.

## Imported (vendored) skills
- Pin to a specific tag/commit; never live-link upstream.
- Import selectively: only what a repo actually uses.
- Keep the upstream license / notice alongside vendored files (all current sources are MIT).
- Where an Indice skill and an imported skill disagree, the Indice skill wins.

## Freshness
Skills are reviewed quarterly and whenever a referenced library ships a breaking
change. Stale guidance is worse than none.

## Reporting a bad result
If a skill led the agent to a wrong or inconsistent result, open an issue with
the skill name, the prompt, and what went wrong.
