---
name: kotlin-multiplatform-libraries-expert
description: Discover, compare, upgrade, audit, or add Kotlin Multiplatform libraries with verified coordinates, stable versions, and target support. Use when KMP dependency metadata matters; do not use for general project setup or build troubleshooting.
---

# Goal

Select exact KMP coordinates and the newest suitable stable version that supports every required project target.

# Use when

Finding a library, validating coordinates/version/target support, comparing KMP dependencies, or auditing a shared dependency.

# Do not use when

No library metadata decision is involved, the dependency is Android-only by design, or the task is general Kotlin/Gradle troubleshooting.

# Required inputs

Capability or known coordinates, required targets/source set, stability policy, and project Kotlin/toolchain versions.

# Inspect before editing

Inspect declared targets, the version catalog, and the consuming source set, then query the klibs.io MCP server when available or the exact `https://klibs.io/package/<group>/<artifact>` page. Use a project page only to locate package coordinates.

# Decision rules

- Treat klibs.io package metadata as primary for KMP target support and versions.
- Recommend the newest stable release unless prereleases are explicitly requested.
- Verify every declared target for `commonMain`; verify only the actual target set for narrower source sets.
- Prefer exact package coordinates and capture release date/Kotlin or build-tool compatibility when available.
- Keep shortlists short and compare only verified target-compatible libraries.
- If klibs.io lacks the library, state that it is unverified and do not invent a version.

# Allowed changes

Version-catalog version/library aliases and the consuming source-set dependency declaration after approval implied by the task.

# Prohibited changes

Guessed versions/coordinates, JVM-only artifacts in common code, unrequested prereleases/repositories, or architecture/source-set decisions made without the placement rules.

# Verification

Resolve the dependency and compile every host-valid target of its source set; run affected tests. Provide the klibs.io package link used.

# Stop conditions

Stop when required target/version metadata cannot be verified or adding the dependency requires a new repository/prerelease not authorized by the user.

# Completion report

Report coordinates, version/release date, verified targets, source-set placement, Gradle catalog/dependency changes, source link, commands, and unverified targets.
