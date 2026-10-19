---
name: dotnet-testing
description: >
  Use when writing, reviewing, or choosing tests for .NET and Angular work:
  the test stack (xUnit, FluentAssertions, Testcontainers, NetArchTest,
  Playwright, k6/NBomber), proportional verification, which risk categories
  need which tests, regulated-path evidence rules, test data, and naming.
---

# Testing rules

Verification is the contract that keeps AI output honest. Tests support a production-ready implementation of the approved scope; they never substitute for it.

Every acceptance criterion maps to proportionate verification evidence. One verification may cover several criteria, and it need not be a new automated test. Automated tests are required where they protect material changed behaviour or a regulated, security, authorization, financial, tenant-isolation, idempotency, or state-transition boundary. Infrastructure, configuration, operational, compliance, and governance controls are verified through the system that owns them. Command selection (changed-file, focused-first, no-suite fallback) follows the engineering rules instructions.

## Stack

| Type | Tool | Covers |
| --- | --- | --- |
| Unit | xUnit + FluentAssertions | Domain rules, value objects, validators, pure calculations, state transitions |
| Integration | xUnit + Testcontainers with real SQL Server | Real database, transactions, middleware, authentication and authorization wiring, serialization, module integration |
| Contract | xUnit | Actual module, event, or provider contracts |
| Architecture | NetArchTest or approved architecture tests | New or changed boundary rules; otherwise run the existing suite |
| E2E | Playwright | Required critical journeys or material cross-system risks |
| Load / concurrency | k6 / NBomber | Defined performance or concurrency requirements, known contention paths, credible introduced races |

## Core rules

* Existing tests or checks may satisfy a criterion when they directly cover the changed behaviour.
* Do not create production code merely to give a test something to exercise. Do not create tests for behaviour that is not approved, not implemented, and not being implemented in the same task. Do not create synthetic registries, configuration classes, interfaces, adapters, or abstractions merely to encode a checklist in C#.
* Test behaviour, not implementation details.
* Use the lowest effective layer that can catch the defect. Use real SQL Server only when SQL mappings, constraints, transactions, database concurrency, or persistence behaviour is part of the risk.
* Do not duplicate an assertion across layers unless each layer protects a distinct failure mode.
* Regulated calculations (fees, tax, limits, settlement amounts, allocation) should be pure. Test approved examples, meaningful boundaries, and materially distinct equivalence classes with evidence-backed expected values. Exhaustive testing only for a small finite input domain or when explicitly required.
* Tests are deterministic: control the clock, identifiers, and randomness; never rely on wall-clock time; never call live external services. Use provider fakes, local test doubles, signed test webhook fixtures, or contract fixtures for PSP, KYC, AML, SMS, email, Viber, notification, and tax-provider integrations.
* Do not chase coverage percentage. Coverage is diagnostic; it never drives production-code creation, test creation, or retention of useless tests.
* Tests may be written before, alongside, or after implementation. Sequence is not a compliance gate.
* Do not test trivial records or DTO storage, generated code, compiler or framework guarantees you do not customize, private implementation details, logging call counts, or combinatorial invalid inputs made unreachable by centralized validation.
* If test changes materially exceed implementation, consolidate duplicates and name the distinct risk each remaining test family protects. No rigid line-count ratio.
* An irrelevant risk category is marked `N/A` with a short concrete rationale instead of boilerplate tests.

## Regulated assertions need a traceable basis

AI may write test scaffolding and ordinary test bodies, but the expected value of a regulated calculation or decision must come from an approved example, an architecture decision, legal, compliance, or tax-advisor input, or an authoritative source. The same agent must not invent both the regulated behaviour and its expected result. The PR identifies the source of the assertions, and the implementation must not exceed the approved cases.

For behaviour that is not yet approved: do not write executable tests for imagined behaviour, and do not implement the logic that would make them pass. Appropriate outputs are documentation, contracts expressed as documentation, design proposals, open questions, implementation options, non-executable examples, risk assessments, and explicit stop conditions. When blocked, state it as:

```text
regulated zone — awaiting approval
```

A regression test may precede a fix only when the production path exists, the defect is real and reproducible, the required behaviour is approved, and the test exercises the real affected seam.

## Risk-triggered categories

Apply each category only when the change introduces, changes, or materially exposes that behaviour and no directly relevant shared test already covers it.

**Money, payments, ledger** (money, payment, webhook, ledger, reversal, balance, or rounding changes)
* A duplicate PSP webhook does not create duplicate orders or ledger postings. A late webhook is handled safely. A failed webhook does not create paid orders. An invalid signature is rejected.
* The ledger is append-only; a reversal posts a new fact. Totals and balances derive correctly from ledger facts.
* Money always includes currency; rounding and precision use approved expected values.

**Lifecycle state boundaries** (guarded state machines)
* Transitions are guarded; invalid transitions are rejected; a locked or closed record changes only through approved operations.
* Lifecycle state is tenant aware where relevant.
* Selection, fairness, randomness, or weighting logic is tested only against approved, evidence-backed expected behaviour.

**Eligibility and customer protection** (eligibility, caps, limits, or KYC/AML changes)
* An excluded or ineligible customer cannot purchase or initiate payment. Configured caps and limits are enforced server-side. KYC/AML gates block regulated actions.
* Gates apply to API, batch, and callback paths, not only the UI.

**Authorization and tenant isolation**
* Back-office actions require the correct role or permission; unauthorized access is blocked server-side.
* Test `401` and `403` separately only when both are reachable and the distinction is material.
* A user from one tenant cannot access or modify data of another tenant. Direct object reference attempts are rejected.

**Configuration**
* Rule changes affect only the intended tenant scope.
* Defaults are safe. Missing configuration fails safely and never silently enables regulated behaviour.

**Audit and evidence** (state, regulated decisions, permissions, configuration, financial lifecycle, consent, or evidence changes)
* State changes, regulated actions, and permission and configuration changes emit audit events containing actor, tenant, timestamp, correlation ID, and target reference where relevant.
* Consent, legal-copy, financial, KYC/AML, tax, and reporting evidence is immutable where required.

**API behaviour**
* Responses are DTOs, not entities. ProblemDetails for errors. List endpoints paginated; filtering and sorting behave as specified. Validation failures return the expected shape and status. Sensitive existence checks respect anti-enumeration.
* Do not automatically add separate unauthenticated, forbidden, cross-tenant, empty, boundary, pagination, and ProblemDetails tests for every endpoint; apply each only when relevant.

**UI behaviour**
* Cover custom component or state behaviour that can regress; do not test Angular, the component library, the browser, or generated-client behaviour you do not customize.
* Loading, error, and success apply to asynchronous screens; empty, forbidden, not-found, pending, or partial only when reachable.
* The UI does not rely on hidden or disabled controls for security; regulated decisions are confirmed by server responses.
* Playwright only where a critical journey is required or a material cross-system risk warrants it.

**Concurrency and idempotency** (defined concurrency behaviour, known contention or retry paths, credible race risks)
* Concurrent purchases near a capacity threshold do not corrupt ledger facts or exceed approved allocation limits.
* Concurrent webhooks are idempotent; retries do not duplicate state changes; event handlers are safe to reprocess; out-of-order callbacks are handled safely.

## Test data

Minimal, synthetic, sanitized. No real personal data, payment data, production secrets, or live provider credentials. Prefer builders or fixtures that make tenant scope visible. Avoid hidden defaults that make regulated tests look simpler than production.

## Naming

Readable over clever: `Method_State_ExpectedResult`, or a clear Given / When / Then body for scenario-heavy tests. Every test carries runner-visible intent metadata (for example an xUnit `DisplayName`) saying what it verifies and why it matters.

```text
PurchaseOrder_CustomerIsExcluded_ReturnsForbidden
HandleWebhook_DuplicatePaymentConfirmation_DoesNotCreateDuplicateLedgerPosting
LockRecord_TargetNotReached_ReturnsValidationError
GetPayments_UserFromDifferentTenant_ReturnsForbidden
CalculateFee_ApprovedExample_ReturnsExpectedAmount
```
