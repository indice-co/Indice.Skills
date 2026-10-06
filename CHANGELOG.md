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
- Added the `indice-messaging` skill (`common/indice-messaging/`): what Indice Messaging
  is, how a campaign becomes a delivered message, and how to stand up the API/UI host and
  the delivery worker in a new solution. `SKILL.md` carries the model and the known traps;
  `setup.md` is the step-by-step; `reference.md` holds option defaults, configuration keys,
  endpoints, queues and providers. Verified against Indice.Platform 8.57.x and the
  `indice.messaging` templates.
- Added `evals/indice-web-api/`: three tasks and a rubric for measuring whether the
  skill changes agent output.
