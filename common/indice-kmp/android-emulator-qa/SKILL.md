---
name: android-emulator-qa
description: Validate Android feature flows in an emulator with adb-driven launch, input, UI-tree inspection, screenshots, and Logcat capture. Use for Android runtime QA; do not use as proof of iOS or common target behavior.
---

# Goal

Reproduce and verify an Android flow on a selected emulator with inspectable UI, screenshot, and log evidence.

# Use when

Running Android feature QA, reproducing UI issues, or collecting emulator diagnostics.

# Do not use when

Only unit/metadata compilation is needed, no emulator is available, or the requested proof concerns iOS.

# Required inputs

Application ID, launch activity/flow, expected result, build variant, and selected emulator serial.

# Inspect before editing

Discover install tasks with `gradlew tasks --all`, list devices with `adb devices`, and resolve the launch activity before starting it.

# Decision rules

- Build/install the narrow target variant, then launch with an explicit `adb -s <serial>` command.
- Derive tap coordinates from `uiautomator` bounds, never from screenshots.
- If a node is absent and a scrollable container exists, scroll and re-dump once before concluding it is missing.
- Dump the UI tree with `adb -s <serial> shell uiautomator dump` and read the XML; tap the center of the target node's `bounds`.
- Clear Logcat before the flow; capture app-process and crash logs after it.

# Allowed changes

Test-only app configuration or semantics needed to make the requested flow observable, when in scope. QA artifacts should go to an ignored temporary/output directory.

# Prohibited changes

Guessing coordinates, driving an unspecified device, treating screenshots as the UI hierarchy, suppressing crashes, or claiming non-Android verification.

# Verification

Confirm the activity resolves, execute the flow, inspect a fresh UI tree, capture a screenshot, and review filtered and crash Logcat output.

# Stop conditions

Stop when no authorized emulator/device is available, app installation/launch fails for a build cause outside QA scope, or the flow requires credentials/destructive external actions not provided.

# Completion report

Report serial/variant/package/activity, steps and observed UI state, screenshot/log paths, failures, and the exact commands used.
