---
name: dotnet-conventions
description: >
  Use when writing or reviewing C#/.NET backend code at Indice: project structure,
  DI, configuration, logging, and error handling conventions. Prefer Indice.Platform
  primitives before adding new abstractions.
---

# .NET conventions

## Purpose

Company-wide backend standard for C#/.NET services. Read this before creating or
changing .NET code. For generic .NET guidance, the pinned `dotnet/skills` baseline
applies; this skill only records where Indice differs or adds to it.

## Guardrail

Before proposing a new implementation, search the relevant Indice library
(see the `indice-platform` skill) for existing functionality. Only write new code
if nothing suitable exists, and say which library you checked.

## Target framework & language

- Target framework: TODO
- Language version / nullable reference types: TODO

## Solution & folder layout

- TODO

## Naming

- TODO

## Async guidelines

- TODO

## Dependency injection

- TODO: registration patterns

## Configuration

- Use `IOptions<T>`; TODO

## Logging

- Structured logging; TODO

## Error handling

- HTTP responses, problem-details and endpoint exception policy live in the `indice-web-api` skill. Do not restate them here.
- TODO: non-HTTP exception policy (background workers, message handlers).

## Examples

TODO: minimal, real snippets that show the preferred pattern.
