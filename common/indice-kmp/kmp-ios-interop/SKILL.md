---
name: kmp-ios-interop
description: Design, implement, or review Kotlin-to-Swift and Objective-C interop for the shared iOS framework, SwiftUI/UIKit integration, coroutine and Flow bridging, framework packaging, and native error mapping. Use when Swift directly consumes shared APIs.
---

# Goal

Provide a stable, idiomatic Swift-facing boundary to the shared Kotlin framework and keep iOS packaging/integration reproducible.

# Use when

Changing framework exports, the Compose entry view controller (e.g. `MainViewController`), SwiftUI/UIKit embedding, Swift-consumed APIs, callbacks, coroutines/Flow, or Xcode integration.

# Do not use when

The change remains entirely inside common/Android code and does not affect iOS consumers or packaging.

# Required inputs

Swift consumer, exported Kotlin declarations, lifecycle/cancellation/error expectations, framework distribution method, and deployment target.

# Inspect before editing

Inspect declared targets/toolchain, the shared framework configuration, and the iOS app's Xcode project, then consult the official iOS integration, SwiftUI/UIKit, direct integration, Swift export, and compatibility documentation. Verify APIs against the catalog and Xcode project.

# Decision rules

Prefer small non-generic Swift-facing facades; define ownership and cancellation for asynchronous work; map failures intentionally; avoid exposing implementation collections/types; keep framework base name/package wiring consistent; use direct Gradle/Xcode integration already established unless migration is explicitly requested.

# Allowed changes

Swift-facing adapters/facades, iOS source-set implementations, SwiftUI/UIKit bridge code, framework exports, and focused Xcode configuration required by the feature.

# Prohibited changes

Unrequested CocoaPods/SwiftPM migration, platform types leaking into common APIs, uncancellable background work, raw exception contracts, or claims of iOS verification without macOS/Xcode.

# Verification

On macOS compile the framework, build the iOS app, and run affected simulator tests. On other hosts run common/Android checks and explicitly defer iOS execution.

# Stop conditions

Stop when Apple signing, distribution method, binary compatibility, or lifecycle ownership requires a user decision.

# Completion report

Report exported API/consumer changes, ownership/cancellation/error behavior, packaging changes, commands/results, and host-restricted verification.
