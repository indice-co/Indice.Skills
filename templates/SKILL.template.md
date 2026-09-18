---
name: <short-kebab-case-name>          # e.g. billing-domain
description: >
  Use when working on <product/area>. Covers <domain terms, business rules,
  key integrations>. The agent should read this before implementing features in
  this area, and prefer the referenced Indice libraries over new code.
applyTo:                                # optional: auto-apply as instructions
  - "src/Billing/**"
---

# <Skill title>

## Purpose
One paragraph: what this skill covers and when to use it.

## Domain glossary
- **Term** — definition and how it is used.

## Business rules & invariants
- Rule 1 (and why it exists).
- Rule 2.

## Architecture
- Modules/services and how they relate. Where to add new code.

## Integrations & libraries
- Uses [Indice.Platform](https://github.com/indice-co/Indice.Platform) for <X>.
- External systems: <system> via <contract>.

## Do / Do not
- Do: ...
- Do not: ...

## Examples
Minimal, real snippets that show the preferred pattern.
