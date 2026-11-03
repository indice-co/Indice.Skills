---
name: kmp-source-set-placement
description: Choose the correct Kotlin Multiplatform source set and dependency scope for code, resources, and tests. Use when adding, moving, or reviewing declarations or dependencies across common, iOS, or Android source sets. Do not use when placement and dependency boundaries are already fixed.
---

# Goal

Place each declaration, dependency, resource, and test in the broadest existing source set serving exactly its intended targets.

# Use when

Adding or moving shared/platform code, dependencies, resources, tests, or source-set relationships.

# Do not use when

The affected source set is predetermined and no target or dependency boundary changes.

# Required inputs

The intended target set and the behavior or dependency being placed.

# Inspect before editing

Inspect `settings.gradle.kts`, `gradle/libs.versions.toml`, the affected build file, and existing source directories. Consult the official project-structure, hierarchy, and dependency documentation.

# Decision rules

- Use `commonMain`/`commonTest` only when valid for every declared target.
- Use existing `iosMain`/`iosTest` for behavior shared by the iOS targets, and Android source sets for Android-only behavior.
- Do not create an intermediate source set for a single one-off declaration.
- Declare dependencies where consumed and verify support for every target of that source set.
- Prefer existing repository dependencies; manage additions in the version catalog.
- Check for an existing abstraction or KMP library before adding platform adapters.
- Prefer an injected common interface for substantial behavior; reserve `expect`/`actual` for small bindings.

# Allowed changes

Affected source files/directories, the affected module build file, matching tests, and necessary version-catalog aliases.

# Prohibited changes

Platform API imports in common code, duplicated equivalent Apple implementations, silent repository/prerelease additions, target removal, or unrelated toolchain upgrades.

# Verification

Run the narrowest compile and test tasks for each affected host-valid target. Never claim Apple verification from a non-macOS host.

# Stop conditions

Stop if the intended target set is genuinely ambiguous, required library target support cannot be verified, or placement requires an architectural expansion not authorized by the request.

# Completion report

Report intended targets, chosen source set, rejected broader/narrower placements, dependency placement, tests/commands, and unverified targets.
