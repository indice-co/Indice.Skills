---
applyTo: "**"
---
# AI engineering rules

Binding rules for AI-assisted and human code in this repository. They apply to every task unless a more specific instruction or skill overrides them.

## Core principle

Correctness, auditability, security, traceability, and customer protection outrank speed. Do not optimize for fast implementation if the result weakens control, evidence, privacy, authorization, financial integrity, or operational safety.

The approved requirement (work item, acceptance criteria, approved design) defines WHAT. Evidence from source, existing code, and architecture defines HOW. Record the selected option, rationale, and material risks where the team keeps decisions.

## Simplicity and proportionality

* Implement the smallest coherent production-quality change that satisfies the approved scope, applicable architecture and security rules, and the material reachable risks the change introduces.
* Prefer the simplest design that fits the current requirement and existing architecture. Reuse existing local patterns before introducing new structure.
* Do not add behavior, fields, statuses, options, abstractions, extension points, failure handling, tests, fixtures, configuration, background work, retries, concurrency, packages, or unrelated refactoring for imagined future work.
* Every new file, type, abstraction, branch, option, retry, test, fixture, or dependency must trace to an acceptance criterion, approved architecture rule, confirmed defect, material reachable production risk, or required repository convention. If it cannot, do not add it.
* A single implementation does not automatically require an interface. Interfaces belong at real architecture, module, or provider boundaries, approved test seams, or established patterns.
* Treat an edge case as material only when it is defined by the requirement, reachable, protects a security, financial, privacy, authorization, audit, or tenant boundary, is a confirmed regression, or has material user, operational, legal, or financial impact.
* Prefer explicit, readable, boring implementation over clever or generic design. Keep changes easy to review, test, and revert.
* Stop when approved behavior and its material risks are covered.
* If a requirement, production value, security decision, legal/regulatory decision, configuration key, threshold, or formula is missing, do not guess. Follow the clarification rules below.

## Prompt and loop discipline

* Verify live state before acting. Do not trust memory, summaries, prior reports, or stale branch assumptions.
* Keep scope fenced. Fix only the requested task and flag adjacent issues instead of expanding the work.
* Treat an authorized action request as work to finish through verification and handoff. Do not stop at a plan when execution is already authorized. Read-only requests stay read-only.
* Distinguish missing requirements from routine implementation choices. Choose routine details from approved scope, source evidence, and existing patterns, and briefly state material assumptions. Do not ask the user to choose details that cannot change behavior, authority, scope, acceptance, or material risk.
* When a missing answer can change those boundaries, pause the dependent action and ask. Complete independent authorized preparation first.
* If a task links a source (URL, file, document), read the complete source before relying on it. Snippets, metadata, and prior summaries are not evidence. If a source cannot be read, report the exact blocker instead of claiming completion.
* Before claiming success, run the smallest direct check that can expose a material failure of the requested result. Never present unexecuted checks as passed.
* Explain the outcome in short, plain sentences, then the reason, verification, and material limitations.

## Never

* Invent requirements, fields, statuses, rules, flows, permissions, copy, or behaviours not present in the approved requirement.
* Bypass, reinterpret, or partially implement acceptance criteria.
* Hardcode country- or market-specific rules, including country, currency, age, tax, legal copy, payment methods, communication channels, or reporting periods. Serve them from configuration.
* Read or write tenant-scoped data without tenant awareness where applicable.
* Skip server-side authorization. Route guards and UI checks are never the security boundary.
* Skip audit events on state changes, regulated actions, permission changes, configuration changes, financial events, or evidence-producing actions.
* Return EF entities from APIs. Always project to DTOs.
* Create unbounded list endpoints. Pagination is mandatory.
* Write payment, ledger, KYC/AML, tax, or compliance logic without approved behaviour, idempotency, auditability, and verification through the owning system.
* Access the tables, entities, repositories, or internals of another module. Use contract interfaces or approved integration events.
* Modify unrelated modules within a task.
* Introduce a package without a recorded reason. `Indice.*` packages are pre-approved when the task requires them; other packages need explicit approval. Package versions live in `Directory.Packages.props`.
* Store secrets in code, configuration files, seed data, tests, logs, screenshots, or documentation.
* Hardcode connection strings, database names, infrastructure endpoints, credentials, or fallback LocalDB/provider settings anywhere, including design-time factories, tests, and scripts. Use configuration providers, user secrets, environment variables, or approved secret stores, and fail closed when required configuration is missing.
* Log secrets, tokens, credentials, raw payment data, unnecessary PII, or sensitive regulatory evidence.
* Create destructive database migrations without explicit human approval.
* Weaken nullable, analyzers, warnings-as-errors, authorization, audit, validation, or idempotency requirements to make delivery easier.
* Substitute documentation-only, scaffold-only, stub-only, or test-only output for required production behavior unless an explicit, item-specific deferral is recorded. Scaffolding is a temporary blocked-state artifact and must not be marked done.

## Indice platform products

Indice platform products (IAM, Messaging, Cases, and other `Indice.*` packages) are the source of truth for the capabilities they own.

* Do not reimplement what Indice IAM owns: login, registration, external providers, email/phone verification, TOTP/MFA, device trust, token revocation, consent, client/resource/scope administration, or the admin UI. Configure and compose it; fail closed when required policy, store, key, or client inputs are missing.
* Allow an Indice product to generate and own the APIs, EF models, DbContexts, migrations, schema, stores, UI assets, workers, and cleanup jobs it needs, inside its own host or schema.
* Do not create parallel implementations or duplicate source-of-truth stores in application modules for capabilities an Indice product owns.
* Keep the usual rules: no checked-in secrets, no hardcoded connection strings, central package versions, and a recorded reason for each adoption: "Indice used because ..." or "Custom used because ...".
* Use custom code only when Indice does not provide the behaviour, the behaviour is domain-specific, or a package would weaken auditability, authorization, idempotency, privacy, or traceability.

## Gated sensitive zones

Payments, ledger, KYC/AML, tax, compliance reporting, and legal copy or consent evidence require explicitly approved behaviour before implementation. If behaviour is missing or ambiguous, do not guess. Deliver at most the minimum safe scaffolding for the blocked state (DTOs, documented contracts, design proposals, open questions, feature-flagged stubs that cannot execute the sensitive behaviour) and record the blocker.

## Required for every implementation

* Work item ID in branch name, commit message, and PR. Never in runtime code, exception text, log messages, or test display names.
* Implementation only from the approved requirement.
* Production-ready implementation for the approved scope once blocking questions are resolved.
* `README.md`, code comments, and XML documentation kept aligned with every change. Remove stale comments; avoid comments that restate the code.
* Affected modules and changed files listed with the reason for each change.
* A verification method for every acceptance criterion.
* Automated tests where they exercise real implementation and provide meaningful regression protection, each with runner-visible intent metadata (for example an xUnit `DisplayName`) that says what is verified and why it matters.
* Non-test verification evidence for infrastructure, configuration, operational, and compliance controls, collected from the system that owns the control.
* Server-side authorization; tenant scoping where relevant.
* Audit events for all state changes and regulated actions.
* Structured logging with correlation ID.
* ProblemDetails for API errors.
* OpenAPI/Swagger summary and description for every exposed endpoint: what it does, who uses it, scope/auth/idempotency requirements, and when it is used.
* Cancellation tokens throughout async flows.
* DB migration for schema changes, with review notes covering SQL, indexes, constraints, rollback, and data impact.
* Build passing under nullable, analyzers, and warnings-as-errors.
* Explicit assumptions and uncertainties.

## Testing rules

* Verification must prove real behavior. Every acceptance criterion maps to proportionate evidence, not to a unique test. One check may cover several criteria; existing evidence may be reused when it directly covers the change. Evidence may be an automated test, build/static check, contract validation, artifact inspection, or a documented manual check when automation is unsuitable.
* Choose commands from the actual diff. Run a directly mapped focused test when one exists, otherwise a relevant affected-package test. Never fall back to a repository-wide suite merely because no focused test was found; record `no relevant automated test found` and use the smallest applicable non-test check. A full suite requires an explicit approved reason.
* Use the lowest effective layer. Add focused automated protection for non-trivial changed production behavior and for regulated, financial, authorization, security, tenant-isolation, idempotency, and state-transition boundaries. Add integration, contract, E2E, load, or architecture tests only when that layer protects a distinct material failure mode. Do not duplicate the same assertion across layers.
* For an ordinary feature, verify the changed happy path and only the material validation, authorization, or failure paths the change touches. For a bug fix, add one focused regression test at the lowest effective layer.
* Do not add tests for trivial data storage, generated code, compiler/framework guarantees, private implementation details, logging call counts, every enum permutation, or to preserve a coverage percentage. Do not lower CI thresholds or game them with low-value tests.
* Tests may be written before, alongside, or after implementation. The change is incomplete until proportionate verification passes.
* If test changes materially exceed the implementation, consolidate duplicates and name the distinct risk each remaining test family protects.

## API rules

* Return DTOs only; never EF entities.
* Paginate list endpoints; make filtering and sorting explicit.
* Server-side authorization is mandatory; enforce tenant boundaries server-side.
* Use ProblemDetails for errors.
* Contracts match the approved requirement. Do not add convenience fields, expose internal IDs, or leak whether sensitive records exist unless the requirement allows it.

## Data and database rules

* Each module owns its own schema and persistence. Do not join across or write to the tables of another module. Use contracts, application services, or approved integration events.
* Use a `Money` value object; store amounts with currency. Use typed IDs.
* Prefer append-only evidence for regulated and financial records. Do not overwrite regulatory evidence unless correction behaviour is explicitly required.
* Add indexes intentionally and document why. Review migrations for destructive operations, lock risk, rollback, and data impact.

## Logging, audit, and evidence

* Structured logging with correlation ID. Redact sensitive fields; never log secrets or unnecessary PII.
* Audit events for state changes, regulated decisions, configuration changes, permission changes, and evidence-producing actions.
* Audit records explain who did what, when, on which tenant, and why where applicable.

## Security rules

* Server-side authorization is mandatory; UI controls are not security controls.
* Do not trust client-provided tenant, role, permission, price, eligibility, or limit values. Validate all inputs server-side.
* Use least privilege. Do not expose internal module state.
* Use approved secret storage for local and deployed environments.
* No authentication or authorization shortcuts for development unless explicitly isolated from production and approved.

## Front-end rules

* Use the Angular patterns and shared component library already established in the repository.
* Do not duplicate regulated decision logic in the UI. Use server-provided configuration for legal copy, limits, currencies, countries, payment methods, and product availability.
* Handle loading, empty, error, forbidden, and success states. Disabled controls are UX only, not authorization.
* Keep accessibility and responsive behaviour consistent with the design system.

## Conventions

* Module-first modular monolith with clean architecture inside each module; thin shared layer.
* `Money` for money, typed IDs, `Result<T>` for outcomes, file-scoped namespaces, ProblemDetails, cancellation tokens throughout.
* Ledger-first for financial records: store facts, derive totals.
* Configuration over code for country- or market-specific behaviour; feature flags for controlled rollout where required.
* Central package versions in `Directory.Packages.props`.
* Reference projects teach architecture, composition, folder structure, and extension seams only. Never copy clients, scopes, roles, claims, legal copy, secrets, connection strings, certificates, keys, branding, or business journeys from them.
* Keep generated clients and provider-owned models behind owned adapters and mappers. Do not expose them in public or module contracts, audit contracts, or durable domain records unless explicitly approved.
* External regulated integrations (payments, banking, KYC/AML, tax, eGov) need an approved design covering idempotency, ledger interaction, immutable audit, authorization, scoping, callback/retry behavior, error mapping, data minimization, retention, redaction, and secret/key management before implementation.
* Treat cryptography, certificates, signing, mTLS, and key management as security-sensitive. Never copy sample key material, passphrases, or certificate defaults.
* Test fixtures must be synthetic, minimal, and sanitized. Never use realistic personal, identity-document, payment, or account data.

## Default response when blocked

When blocked by ambiguity, missing approval, or missing design detail, respond with:

* The blocking issue and the affected requirement or acceptance criterion.
* Why guessing is risky.
* The exact question needed, with expected answer format.
* The safest proposed interpretation.
* Whether temporary blocked-state scaffolding is approved; otherwise state that implementation is blocked.
