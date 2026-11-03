---
name: kmp-toolchain-upgrade
description: Upgrade Kotlin, Gradle, Android Gradle Plugin, Compose Multiplatform, KSP, Kotlin/Native, and related tooling as a compatible set. Use only for an explicit upgrade request or confirmed compatibility failure; do not activate for ordinary build errors.
---

# Goal

Move the KMP toolchain to a stated compatible version set without mixing in unrelated feature or architecture work.

# Use when

The user explicitly invokes this skill for an upgrade, or diagnosis proves a version compatibility failure and the user authorizes migration.

# Do not use when

A build merely fails, a single library is being added, or no toolchain change was requested/confirmed.

# Required inputs

Current version set, requested target versions or constraint, last green baseline, host/CI capabilities, and rollback point.

# Inspect before editing

Inspect all build/version files and module topology, then read the official Kotlin Multiplatform compatibility guide, Compose compatibility notes, AGP migration guidance, and relevant release/migration notes. Confirm whether the Android KMP library uses `com.android.kotlin.multiplatform.library`; do not mechanically replace plugin IDs.

# Decision rules

State the target compatibility set before editing. Upgrade one compatibility layer at a time, separate required DSL/source migrations from version changes, and validate after each stage. Treat Kotlin, Gradle, AGP, Compose, KSP, Kotlin/Native, JDK, and Xcode as a coordinated set.

# Allowed changes

Version catalog, wrapper, plugin/build DSL, and mandatory source migrations directly required by the target set.

# Prohibited changes

Feature work, architectural refactors, disabled targets, speculative upgrades, new repositories, or cache deletion used to mask incompatibility.

# Verification

Establish/document baseline; after each stage run the narrowest relevant task; at completion run all host-valid target compilation/tests and record host-restricted gaps.

# Stop conditions

Stop when official compatibility data does not support the desired set, the baseline is already broken for another cause, or required host tooling/authorization is missing.

# Completion report

Record previous/final versions, mandatory source changes, remaining deprecations, commands/results, unverified targets, and rollback point.
