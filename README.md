# Indice.Skills

> Indice's agent skills: the conventions, libraries, and guardrails an AI coding agent (GitHub Copilot, Claude Code, Codex, Cursor, and others) needs to write code the way Indice does.

## 1. What this repository is

Public skill catalogs such as [dotnet/skills](https://github.com/dotnet/skills) and [angular/skills](https://github.com/angular/skills) teach an agent how to write good .NET or Angular in general. They do not know how **Indice** builds software: which `Indice.*` packages already solve a problem, how our web APIs are shaped, how we host IAM or integrate with Messaging and Cases, or which security baseline we apply.

The skills in this repository fill that gap. Each one is an **Indice override** of a common skill area: it builds on the public baseline (see [section 4](#4-recommended-public-skills-for-net-and-angular)) and states where Indice does things differently. For example, `dotnet-web-api` tells the agent how *we* write endpoints (Api/Handlers/Service split, `TypedResults`, `ResultSet` paging, Indice.Platform primitives) instead of the generic ASP.NET Core defaults.

### Why

- **Consistency.** Two developers asking the same question get the same architecture.
- **Reuse before writing.** The agent checks [Indice.Platform](https://github.com/indice-co/Indice.Platform) and the other [Indice libraries](https://github.com/indice-co) before proposing new code.
- **Fewer tokens.** A skill loads only when the task matches it, instead of the same context being pasted into every chat.
- **Faster onboarding.** New developers, and their agents, inherit our conventions from day one.

### How

Skills follow the open [Agent Skills specification](https://agentskills.io): a folder containing a `SKILL.md` whose front-matter `name` and `description` tell the agent *when* to load it. The agent sees only the descriptions up front and reads the full skill when a task matches.

| Type | What it is | When it loads | File |
| --- | --- | --- | --- |
| **Skill** | Domain knowledge the agent pulls in on demand | When the task matches the skill's `description` | `<name>/SKILL.md` (plus optional reference files) |
| **Instruction** | Always-on rules scoped by file glob | Automatically, based on `applyTo` | `*.instructions.md` |
| **Prompt** | A reusable prompt for a recurring task | When the developer invokes it | `*.prompt.md` |

### Repository layout

| Folder | Contents |
| --- | --- |
| `common/` | The Indice skills (one folder per skill) and the always-on engineering rules (`engineering-rules*.instructions.md`) |
| `instructions/` | Always-on language instructions for .NET and Angular |
| `prompts/` | Reusable `*.prompt.md` files |
| `templates/` | Templates for project-specific skills (see [section 3](#3-project-specific-skills)) |
| `evals/` | Tasks and rubrics that measure whether a skill changes agent output |

### Skill catalog

**Indice platform**

| Skill | Use when |
| --- | --- |
| `indice-packages` | Before writing infrastructure or platform plumbing in .NET: which `Indice.*` package covers the need and how to set it up |
| `indice-platform` | Before writing a new backend building block: what Indice.Platform provides, how to install it, minimal usage |
| `indice-templates` | Scaffolding a new web project with `Indice.DotNet.Templates.Web`: Identity, Messaging, Cases, Minimal API, REST API, Azure Functions workers |
| `indice-iam` | Identity, authentication, authorization, or any project that hosts Indice IAM |
| `indice-messaging` | Integrating with an existing Indice Messaging deployment: sending messages (Send API) or showing a user's inbox and preferences (My API) |
| `indice-cases` | Integrating with an existing Indice Cases deployment: customers creating and tracking cases (My API) or back-office users working them (Manage API) |

**.NET and Azure**

| Skill | Use when |
| --- | --- |
| `dotnet-conventions` | Writing or reviewing C# code: project structure, DI, configuration, logging, error handling |
| `indice-web-api` | Writing or reviewing HTTP endpoints in an Indice.Platform feature library or a product API |
| `dotnet-testing` | Writing or choosing tests: xUnit, Testcontainers, `WebApplicationFactory`, architecture, E2E, and load tests |
| `azure-services` | Choosing or configuring Azure services for an Indice product, and when to pick each |

**Angular**

| Skill | Use when |
| --- | --- |
| `angular-conventions` | Writing or reviewing Angular code: components, folder structure, state, RxJS, change detection, styling |
| `angular-architecture` | Creating or restructuring an Angular app and its ASP.NET Core host: routing, runtime config, OIDC, API clients |
| `angular-ux` | Designing or implementing Angular screens with PrimeNG |

**Cross-cutting**

| Skill | Use when |
| --- | --- |
| `security-owasp` | Changes touching authorization, tenant isolation, secrets, PII, payments, input validation, or uploads |
| `performance` | Hot paths, list and export endpoints, EF queries, concurrency, caching, Angular bundle and rendering |
| `regulated-integrations` | Integrating with banks/PSD2, payment gateways, government KYC or tax services, CRM, ERP, and similar systems |

The always-on engineering rules set the baseline every skill assumes: `engineering-rules.instructions.md` (all files), `engineering-rules.backend.instructions.md` (`**/*.cs`), and `engineering-rules.frontend.instructions.md` (`**/*.{ts,html,scss}`). For the authoritative list of skills, run `npx skills add indice-co/Indice.Skills --list`.

---

## 2. Install and use the skills

Skills are installed with the [`skills` CLI](https://github.com/vercel-labs/skills) (`npx skills`, requires Node.js 22+). It detects the coding agents you have installed and places the skills in each agent's skills folder. It uses your existing Git credentials (SSH, credential helper, or GitHub CLI) to read this repository.

```bash
# List the available skills
npx skills add indice-co/Indice.Skills --list

# Install into the current project (default)
npx skills add indice-co/Indice.Skills

# Install globally, for every project on your machine
npx skills add indice-co/Indice.Skills -g

# Install only some skills, for specific agents
npx skills add indice-co/Indice.Skills --skill indice-packages --skill dotnet-web-api -a github-copilot -a claude-code

# Non-interactive (CI, dev containers)
npx skills add indice-co/Indice.Skills --skill '*' -a github-copilot -y
```

| Scope | Flag | Installed to | Use when |
| --- | --- | --- | --- |
| **Project** | *(default)* | `.agents/skills/`, `.claude/skills/`, … in the repo | The product repo should carry a pinned set the whole team shares. **Recommended for product repos.** |
| **Global** | `-g` | `~/.copilot/skills/`, `~/.claude/skills/`, … | Personal setup across all repos |

Manage installed skills:

```bash
npx skills list               # installed skills (add -g for global)
npx skills update             # update unpinned skills to the latest version
npx skills remove <skill>     # uninstall
```

> `npx skills` installs only `SKILL.md` skills. To use the engineering rules in `common/` and the files in `instructions/` and `prompts/`, copy them into the product repo (for GitHub Copilot: `.github/instructions/` and `.github/prompts/`).

### Versioning

Releases are tagged with SemVer (`vMAJOR.MINOR.PATCH`) and recorded in [CHANGELOG.md](CHANGELOG.md):

- **MAJOR**: a skill is removed or renamed, or its guidance changes the shape of generated code.
- **MINOR**: a new skill or new guidance.
- **PATCH**: fixes and clarifications.

Pin product repos to a release by appending `#<tag>` to the source:

```bash
npx skills add indice-co/Indice.Skills#v1.2.0
npx skills add indice-co/Indice.Skills#v1.2.0 --skill dotnet-web-api
```

Project installs record the source, ref, and a content hash of each skill in `skills-lock.json`. Commit it together with the installed skill folders so the team and CI use the same version. To upgrade, read the changelog and re-run `npx skills add` with the new tag. Unpinned installs track `main`.

---

## 3. Project-specific skills

Indice skills describe **how we build**. A project skill describes **what a specific product is**: its domain language, business rules, architecture, and integrations, which an agent cannot infer from code alone. Project skills live in the product repo, next to the code, so a change to a business rule and its skill land in the same PR.

### Why

- The agent uses the product's own terms and enforces the real business rules instead of inventing them.
- It points to the Indice skills instead of repeating them, so it stays short and cheap to load.

### How

1. Create a folder for the skill in the product repo: `.agents/skills/<product>-<area>/` (read by GitHub Copilot, Codex, Cursor, Gemini CLI, and OpenCode; Claude Code reads `.claude/skills/`).
2. Copy [templates/SKILL.template.md](templates/SKILL.template.md) into it as `SKILL.md` and fill it in:

   | Section | Contents |
   | --- | --- |
   | Front-matter | `name` equal to the folder name, prefixed with the product to avoid clashes with installed Indice skills. A specific `description`, because it decides when the skill loads. |
   | Builds on | The Indice skills this one relies on, so it does not restate them |
   | Domain glossary | Entities, statuses, and roles in the product's own words |
   | Business rules & invariants | For example, "an invoice cannot be cancelled after settlement", and why |
   | Architecture | Main modules or services, how they talk, where new code goes |
   | Integrations & libraries | External systems and the Indice or third-party libraries used |
   | Do / Do not | Product-specific guardrails and known traps |
   | Examples | Short, real snippets of the preferred pattern |

3. Optionally add an always-on instructions file and a recurring-task prompt, using [templates/project-skill.template.md](templates/project-skill.template.md).

> Keep secrets, credentials, and customer data **out** of skills. Reference where they live (Key Vault, App Configuration), never the values.

### Example

> **Task:** "Add an endpoint to cancel a subscription."
>
> Without skills, the agent guesses the domain, invents validation, and hand-rolls persistence.
>
> With skills, the agent loads `dotnet-web-api` (Indice) for the endpoint shape, loads `billing-subscriptions` (project) and learns that *a subscription can only be cancelled while `Active` and outside the notice period*, checks `indice-packages` for an existing primitive before writing new code, and produces an endpoint that follows our conventions and enforces the real business rule.

---

## 4. Recommended public skills for .NET and Angular

The Indice skills are overrides: they assume a public baseline is installed alongside them. Install the baseline, then the Indice skills. Where the two disagree, the Indice skill wins.

Install selectively. Every installed skill's description sits in the agent's context, so unused skills cost tokens and can trigger on the wrong task. Run `--list` first and install only what the repo uses, then check the list for name clashes: skills with the same `name` overwrite each other.

### .NET

| Source | What it covers | Install |
| --- | --- | --- |
| [dotnet/skills](https://github.com/dotnet/skills) | Official .NET team skills: C#, ASP.NET Core, EF Core, testing, MSBuild, NuGet, diagnostics, upgrades | `npx skills add dotnet/skills --list` |
| [DuendeSoftware/duende-skills](https://github.com/DuendeSoftware/duende-skills) | IdentityServer, BFF, OAuth 2.0 / OpenID Connect, ASP.NET Core authentication and authorization. Relevant wherever Indice IAM is hosted | `npx skills add DuendeSoftware/duende-skills --list` |
| [microsoft/azure-skills](https://github.com/microsoft/azure-skills) | Preparing, deploying, diagnosing, and costing Azure workloads, plus the Azure MCP Server | See the repository |
| [microsoft/skills](https://github.com/microsoft/skills) | Azure SDK skills per service and language (Service Bus, Storage, Key Vault, Identity, …). Pick only the SDKs the repo uses | `npx skills add microsoft/skills --list` |
| [Microsoft Learn MCP Server](https://learn.microsoft.com/training/support/mcp) | Up-to-date .NET and Azure documentation for the agent | See the documentation |

### Angular

| Source | What it covers | Install |
| --- | --- | --- |
| [angular/skills](https://github.com/angular/skills) | Official Angular team skills: `angular-developer` (components, signals, forms, DI, routing, SSR, accessibility, testing) and `angular-new-app` | `npx skills add angular/skills` |
| [Angular CLI MCP Server](https://angular.dev/ai/mcp) | Lets the agent search Angular docs and best practices and run CLI tasks in the workspace | See the documentation |
| [PrimeNG plugin and MCP Server](https://primeng.dev/mcp) | PrimeNG component docs, API metadata, and usage validation. Used together with `angular-ux` | `pnpm dlx @primeui/cli plugin install --tool copilot --library primeng` |

### Starter sets

| Repo type | Public baseline | Indice skills and rules |
| --- | --- | --- |
| New service | | `indice-templates`, then the .NET row |
| .NET API or feature library | `dotnet/skills` (selected), `duende-skills` if it hosts IAM | `indice-packages`, `dotnet-conventions`, `dotnet-web-api`, `dotnet-testing`, `security-owasp`, plus the general and backend engineering rules |
| App that uses Indice Messaging or Cases | | `indice-messaging`, `indice-cases` |
| Angular app | `angular/skills`, PrimeNG plugin | `angular-conventions`, `angular-architecture`, `angular-ux`, plus the general and frontend engineering rules |
