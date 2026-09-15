# Indice.Skills

> A shared, version-controlled home for the AI **skills**, **instructions**, and **prompt templates** we use across the company to work with AI coding agents (GitHub Copilot, Claude, and similar tools).

## Purpose

We adopted AI tooling to move faster and ship better software. In practice, though, every developer was re-discovering the same context on every task: *how we structure a .NET service, which Angular patterns we follow, which Azure services we standardize on, and — most importantly — which Indice libraries already solve a problem before anyone writes a single line of new code.*

That repeated context has two costs:

1. **Wasted tokens.** The same background is re-typed into every chat, re-read by the model on every request, and paid for again and again.
2. **Inconsistent output.** Without shared guardrails, two developers ask the same question and get two different architectures.

**Indice.Skills solves both.** It is a single source of truth for the knowledge an AI agent needs to behave like an experienced Indice engineer. By packaging that knowledge into reusable **skills** (loaded on demand) and **instructions** (applied automatically), we:

- **Cut token costs** — the agent loads only the relevant skill for the task instead of a wall of context on every prompt.
- **Increase consistency** — everyone builds on the same conventions and the same libraries.
- **Avoid re-inventing the wheel** — the agent is told to check [Indice&#39;s existing libraries](https://github.com/indice-co) *before* proposing new code.
- **Onboard faster** — new team members (and their agents) inherit institutional knowledge from day one.

This README describes **what** should live here, **how** it is distributed and maintained, and **how** teams create their own project-specific skills.

---

## Key concepts

Before the topics, a quick shared vocabulary. Different tools name these slightly differently, but the ideas map cleanly:

| Concept                   | What it is                                                                   | When it loads                                 | Typical file          |
| ------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------- | --------------------- |
| **Instruction**     | Always-on rules and conventions scoped to file globs                         | Automatically, based on`applyTo`            | `*.instructions.md` |
| **Skill**           | A self-contained package of domain knowledge the agent pulls in*on demand* | When the task matches the skill's description | `SKILL.md` + assets |
| **Prompt template** | A reusable, parameterized prompt for a recurring task                        | Invoked explicitly by the developer           | `*.prompt.md`       |
| **Agent / mode**    | A persona with a scoped toolset and behavior                                 | Selected by the developer                     | `*.agent.md`        |

Rule of thumb: **instructions** = "always follow these"; **skills** = "read this when the task is about X"; **prompts** = "run this recurring workflow".

---

## Topic 1 — Which common skills should exist

These are the cross-cutting skills every team benefits from. They encode *how Indice builds software*, independent of any single product. Start with the highest-leverage ones and grow the catalog as patterns stabilize.

### 1.1 .NET (company-wide backend standard)

- **`dotnet-conventions`** — target framework and language version, nullable reference types, folder/solution layout, naming, async guidelines, DI registration patterns, `IOptions` configuration, structured logging, and error-handling conventions.
- **`dotnet-web-api`** — controller vs. minimal API decision, versioning, model validation, problem-details responses, pagination, OpenAPI/Swagger setup.
- **`dotnet-testing`** — the test stack we standardize on (xUnit/NUnit + the assertion and mocking libraries we prefer), test naming, and how to write a WebApplicationFactory-based integration test.
- **`dotnet-data-access`** — EF Core conventions, migrations workflow, query performance rules, and when to use Dapper.

> **Example skill description (for the front-matter):**
> *"Use when writing or reviewing C#/.NET backend code at Indice: project structure, DI, configuration, logging, and error handling conventions. Prefer Indice.Platform primitives before adding new abstractions."*

### 1.2 Angular (company-wide UI standard)

- **`angular-conventions`** — standalone components vs. modules, folder structure, state management approach, RxJS patterns, change-detection strategy, and styling conventions.
- **`angular-forms`** — reactive forms patterns, validation, and accessibility baseline.
- **`angular-testing`** — component/service testing conventions and the tools we standardize on.

### 1.3 DevOps (delivery and operations standard)

#### Developer practices

- **`devops-versioning`** — SemVer, release notes, package metadata, and branch/release conventions that make automation predictable.
- **`devops-containerization`** — Dockerfile baseline, health probes, configuration injection, image hardening, and other choices that make services easy to build and operate.
- **`devops-go-live-readiness`** — production configuration checklist, observability hooks, migrations/rollback planning, and hand-off expectations before a release goes live.

#### DevOps practices

- **`devops-azure-platform`** — Indice Azure defaults (App Service / Container Apps, Azure SQL, Storage, Service Bus, Key Vault, App Configuration, Application Insights) and *when* to pick each.
- **`devops-delivery-pipelines`** — GitHub Actions flow, build/test/package/release stages, environment promotion, approvals, and artifact handling.
- **`devops-identity-secrets`** — Managed Identity first, Key Vault for secrets, least-privilege access, and how deployed applications integrate with our identity infrastructure.
- **`devops-observability-messaging`** — telemetry, dashboards, alerts, and the runtime conventions for Service Bus / Event Grid workloads (retries, idempotency, dead-letter handling).

### 1.4 Indice libraries — "don't re-invent the wheel"

This is the highest-value category. Each skill should tell the agent **what the library does, when to reach for it, how to install it, and a minimal usage example**, plus a link so it can read deeper. These are the concrete Indice library skills we should implement first.

#### 1.4.1 Indice.Platform

- **`indice-platform-core`** — foundational backend packages such as `Indice.Common`, `Indice.AspNetCore`, `Indice.EntityFrameworkCore`, `Indice.Hosting`, `Indice.Services`, and `Indice.Functions.Builder`. Use when building shared ASP.NET/Core infrastructure or cross-cutting primitives.
- **`indice-platform-identity`** — the identity/authentication slice (`Indice.Features.Identity.*`, activity/sign-in logging, Apple and GovGR auth providers). Use when working on sign-in, admin UI, end-user identity UI, or identity server extensions.
- **`indice-platform-messaging`** — the messaging slice (`Indice.Features.Messages.*`, workers, and Azure worker integrations). Use when a product sends campaigns, notifications, or background-delivered messages.
- **`indice-platform-agents-and-cases`** — the agents and case-management slice (`Indice.Features.Agents.*`, `Indice.Features.Cases.*`, `Indice.Features.Cases.Workflows`). Use when workflows, operational back-office cases, or AI-agent orchestration are in scope.
- **`indice-platform-risk-and-multitenancy`** — the risk, multitenancy, and related platform features (`Indice.Features.Risk.*`, `Indice.Features.Multitenancy.*`, plus adjacent feature packs such as media and government integrations when they appear in the same solution). Use when tenant isolation, fraud/risk scoring, or supporting feature modules shape the design.

#### 1.4.2 Indice.Angular

- **`indice-angular-auth`** — `@indice/ng-auth` for OIDC login/logout, guards/interceptors, session-aware Angular features, and the `@indice/ng-config` hand-off when auth settings are environment-specific.
- **`indice-angular-components`** — `@indice/ng-components` for reusable UI, Tailwind integration, shared layout/form building blocks, and auth-aware components.

#### 1.4.3 Indice.Cryptography

- **`indice-cryptography`** — the broad library skill for PSD2 compliance, certificate management, ASN.1/X.509 work, and cryptographic primitives.
- **`indice-cryptography-http-signing`** — HTTP message signing, request integrity, and certificate-backed API authentication when integrations need that protocol in detail.

> **Guardrail to embed in these skills:** *"Before proposing a new implementation, search the relevant Indice library for existing functionality. Only write new code if nothing suitable exists, and say which library you checked."*

### 1.5 Cross-cutting engineering skills

- **`code-review`** — the checklist we apply in PRs (security, performance, consistency with these skills).
- **`security-owasp`** — OWASP Top 10 baseline, secrets handling, and input validation expectations.
- **`git-conventions`** — branch naming, commit message format, and PR description template.
- **`documentation`** — how we write READMEs, ADRs, and inline docs.

### 1.6 Other languages

- **`mobile-swift`** — iOS conventions, package/dependency setup, secure storage, and how native Swift apps integrate with Indice authentication and backend APIs.
- **`mobile-kotlin`** — Android conventions, Gradle/module structure, secure storage, and how Kotlin apps consume the same identity and API surface.
- Keep these lighter than the .NET and Angular catalogs until a mobile product needs deeper project-specific skills.

---

## Bootstrapping from existing sources (don't write commodity skills from scratch)

A large amount of high-quality, ready-made skill content already exists — most of it **official and MIT-licensed**. For the *commodity* layer (generic C#/.NET, Azure, identity, cross-cutting best practices) it is far cheaper to **import and pin** than to hand-write. We should reserve our own authoring effort for what only we can provide: the **Indice libraries, our Angular conventions, and product/business knowledge**.

### Recommended sources

| Source                                                                         | What it gives us                                                                                                                                                                                                                                                                                                       | Verdict for Indice                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [dotnet/skills](https://github.com/dotnet/skills)                               | Official .NET team Agent Skills:`dotnet`, `dotnet-data` (EF Core), `dotnet-aspnetcore`, `dotnet-blazor`, `dotnet-test` / `dotnet-test-migration`, `dotnet-diag`, `dotnet-msbuild`, `dotnet-nuget`, `dotnet-upgrade`, `dotnet-ai`, `dotnet-maui`. Installs via plugin marketplace or per-skill. | **Include.** This is our baseline .NET layer — official, actively maintained, and eval-tested. Prefer it over hand-written C# guidance.                                                                                              |
| [microsoft/azure-skills](https://github.com/microsoft/azure-skills)             | Official Azure plugin: skills (`azure-prepare`, `azure-validate`, `azure-deploy`, `azure-diagnostics`, `azure-cost`, `azure-rbac`, `azure-storage`, `azure-messaging`, etc.) **plus the Azure MCP Server** (200+ live tools) and Foundry MCP.                                                    | **Include.** Covers our heavy Azure usage. The MCP layer lets the agent act on real resources, not just advise. Note the prerequisites (Node 18+, `az login`, `azd`).                                                             |
| [DuendeSoftware/duende-skills](https://github.com/DuendeSoftware/duende-skills) | Official Duende skills for IdentityServer / BFF / OAuth2 / OIDC:`identityserver-configuration`, `identityserver-stores`, `token-management`, `duende-bff`, `identityserver4-migration`, `aspnetcore-authentication`/`-authorization`, and more. Eval-benchmarked.                                        | **Include — high priority.** We ship [Indice.IdentityServer4](https://github.com/indice-co/Indice.IdentityServer4); this is the most directly relevant external set. The `identityserver4-migration` skill is especially pertinent. |
| [microsoft/skills](https://github.com/microsoft/skills)                         | 170+ Azure**SDK-specific** skills across languages (`-dotnet`, `-ts`, etc.): Service Bus, Storage Blob, Key Vault, Cosmos, Identity, plus Foundry/AI skills, custom agents, and prompt templates.                                                                                                            | **Include selectively.** Great when a service SDK is in play. Do **not** bulk-install — pick only the SDKs a repo actually uses (their own README warns about "context rot" from loading everything).                          |
| [github/awesome-copilot](https://github.com/github/awesome-copilot)             | Community`*.instructions.md` files: `csharp`, `aspnet-rest-apis`, `security-and-owasp`, `bicep-code-best-practices`, `terraform-azure`, `performance-optimization`, `code-review-generic`.                                                                                                             | **Include for gaps only.** Useful for cross-cutting instructions the official sets don't cover. Community-contributed, so vet before adopting. No dedicated Angular file exists.                                                      |

### What we still own (can't be imported)

- **Indice library skills** (`indice-platform-core`, `indice-platform-identity`, `indice-angular-auth`, `indice-angular-components`, `indice-cryptography`, …) — nobody else has these; this is the "don't re-invent the wheel" payoff.
- **Angular conventions** — external coverage is thin, and we have our own `Indice.Angular` lib, so we write this ourselves.
- **Project / business skills** — domain knowledge, by definition, can only come from us.

### How to adopt them safely

1. **Pin, don't live-link.** Vendor a copy at a specific tag/commit (or pin the plugin version). Auto-tracking upstream means agent behavior changes without review — the opposite of the consistency we want.
2. **Import selectively.** Every imported skill's *description* joins the always-on catalog each developer's agent sees. Only bring in what a repo actually uses; unused skills are pure token overhead ("context rot").
3. **Treat as a baseline, then layer.** Import commodity skills → add Indice specifics on top. Where our conventions differ from an imported skill, an Indice skill or instruction wins (make that precedence explicit).
4. **Keep attribution.** All the above are MIT (awesome-copilot too); retain the license/notice when vendoring files.
5. **Prefer the plugin install where the tooling supports it.** `dotnet/skills`, `microsoft/azure-skills`, and `microsoft/skills` all publish plugin marketplaces (`/plugin marketplace add …`), which is cleaner than copying files when the team's host supports it.

> **Bottom line:** import the .NET, Azure, and Duende sets as a pinned baseline; cherry-pick from `microsoft/skills` per SDK; fill cross-cutting gaps from `awesome-copilot`; and spend our real effort on the Indice-specific and business skills.

---

## Topic 2 — How skills are distributed and maintained

The goal: one place to author, an easy way to consume, and a clear process to keep skills trustworthy. **This repository is the single source of truth.**

### 2.1 Repository layout

A suggested structure that keeps common and project skills separate and tooling-friendly:

```
Indice.Skills/
├─ README.md
├─ common/
│  ├─ dotnet-conventions/
│  │  └─ SKILL.md
│  ├─ angular-conventions/
│  │  └─ SKILL.md
│  ├─ devops-azure-platform/
│  │  └─ SKILL.md
│  ├─ indice-platform-core/
│  │  └─ SKILL.md
│  ├─ indice-angular-auth/
│  │  └─ SKILL.md
│  └─ indice-cryptography/
│     └─ SKILL.md
├─ instructions/
│  ├─ dotnet.instructions.md         # applyTo: "**/*.cs"
│  └─ angular.instructions.md        # applyTo: "**/*.ts"
├─ prompts/
│  ├─ new-dotnet-service.prompt.md
│  └─ new-angular-feature.prompt.md
├─ templates/
│  ├─ SKILL.template.md
│  └─ project-skill.template.md
└─ CONTRIBUTING.md
```

### 2.2 Distribution options (favor packaged artifacts)

- **Marketplace / plugin artifact.** Publish the skill set to the target agent marketplace when the host supports it, so teams install a pinned version instead of copying files around.
- **NuGet package artifact.** Publish a versioned package that drops skills into the expected tool directory during setup or build-agent provisioning. Good when our .NET-heavy repos already bootstrap from NuGet.
- **Central + local override.** Consume common skills as an artifact from here, and let each repo add its own project skills locally (see Topic 3). The agent sees the union of both.
- **Vendored snapshot (exception path).** If a tool cannot consume packaged artifacts yet, vendor a pinned snapshot into the repo as a temporary fallback rather than relying on long-lived sync scripts.

> **Recommendation:** distribute the catalog as a **versioned artifact** — preferably through a marketplace/plugin install, otherwise via **NuGet**. Use vendored snapshots only when the target tool has no package-based option yet.

### 2.3 Versioning

- Version the whole set with **SemVer** and tag releases. Consuming repos pin to a tag/version so an agent's behavior doesn't change under teams unexpectedly.
- Keep a short **`CHANGELOG.md`** so teams can see what changed before they bump.

### 2.4 Maintenance & governance

- **Freshness.** Review skills on a cadence (for example quarterly) and whenever a referenced library releases a breaking change. Stale guidance is worse than no guidance because the agent will follow it confidently.
- **Feedback loop.** Give developers an easy way to flag a skill that produced a bad result (an issue template), so real usage drives improvements.

---

## Topic 3 — Templates for project-specific skills (business knowledge)

Common skills capture *how we build*. **Project skills capture *what a specific product is and the business rules it enforces*** — the domain language, the invariants, the integrations, and the decisions an agent cannot infer from code alone. These live **inside each product repo** (so they version with the code) and complement the common skills consumed from here.

### 3.1 What belongs in a project skill

- **Domain glossary** — the ubiquitous language of the product (entities, statuses, roles) so the agent uses the *right* terms.
- **Business rules & invariants** — "an invoice can't be cancelled after settlement", "a loan application requires two approvals", etc.
- **Architecture map** — the main modules/services, how they talk, and where to add new code.
- **Integrations** — external systems, which Indice/3rd-party libraries are used, and the contracts involved.
- **Do / Don't** — product-specific guardrails and known traps.

> Keep secrets, credentials, and customer data **out** of skills. Reference where they live (Key Vault, App Configuration), never the values.

### 3.2 Skill template

Save as `templates/SKILL.template.md` and copy it when creating a new skill. Front-matter drives *when* the agent loads the skill, so the `description` must be specific.

```markdown
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
- **Term** — definition and how it's used.

## Business rules & invariants
- Rule 1 (and why it exists).
- Rule 2.

## Architecture
- Modules/services and how they relate. Where to add new code.

## Integrations & libraries
- Uses [Indice.Platform](https://github.com/indice-co/Indice.Platform) for <X>.
- External systems: <system> via <contract>.

## Do / Don't
- Do: ...
- Don't: ...

## Examples
Minimal, real snippets that show the preferred pattern.
```

### 3.3 Project instructions template

For always-on rules (not on-demand), use an instructions file scoped by glob:

```markdown
---
applyTo: "**/*.cs"
---
# <Product> backend conventions
- Follow the common `dotnet-conventions` skill.
- Persist money as <type>; never use double for currency.
- All external calls go through <Indice library / internal client>.
```

### 3.4 How teams leverage project skills

1. **Scaffold** — copy the template into the repo's agent-config folder and fill it in with real domain knowledge.
2. **Layer** — the agent uses **common skills** (from this repo) *plus* the repo's **project skills**. Common = how we build; project = what this product is.
3. **Reference, don't repeat** — a project skill should *point to* common skills and Indice libraries rather than restating them, which keeps it short and cheap to load.
4. **Invoke via prompts** — pair a project skill with a prompt template (for example `new-feature.prompt.md`) so recurring work is one command that already carries the right context.
5. **Keep it close to the code** — because project skills live in the product repo, a change to a business rule and its skill land in the same PR, keeping the two in sync.

### 3.5 Worked example — leveraging a project skill

> **Task:** "Add an endpoint to cancel a subscription."
>
> Without skills, the agent guesses the domain, invents validation, and hand-rolls persistence.
>
> With skills, the agent: loads `dotnet-web-api` (common) for the endpoint shape → loads `subscriptions-domain` (project) and learns *a subscription can only be cancelled while `Active` and not within the notice period* → checks `indice-platform` for an existing cancellation primitive **before** writing new code → produces an endpoint that matches our conventions, enforces the real business rule, and reuses shared infrastructure.

That is the entire point of this repository: **the agent behaves like an Indice engineer who already knows the codebase, the standards, and the libraries — using fewer tokens to get there.**

---

## Getting started

1. Browse `common/` to see the shared skills available.
2. In your product repo, install or restore the common skills from the published marketplace/plugin artifact or NuGet package (see Topic 2.2).
3. Create your **project skills** from `templates/SKILL.template.md` and commit them alongside your code.
4. Propose improvements to common skills via PR — everyone benefits.

## Contributing

See `CONTRIBUTING.md` (to be added). In short: open a PR, keep skills accurate and concise, update the description front-matter, and route it to the right `CODEOWNERS`.
