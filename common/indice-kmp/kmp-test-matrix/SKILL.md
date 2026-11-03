---
name: kmp-test-matrix
description: Add and run tests for Kotlin Multiplatform changes across common and affected platform source sets. Use for shared behavior, platform implementations, serialization, persistence, networking, coroutines, or Compose UI. Discover real Gradle tasks and report every target not executed.
---

# Goal

Provide evidence that changed behavior works in shared code and every affected platform implementation.

# Use when

Adding tests, defining a verification matrix, or validating behavior across targets.

# Do not use when

Only static documentation or non-executable metadata changed.

# Required inputs

Changed production source sets, affected behaviors, declared targets, and current host restrictions.

# Inspect before editing

Inspect declared targets, source-set relationships, and current tests, and use `gradlew tasks --all` rather than guessing task names. Consult the official guides on running multiplatform tests, and on Compose testing when shared UI is affected.

# Decision rules

- Put deterministic shared behavior in `commonTest`.
- Add platform tests when an actual implementation, filesystem/database behavior, native bridge, lifecycle, threading, permission, or serialization differs.
- Use fakes for time, dispatchers, storage, network, and platform services.
- Use `runTest` where supported, inject dispatchers, test cancellation/ownership, and avoid arbitrary delays.
- Use common Compose UI tests for shared semantics; retain platform tests for rendering/input/lifecycle differences.

# Allowed changes

Matching test source sets, fixtures/fakes, minimal test dependencies, and production seams required for deterministic tests.

# Prohibited changes

Disabling targets/tests, inventing task names, treating metadata compilation as target proof, or hiding host restrictions.

# Verification

Run the narrowest affected test tasks followed by adjacent compile tasks. Record actual results.

# Stop conditions

Stop if a required target needs unavailable hardware/OS/tooling or deterministic testing needs an unapproved redesign.

# Completion report

Return a matrix with Target, Compilation, Unit tests, Integration/UI tests, and Reason not run, populated only from observed results.
