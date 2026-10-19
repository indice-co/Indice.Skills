---
# Must match the folder name. Prefix with the product to avoid clashing with installed Indice skills.
name: <product>-<area>
description: >
  Use when working on <product/area>: <domain terms, business rules, key
  integrations>. Read before implementing features in this area. Builds on the
  Indice skills (<indice-skill-a>, <indice-skill-b>) and does not repeat them.
---

# <Skill title>

## Purpose
One paragraph: what this skill covers and when to use it.

## Builds on
- `<indice-skill>`: what it already covers, so this skill does not restate it.

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
