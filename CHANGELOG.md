# Changelog

All notable changes to this skill set are recorded here. Releases are tagged
with SemVer; consuming repos pin to a tag or commit.

## [Unreleased]
- Initial repository layout: `common/`, `instructions/`, `prompts/`, `templates/`, `CONTRIBUTING.md`.
- Added the `indice-web-api` skill: endpoint conventions for Indice.Platform feature
  libraries and for product APIs built on them. Indice.Platform is the reference
  implementation; product APIs deviate only where there is a structural reason, and
  the skill lists the known drift to write away from rather than copy. Named `indice-web-api` rather than
  `dotnet-web-api` to avoid confusion with the upstream `dotnet/skills` `dotnet-webapi`
  skill, which it treats as a baseline and overrides in a documented set of cases.
- Added `evals/indice-web-api/`: three tasks and a rubric for measuring whether the
  skill changes agent output.
- Added ten Kotlin Multiplatform skills under `common/indice-kmp/`: source-set placement,
  platform boundaries, shared API review, iOS interop, Compose Multiplatform features,
  test matrix, build triage, toolchain upgrades, KMP library selection, and Android
  emulator QA.
