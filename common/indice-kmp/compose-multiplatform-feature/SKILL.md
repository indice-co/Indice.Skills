---
name: compose-multiplatform-feature
description: Implement or review screens and components intentionally shared through Compose Multiplatform. Use for shared state, resources, lifecycle, accessibility, previews, adaptive behavior, and common UI tests. Do not use for native SwiftUI/UIKit or platform-owned screens.
---

# Goal

Build shared Compose UI that follows repository state, resource, lifecycle, accessibility, and testing conventions on Android and iOS.

# Use when

Adding or changing UI owned by shared `commonMain` code.

# Do not use when

The requested screen is intentionally native SwiftUI/UIKit or Android-only UI.

# Required inputs

Feature behavior, UI states/events, navigation ownership, platform-specific differences, and accessibility expectations.

# Inspect before editing

Inspect existing shared UI/state/resources/tests and the relevant Compose Multiplatform documentation (layout, resources, lifecycle, navigation, accessibility, platform, testing). Verify APIs against the version catalog/build files.

# Decision rules

Separate state/events from rendering; keep platform services behind interfaces; use shared resources; preserve semantics and keyboard/pointer behavior where relevant; follow existing navigation/lifecycle conventions; keep intentional native UI native.

# Allowed changes

Shared composables, state/event contracts, multiplatform resources, previews, platform adapters needed by the feature, and common/platform UI tests.

# Prohibited changes

Platform resource lookup in common UI, UI-owned global scopes, platform APIs in common composables, replacing native UI merely to reduce file count, or unrequested navigation/toolchain changes.

# Verification

Compile shared metadata and Android, run applicable common/Android tests, and verify iOS on macOS. Add common UI tests for shared semantics and platform tests where rendering/input/lifecycle differ.

# Stop conditions

Stop when UI ownership, navigation contract, or a material platform divergence needs a product decision.

# Completion report

Report shared/platform ownership, states/events/resources/accessibility handled, tests/commands, and unverified targets.
