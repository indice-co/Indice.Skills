---
name: performance
description: >
  Use when working on hot paths, list and export endpoints, EF queries and
  indexes, money and ledger concurrency, demand spikes near a threshold,
  external calls and background work, caching, Angular bundle and rendering
  performance, or performance observability. Correctness first, then speed.
---

# Performance rules

Correctness first, then speed. These are delivery defaults, not optimizations to add later. Performance must never weaken regulated correctness, auditability, authorization, idempotency, or financial evidence.

## Expectations

* Performance budgets are defined per endpoint, journey, or workload in the approved requirement or performance profile. Do not invent targets inside implementation work.
* Treat meaningful regressions as bugs.
* Validate defined budgets with realistic data volume, filters, and tenant scoping.
* Angular bundle-size budgets are enforced through `angular.json`.

## Queries

* Project to DTOs. Do not load EF entities for list or read screens unless domain behaviour is required, and never return them from APIs.
* No unbounded `Include()`, no entity loads for screens, no N+1 patterns.
* Pagination is mandatory; filtering and sorting are server-side with allow-listed fields.
* Every filter and sort path on a hot list has an intentional indexing strategy. Review query plans for hot paths, and verify important query paths with EF query logging or integration tests where relevant.

Typical hot paths: primary resource lookups, progress or balance projections, purchase and payment status, ledger projections, back-office list screens, compliance exports, and operational queues.

## Lists and exports

Back-office screens use server-side grids: server-side pagination, filtering, and sorting; a maximum page-size cap; a stable default sort; indexed filter and sort fields; DTO projection; no load-all-then-filter.

No unbounded exports from interactive endpoints, and a list endpoint never doubles as an export endpoint. Large exports use an approved flow: background job, export request record, status polling, secure download link, audit event, expiry policy.

## Money, ledger, and concurrency

Money, order, and ledger paths must be correct under retries and concurrency:

* Transactions around related money, order, and ledger writes.
* Idempotency keys for money, state-changing, callback, and retryable operations.
* Optimistic concurrency tokens on important aggregates and read-model updates.
* Append-only ledger facts as the source of financial truth; balances, progress, fees, and settlement views are derived.
* Reprocessable event handlers; safe handling of duplicate, late, and out-of-order callbacks.

Never treat a mutable counter as financial truth. Any projection or read model is derived from ledger facts and must be rebuildable.

## Demand spikes near a threshold

When demand can exceed supply, traffic spikes hardest as a resource nears its capacity or sales threshold. Design that path for contention from day one:

* Idempotent order and payment-confirmation handling; ledger-first recording.
* Contention-safe projection updates, no lost updates, no allocation beyond approved limits.
* A race-free threshold trigger (lock or close) that fires exactly once, with duplicate attempts safe.
* Intake after the threshold follows approved lock and over-allocation rules.
* Read-heavy "is it reached yet?" checks use a read model or projection, not the write path.
* Load and concurrency tests cover the path when the requirement defines it, the change touches the known contention path, or a credible race is introduced.

## External calls and background work

Request paths do not wait on slow external work (PSP, KYC/AML, sanctions or PEP screening, notifications, email, SMS, Viber, tax or reporting integrations) unless synchronous confirmation is explicitly required. Use outbox, background jobs, provider callback processing, status polling, retry policies, and dead-letter or manual-review queues.

* Async all the way; no sync-over-async; pass `CancellationToken`.
* External calls are timeout-bounded; retries are idempotent.
* Provider failures never leave financial or regulated state ambiguous.
* Slow provider work never blocks unrelated user journeys.

## Caching

Cache only after correctness and invalidation are understood.

* Safe: static reference data, public configuration, non-sensitive lookups, versioned content with expiry, read models designed for eventual consistency.
* High risk: eligibility decisions, KYC/AML clearance, exclusion or limit status, payment status, ledger balances, progress near a threshold, lock status, tax outcomes, consent status. Never cache regulated state in a way that can serve a stale gate, limit, eligibility, payment, or selection decision.
* Where used: define TTL, invalidation, freshness, and tenant scope; avoid cache keys that leak PII.

## Angular

Lazy-loaded feature routes and route-level code splitting; bundle budgets in `angular.json`; stable identity or `trackBy` for repeated lists; virtual scroll for large tables where appropriate; server-side grids; debounced search and minimum search length where specified; no repeated API calls from uncontrolled signal or effect loops; no large reference data sets loaded unless needed; no regulated totals calculated from client-side list data. Back-office tables prioritise server-side performance over client-side convenience.

## Database

For hot paths: review indexes and query plans; avoid table scans on common filters; avoid cross-module joins and querying another module's schema; keep transactions short and never wrap external calls in them; use concurrency tokens where transitions can race; add indexes intentionally in migrations; consider read models for high-volume operational screens.

For compliance reporting: prefer reproducible report queries or export jobs; do not block operational tables with heavy synchronous reporting; use approved reporting projections; preserve evidence correctness over report speed.

## Observability

Capture safe metadata for query latency, endpoint latency, external provider latency, queue processing delay, retry count, idempotency duplicate detection, webhook processing outcome, threshold-trigger attempts, projection lag, and export job duration. Use correlation IDs across request, background job, provider callback, audit event, and ledger posting. Never log secrets, raw payment data, unnecessary PII, or sensitive regulatory evidence.

## Checklist

* Lists paginated, capped, projected to DTOs, server-filtered and sorted; hot filters and sorts indexed; no unbounded `Include()`, N+1, or load-all-then-filter.
* Large exports use the approved export flow.
* Money, order, lock, ledger, and callback paths idempotent; financial truth from append-only ledger facts; progress derived, not mutable; transactions protect related writes.
* Concurrency handled for threshold and payment spikes; the threshold trigger is race-free and fires once.
* Slow external calls off the request path; retries idempotent.
* Caching has defined TTL, invalidation, scope, and freshness; no stale cache can approve or block a regulated action.
* Angular routes lazy-loaded and bundle budgets respected.
* Performance-sensitive paths have safe observability.
