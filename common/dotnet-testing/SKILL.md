---
name: dotnet-testing
description: >
  Use when writing, reviewing, or choosing tests for C#/.NET code: default test
  stack (xUnit, Testcontainers, WebApplicationFactory), which layer to test at,
  determinism, fixtures, mocking, architecture tests (NetArchTest), E2E tests
  (Playwright), load and concurrency tests (k6/NBomber), risk-triggered test
  categories, test data, and naming.
---

# .NET testing rules

Tests support a production-ready implementation of the approved scope; they never substitute for it. Every acceptance criterion maps to proportionate verification evidence. One check may cover several criteria, and it need not be a new automated test.

## Scope

Follow the test layers, frameworks, and project layout the repository already uses. Do not introduce a new test type, framework, or test project (architecture, contract, E2E, load) unless the user asks for it or an acceptance criterion requires it. If a needed layer is missing, report the gap instead of creating it.

## Stack

Defaults for new test projects; existing repositories keep their stack.

| Type | Default tool | Use when |
| --- | --- | --- |
| Unit | xUnit | Domain rules, value objects, validators, pure calculations, state transitions |
| Integration | xUnit + `WebApplicationFactory<TProgram>` + Testcontainers | Real database, transactions, middleware, authentication and authorization wiring, serialization |
| Contract | xUnit | Module, event, or external provider contracts |
| Architecture | NetArchTest | New or changed boundary rules; otherwise run the existing suite |
| E2E | Playwright | Required critical journeys or material cross-system risks |
| Load / concurrency | k6 or NBomber | Defined performance or concurrency requirements, known contention paths, credible introduced races |

Licensing: FluentAssertions v8+ and NBomber require commercial licences for company use. Keep whatever assertion library the repository already uses; for new projects use a free alternative (for example AwesomeAssertions or Shouldly) or pin FluentAssertions 7.x.

## Core rules

* Test behaviour, not implementation details.
* Use the lowest effective layer that can catch the defect. Do not duplicate an assertion across layers unless each layer protects a distinct failure mode.
* Existing tests may satisfy a criterion when they directly cover the changed behaviour.
* Do not create production code, interfaces, or abstractions only to give a test something to exercise. Do not test behaviour that is not implemented or being implemented in the same task.
* Keep business calculations pure. Expected values come from the specification or approved examples, never from re-running the code under test. Cover approved examples, boundaries, and distinct equivalence classes, not every permutation.
* Tests are deterministic: control the clock, identifiers, and randomness; never call live external services.
* Do not test trivial records or DTOs, generated code, framework guarantees you do not customize, private members, or logging call counts.
* Coverage is diagnostic; never write or keep tests to hit a percentage.
* Tests may be written before, alongside, or after implementation.
* If test changes materially exceed the implementation, consolidate duplicates and name the distinct risk each remaining test family protects.
* Mark an irrelevant risk category `N/A` with a short concrete rationale instead of adding boilerplate tests.
* Before writing new test helpers, check the `indice-platform` skill for existing ones.

## .NET practices

* Time: inject `TimeProvider` and use `FakeTimeProvider` (`Microsoft.Extensions.TimeProvider.Testing`) in tests. No `DateTime.Now` / `UtcNow` in code under test.
* API integration tests run in-process with `WebApplicationFactory<TProgram>`; replace dependencies with `ConfigureTestServices`.
* Do not use the EF Core InMemory provider to test persistence behaviour; use the real provider through Testcontainers. Reset data between tests (for example with Respawn) or isolate data per test.
* Share expensive setup through `IClassFixture<T>` / `ICollectionFixture<T>` with `IAsyncLifetime`. Avoid static or shared mutable state; xUnit runs test classes in parallel.
* Prefer fakes over mocks, and mock only boundaries you own. For outbound HTTP, stub `HttpMessageHandler` or use WireMock.Net; do not mock `HttpClient`.
* Use fakes or recorded contract fixtures for external providers (payments, identity, messaging, email/SMS); never live credentials.
* Async tests return `Task`; no `async void`, `.Result`, or `.Wait()`.
* Use `[Theory]` with `InlineData` / `MemberData` for equivalence classes and boundaries.
* Capture logs with `ITestOutputHelper` or `FakeLogger<T>` for diagnostics, not to assert call counts.

## Architecture tests (NetArchTest)

* Encode only boundary rules the architecture actually defines: layer dependencies (domain does not reference infrastructure or ASP.NET Core), module isolation, and visibility conventions. Do not encode style preferences or checklists.
* Add or change a rule only when a boundary rule is introduced or changed; otherwise run the existing suite.
* One rule per test. On failure, report the offending types.

```csharp
var result = Types.InAssembly(typeof(Order).Assembly)
    .That().ResideInNamespace("MyApp.Domain")
    .ShouldNot().HaveDependencyOn("Microsoft.EntityFrameworkCore")
    .GetResult();

Assert.True(result.IsSuccessful, string.Join(", ", result.FailingTypeNames ?? []));
```

## E2E tests (Playwright)

* Only for required critical journeys (for example sign-in and the product's core flow) or a material cross-system risk. Edge cases belong in lower layers; keep the suite small.
* Use `Microsoft.Playwright` when the E2E suite lives in the .NET solution; follow the repository if it already uses `@playwright/test`.
* Locate by role, label, or test id (`GetByRole`, `GetByLabel`, `GetByTestId`), not CSS or XPath. Use auto-waiting assertions (`Expect(locator).ToBeVisibleAsync()`); never fixed delays.
* Each test creates its own data and does not depend on execution order.
* Authenticate once and reuse the stored state; only the sign-in test goes through the login UI.
* Run against a dedicated test environment with test accounts, never production or real users. Keep traces and screenshots for failures only.

## Load and concurrency tests (k6 / NBomber)

* Only for defined performance or concurrency requirements, known contention paths, or credible introduced races.
* Every load test declares pass/fail thresholds (for example p95 latency and error rate) through k6 `thresholds` or NBomber assertions. No threshold, no test.
* Prefer k6 for HTTP-level load. Use NBomber when the scenario needs .NET code (in-process clients, non-HTTP protocols), subject to its licence.
* Run against an isolated, production-like environment with synthetic data and stubbed external providers. Never against production or shared environments without agreement.
* Keep load tests out of the regular CI test run; run them on demand or on a schedule.
* For a race on one specific path, a focused integration test that fires parallel requests (`Task.WhenAll`) against a real database is usually enough; reserve load tools for throughput and latency.

## Risk-triggered categories

Apply each category only when the change introduces, changes, or materially exposes that behaviour and no existing test already covers it.

**Authorization**
* Protected operations reject unauthorized callers server-side.
* Test `401` and `403` separately only when both are reachable and the distinction is material.
* In multi-tenant systems, one tenant cannot read or modify another tenant's data, including through direct object references.

**API behaviour**
* Responses are DTOs, not entities. Errors use ProblemDetails. Validation failures return the expected shape and status. Pagination, filtering, and sorting behave as specified. Sensitive existence checks respect anti-enumeration.
* Do not add unauthenticated, forbidden, empty, boundary, pagination, and ProblemDetails tests to every endpoint; apply each only when relevant.

**State transitions**
* Invalid transitions are rejected; guarded states change only through allowed operations.

**Idempotency and concurrency**
* Retries and duplicate messages do not duplicate state changes; handlers are safe to reprocess; out-of-order messages are handled safely.
* Concurrency tests only for defined requirements, known contention paths, or credible introduced races.

**Configuration**
* Missing or invalid configuration fails safely and never silently enables behaviour.

## Test data

Minimal, synthetic, sanitized. No real personal data, production secrets, or live credentials. Prefer builders or fixtures that make the relevant state visible. Avoid hidden defaults that make tests look simpler than production.

## Naming

Readable over clever: `Method_State_ExpectedResult`, or a clear Given / When / Then body for scenario-heavy tests. Add an xUnit `DisplayName` only when the method name cannot express the intent.

```text
CreateOrder_QuantityIsZero_ReturnsValidationProblem
GetOrder_OrderBelongsToAnotherUser_ReturnsNotFound
Submit_AlreadySubmitted_ReturnsConflict
HandleMessage_DuplicateMessageId_ProcessesOnce
CalculateDiscount_ApprovedExample_ReturnsExpectedAmount
```
