---
name: kmp-build-triage
description: Diagnose Kotlin Multiplatform Gradle sync, metadata/platform compilation, Kotlin/Native linking, Xcode integration, Compose compiler, and dependency-resolution failures. Use when sync or a build task fails; do not use for a planned toolchain upgrade.
---

# Goal

Identify the first causal build failure and apply the smallest verified correction.

# Use when

Gradle sync, compilation, linking, packaging, tests, framework embedding, or Xcode integration fails.

# Do not use when

The user requested a planned upgrade without a current failure.

# Required inputs

Exact command/IDE operation, failing task, first causal exception, relevant error block, and host OS.

# Inspect before editing

Record Java/Gradle/Kotlin/AGP/Compose/Xcode versions and declared targets from the build files, and consult the relevant official build, compatibility, Android, or iOS documentation. Inspect current build files before applying examples.

# Decision rules

Classify the failure as settings/plugin resolution, source-set configuration, dependency metadata, common compilation, platform compilation, native linking, packaging, runtime, or test. Reproduce with the narrowest task, change one bounded cause, rerun it, then run the nearest neighboring validation.

# Allowed changes

The smallest configuration/source/dependency correction proven relevant to the causal error and tests guarding it.

# Prohibited changes

Cache purges as a first response, broad upgrades, repository changes, compiler suppression, disabled targets, generated-file edits, or dependency replacement without demonstrated incompatibility.

# Verification

Show the failing task before and after the correction and run the closest related task.

# Stop conditions

Stop when the error cannot be reproduced, required logs are unavailable, host-only tooling is missing, or correction requires an explicit migration.

# Completion report

Report causal error, classification, evidence, bounded correction, commands/results, and remaining unverified targets.
