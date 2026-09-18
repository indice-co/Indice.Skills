---
name: security-owasp
description: >
  Use when a change touches authorization, tenant isolation,
  secrets, PII, payments or card data, input validation, file uploads, rate
  limiting, anti-enumeration, fail-closed defaults, audit events, back-office
  operator actions, or dependencies. The OWASP-style security baseline for
  server-authoritative, least-privilege, fail-closed systems.
---

# Security rules

Server-authoritative, least-privilege, fail-closed. Security lives in the backend; the UI is never trusted.

## Principles

Deny by default. Enforce authorization server-side. Apply least privilege. Scope data access by tenant. Minimize data collection and exposure. Audit regulated and security-relevant actions. Fail closed when configuration is missing or invalid. Never trade security, auditability, or privacy for delivery speed.

## Authorization

Route guards, hidden menus, and disabled buttons are UX only. Authorization is always server-side, using Indice IAM scopes, roles, policies, and claims through approved patterns.

IAM proves who or what the caller is and issues validated identity context: authentication, MFA, sessions, OIDC/OAuth2 clients, API resources and scopes, token issuance and signing, provider configuration, sign-in and identity activity logs. The application decides what product actions the caller may perform: product permissions, tenant access, eligibility, KYC/AML, limit gates, and regulated action authorization. Never implement IAM primitives inside an API or business module (see the `indice-iam` skill).

* Apply endpoint-level authorization; check resource ownership and tenant scope where relevant.
* Reject direct-object-reference attempts.
* Never trust client-provided tenant, role, permission, eligibility, KYC, limit, payment, fee, or tax status.
* Do not expose actions the user cannot perform unless the API explicitly returns safe capability information.
* Back-office actions require explicit permissions, never broad "admin" assumptions.

## Tenant isolation

Every resource access enforces the caller's permitted tenant scope.

* A user in one tenant cannot read or modify another tenant's data.
* Changed or materially exposed boundaries get focused automated evidence where feasible (see the `dotnet-testing` skill). UI filters never enforce scope.

## Secrets

Never in source code, test data, seed data, logs, screenshots, documentation, pull requests, or committed configuration. Use user-secrets or approved local storage in development; key vault or managed secret storage in production; managed identity where available; centralized configuration with access controls. The token-signing certificate stays in its environment and is never copied into a repository or shared through chat, email, or tickets.

## PII and sensitive data

Apply data minimisation: store only what the approved business, legal, compliance, operational, or evidence purpose needs. Never log secrets, tokens, credentials, raw payment or card data, unnecessary PII, sensitive regulatory evidence, or full provider payloads unless explicitly approved and redacted. Mask or redact where needed. Retention is configuration-driven. Consent, KYC, financial, tax, and compliance evidence is immutable where required.

## Payments and PCI posture

Stay out of raw card-data handling: never touch, store, log, transmit, inspect, or proxy it. Allowed patterns: PSP-hosted payment flows, tokenized payment references, signed PSP webhooks, approved reconciliation files or APIs, approved refund, reversal, or settlement APIs. Required: webhook signature verification, replay protection where supported, idempotency, safe logging, no raw provider payload logging unless approved and redacted, and no payment state change without an audit event.

## Input and web safety

Validate all input server-side. Angular's built-in XSS protection is not a substitute for server-side authorization, validation, encoding, and output control.

* Validate request DTOs; encode output where appropriate.
* Allow-lists for filters, sorts, states, and enum-like inputs. Never concatenate SQL, build dynamic SQL from user input, or bind arbitrary client field names into EF queries.
* Treat external callbacks as hostile until verified: validate signatures before processing, apply replay protection where supported.
* Anti-forgery protection for browser-posted forms; secure headers and Content-Security-Policy.
* Never expose stack traces or internal exception details.

## File uploads

Validate type, size, extension, and content type. Never trust client filenames; store under generated safe names outside executable paths. Scan where required by policy. Enforce authorization on download and tenant scope on access. Audit sensitive uploads and downloads. Never expose direct storage URLs unless approved, scoped, and time-limited.

## Rate limiting and anti-enumeration

Per-endpoint rate limits on sensitive paths: login, register, forgot password, OTP and MFA, invite acceptance, user lookup, payment initiation, PSP and KYC/AML callbacks where applicable, and back-office search where existence may be inferred.

Do not reveal whether an account exists in sensitive flows; use generic responses for forgot-password and similar; rate-limit lookup-style endpoints; redact sensitive error details; avoid response timing differences where practical.

## Secure defaults

Fail closed. Missing, invalid, expired, or ambiguous configuration never silently enables regulated behaviour. Missing eligibility, limit, KYC provider, or tax rule configuration blocks the regulated action; missing payment method configuration blocks payment initiation; missing legal copy version blocks consent capture; missing governance approval blocks the gated behaviour. No permissive fallbacks for regulated actions unless explicitly approved.

## Audit versus logging

Logging is operational diagnostics and support. Audit is legal, security, compliance, and regulated evidence.

Audit events are required for authorization and permission changes, role assignments, configuration changes, legal copy or consent changes, regulated actions, payment state changes, ledger postings, lifecycle state changes, KYC/AML decisions, limit interventions, evidence capture, and report exports. Each includes, where relevant: actor and actor type, tenant, target resource, action, previous and new state, timestamp, correlation ID, reason or command reference, and evidence reference. Audit records are not a PII dump: store evidence references rather than full sensitive payloads.

## Back-office security

Operators can affect regulated and financial workflows, so: explicit permissions, not admin-only checks; server-confirmed allowed actions where useful; audit every state-changing operator action; record operator reason where required; protect exports and bulk actions; confirm destructive or irreversible actions; no client-side-only restrictions; no sensitive evidence without the right permission and scope.

## Supply chain

Central package management with pinned versions; dependency and secret scanning in CI; no unapproved packages; a recorded justification for new dependencies; transitive-dependency review for security-sensitive packages. Never disable analyzers or warnings to make a build pass.

## Checklist

* Server-side authorization and least privilege; ownership and tenant checks; direct-object-reference rejected; UI controls treated as UX only.
* IAM handles authentication, MFA, and sessions; the application handles product permissions and regulated gates.
* No secrets anywhere in the repository, logs, docs, tests, screenshots, or PRs; no unnecessary PII or evidence logged.
* Raw card data never handled; webhook signatures verified; replay protection where supported.
* Inputs validated, outputs encoded, no dynamic SQL from user input.
* Rate limiting and anti-enumeration on sensitive endpoints; missing configuration fails closed.
* Audit trail for security-relevant and regulated actions; uploads and downloads validated, scoped, authorized, and audited.
* Dependency and secret scanning in CI.
