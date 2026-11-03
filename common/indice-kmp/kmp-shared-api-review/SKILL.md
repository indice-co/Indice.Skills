---
name: kmp-shared-api-review
description: Review public Kotlin Multiplatform APIs for platform leakage, coroutine ownership, cancellation, error mapping, serialization stability, Swift usability, and compatibility. Use during review or before exposing shared APIs to platform applications or external consumers.
---

# Goal

Keep shared APIs portable, lifecycle-safe, compatible, and practical for Kotlin and Swift consumers.

# Use when

Reviewing changed public declarations or preparing shared APIs for platform/external consumption.

# Do not use when

Changes are private implementation details with no boundary or compatibility effect.

# Required inputs

Affected public declarations, known consumers, compatibility expectations, and export method.

# Inspect before editing

Inspect declarations, all consumers, and the declared targets/toolchain, and consult the relevant Swift export, interop, coroutine, serialization, and compatibility documentation.

# Decision rules

Check for platform/framework type leakage, mutable implementation types, hidden dispatcher choice, ownerless scopes, swallowed cancellation, undocumented Swift consumption of `suspend`/`Flow`, poorly exported generics, unmapped exceptions, serialization changes, export ambiguity, nullability inconsistency, and migration requirements.

# Allowed changes

Minimal API corrections, adapters, annotations, documentation, compatibility tests, and migration notes.

# Prohibited changes

Unrequested wholesale API redesign, silent wire-format breaks, platform types in common contracts, or exceptions crossing boundaries without an explicit contract.

# Verification

Compile every affected target available on the host, exercise platform consumers where possible, and test compatibility-sensitive serialization/error/cancellation behavior.

# Stop conditions

Stop when required compatibility guarantees or consumer migration policy are unknown and materially change the correction.

# Completion report

For each finding report declaration, affected consumer, concrete failure mode, minimal correction, and compatibility impact; include commands and unverified targets.
