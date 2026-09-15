# Indice library lookup

Use this file as the quick-reference companion to Topic 1.4 in the main [README](../README.md). It keeps the high-level catalog short while giving authors a concrete place to start when they need a focused skill for an Indice-maintained library.

## Indice.Platform

Repository: [indice-co/Indice.Platform](https://github.com/indice-co/Indice.Platform)  
Primary reference: the repo [README](https://github.com/indice-co/Indice.Platform/blob/main/README.md) plus the package groups under `src/`.

Suggested first-wave skills for the monorepo:

- **`indice-platform-core`** — foundational backend packages such as `Indice.Common`, `Indice.AspNetCore`, `Indice.EntityFrameworkCore`, `Indice.Hosting`, `Indice.Services`, and `Indice.Functions.Builder`. Use when building shared ASP.NET/Core infrastructure or cross-cutting primitives.
- **`indice-platform-identity`** — the identity/authentication slice (`Indice.Features.Identity.*`, activity/sign-in logging, Apple and GovGR auth providers). Use when working on sign-in, admin UI, end-user identity UI, or identity server extensions.
- **`indice-platform-messaging`** — the messaging slice (`Indice.Features.Messages.*`, workers, and Azure worker integrations). Use when a product sends campaigns, notifications, or background-delivered messages.
- **`indice-platform-agents-and-cases`** — the agents and case-management slice (`Indice.Features.Agents.*`, `Indice.Features.Cases.*`, `Indice.Features.Cases.Workflows`). Use when workflows, operational back-office cases, or AI-agent orchestration are in scope.
- **`indice-platform-risk-and-multitenancy`** — the risk, multitenancy, and related platform features (`Indice.Features.Risk.*`, `Indice.Features.Multitenancy.*`, plus adjacent feature packs such as media and government integrations when they appear in the same solution). Use when tenant isolation, fraud/risk scoring, or supporting feature modules shape the design.

If a team repeatedly uses only one of these slices, split it further into package-level skills and link directly to the relevant package README or changelog from the skill.

## Indice.Angular

Repository: [indice-co/Indice.Angular](https://github.com/indice-co/Indice.Angular)  
Primary reference: the repo [README](https://github.com/indice-co/Indice.Angular/blob/main/README.md) and the `projects/` libraries.

Suggested first-wave skills:

- **`indice-angular-auth`** — `@indice/ng-auth` for OIDC flows, guards, interceptors, and session-aware Angular features. Mention `@indice/ng-config` whenever runtime configuration is part of the auth bootstrap.
- **`indice-angular-components`** — `@indice/ng-components` for reusable UI, Tailwind integration, layout/form building blocks, and auth-aware components.
- **`indice-angular-config`** *(optional, narrower follow-up)* — `@indice/ng-config` for environment-driven runtime configuration when that topic becomes large enough to deserve its own skill.

## Indice.Cryptography

Repository: [indice-co/Indice.Cryptography](https://github.com/indice-co/Indice.Cryptography)  
Primary reference: the repo [README](https://github.com/indice-co/Indice.Cryptography/blob/main/README.md).

Suggested first-wave skills:

- **`indice-cryptography`** — the broad library skill for PSD2 compliance, certificate management, ASN.1/X.509 work, and cryptographic primitives.
- **`indice-cryptography-http-signing`** *(optional, narrower follow-up)* — HTTP message signing, request integrity, and certificate-backed API authentication when integrations need that protocol in detail.

## Authoring rule

When you create one of the skills above, keep the skill focused on **when to load it, which package(s) to inspect first, and which README/package docs the agent should read next**. The goal is fast library reuse, not duplicating the upstream documentation word-for-word.
