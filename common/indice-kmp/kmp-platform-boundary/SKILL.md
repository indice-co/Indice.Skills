---
name: kmp-platform-boundary
description: Design and implement a shared Kotlin API over Android or iOS platform services. Use for permissions, storage, filesystem access, notifications, sensors, native SDKs, lifecycle, or threading boundaries. Prefer existing KMP libraries or injected interfaces; use expect/actual only for small bindings.
---

# Goal

Expose platform capabilities through a small, testable common contract without leaking Android or Apple types.

# Use when

Shared code needs a native service, API, lifecycle hook, permission, or SDK.

# Do not use when

The feature is intentionally platform-only or no platform boundary is involved.

# Required inputs

Inputs/outputs, supported platforms, permissions, lifecycle owner, threading/cancellation semantics, and expected failures.

# Inspect before editing

Search for existing abstractions/dependencies and read the official documentation on platform APIs and `expect`/`actual` declarations.

# Decision rules

Use this order: existing repository abstraction; approved dependency; established KMP library; injected common interface with platform implementations; small `expect`/`actual` binding; otherwise keep the feature platform-only. Define error mapping, availability, unsupported behavior, lifecycle ownership, dispatcher expectations, cancellation, and a test-double strategy.

# Allowed changes

Small common contracts, injected platform implementations, factories/wiring, and corresponding common/platform tests.

# Prohibited changes

Platform types in common APIs, common singleton initialization of UI-bound services, swallowed cancellation, Boolean-only error hiding, or an `expect class` where a small interface/factory suffices.

# Verification

Test the common contract with fakes and platform implementations on every host-valid affected target. Exercise permission denial, unavailable services, cancellation, and mapped failures where applicable.

# Stop conditions

Stop when SDK requirements, permissions, lifecycle ownership, or unsupported-platform behavior need a product decision.

# Completion report

Report the boundary, rejected alternatives, lifecycle/thread/cancellation contract, error mapping, tests, commands, and unverified platforms.
