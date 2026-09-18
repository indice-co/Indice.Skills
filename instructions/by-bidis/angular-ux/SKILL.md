---
name: angular-ux
description: >
  Use when designing or implementing Angular screens with PrimeNG: app posture
  (customer-facing vs back-office), folder and feature structure, when to use a
  route vs dialog vs drawer vs inline edit, PrimeNG component selection, forms,
  copy, screen states, tables, status, accessibility, and the UI review checklist.
---

# Angular + PrimeNG UX workflow

Turns approved requirements into consistent, modern, high-quality UI without inventing product behaviour, regulated logic, or one-off interaction patterns.

This skill assumes PrimeNG as the component foundation. If the project uses `Indice.Angular` or another library, apply the same rules and map components accordingly.

## Core rule

The UI must feel premium, modern, clear, fast, trustworthy, consistent, and low-friction. The user should never need to think twice about where they are, what something means, what they can do, what happens next, whether an action succeeded, why an action is blocked, or how to recover from an error.

PrimeNG gives the building blocks. The product owns the experience. Do not ship a default PrimeNG-looking app.

## Non-negotiables

* Do not implement UI directly from raw requirement text; decide the pattern first (see the page checklist).
* Same intent = same pattern. Do not use a modal in one place and a drawer or route in another for the same class of task.
* Do not duplicate regulated decision logic in the browser. Financial, eligibility, fee, tax, payment, KYC, or AML truth is never calculated client-side.
* Do not hardcode legal, payment, tax, or regulated error copy. It comes from server-provided, configurable content.
* Do not build unbounded client-side lists.
* Do not use raw PrimeNG where a project wrapper exists. Do not bypass generated API clients.
* Disabled buttons, hidden menus, and route guards are not security. The server authorizes.
* No dark patterns: urgency manipulation, shame, deceptive scarcity, or pressure loops.
* Clarity, trust, and accessibility outrank visual flash.

## App posture

Customer-facing and back-office apps stay separate. They serve different users, permissions, density, risk, and workflows. Share only genuinely reusable UI through a small library: design tokens, basic layout primitives, form field wrappers, error display, empty-state and loading components, generated API clients, and formatting utilities. Never share business workflow components.

| | Customer-facing app | Back-office app |
| --- | --- | --- |
| Posture | Guided, simple, mobile-first, trust-first, low cognitive load, warm copy. | Dense, operational, fast, review-oriented, evidence-first, keyboard-efficient, direct copy. |
| Visuals | Richer imagery, premium cards, progress moments, trust badges, cinematic hero areas. | Compact density, stable layouts, clear tables, strong filters, status tags, timelines, low motion, highly visible warnings. |
| Must not | Pressure spending, hide fees or rules, create false urgency, make blocked users feel punished. | Decorative hero sections, excessive animation, hidden primary actions, icon-only ambiguous controls, non-standard containers. |
| Responsive | Mobile-first, thumb-friendly, stacked layouts, cards instead of dense tables. | Desktop-first, usable on laptop/tablet, preserve density, state minimum viewport where needed. |

## Angular baseline

App shell, runtime configuration, auth wiring, generated clients, the UI host, build, and test stack are in the `angular-architecture` skill.

Required: standalone components; feature-first folders; lazy-loaded feature routes; `OnPush` change detection; signals for local component state where appropriate; generated API clients from OpenAPI where available; typed models and DTOs; small feature components; shallow hierarchies; container/presentation separation where useful.

Avoid: broad shared modules; dumping everything into `shared`; huge smart components; subscription leaks; uncontrolled signal/effect loops; client-side business-rule engines; UI state that tries to become a second backend.

### Folder structure

```text
apps/<app>/src/app/
  app.routes.ts
  core/          # app-level infrastructure only: auth, api, layout, config, permissions, error-handling
  shared-ui/     # reusable UI primitives, not business workflows: buttons, forms, tables, overlays, status, feedback
  features/      # business screens by capability
    <feature>/
      routes.ts
      pages/        # orchestrate data loading and routing
      components/   # focused UI pieces, isolated forms
      models/       # view models
      mappers/      # shape DTOs into display models; never invent business meaning
```

Shared UI must not depend on features. Do not put API calls inside small visual components. A component must not manage layout, fetch data, run commands, map errors, and decide business rules all at once.

## Wrapping PrimeNG

Use raw PrimeNG only for simple, low-risk display elements. Create project wrappers for buttons, form fields, date pickers, dialogs, drawers, tables, filters, paginators, confirmations, toasts, status tags, empty/error/loading states, money and progress display, and action menus.

Wrappers standardize spacing, density, labels, validation display, error handling, icons, sizes, severity mapping, accessibility attributes, loading, disabled/blocked behaviour, and responsive behaviour.

Before adding a component: Is there a wrapper? Use it. Is there an existing pattern for this interaction? Reuse it. Is it a new interaction class? Document the pattern before using it broadly. Does it hide important information or add cognitive load? Redesign. Does it touch regulated or financial truth? Server-confirmed values only. Is it keyboard and screen-reader accessible? Required.

## Route vs dialog vs drawer vs inline

The most important consistency decision.

| Use | When | Not for |
| --- | --- | --- |
| Dedicated route | Primary object creation; complex or multi-step editing; review before submit; validation-heavy forms; bookmarkable, refresh-safe flows; regulated or financial workflows; anything the user may leave and return to. | Tiny tasks. |
| Dialog | Short, focused, one-screen, low-risk create/edit; confirmation; quick add of a supporting item while the parent stays visible. Needs a clear title, primary action, secondary action, close behaviour, and error handling. | Multi-step flows, large tables, mini-pages, regulated high-risk flows. |
| Drawer | Contextual inspection, side-by-side review, back-office triage, evidence preview, activity history, related records. | Full workflows. If it needs tabs, complex forms, nested tables, and multiple actions, it needs a route. |
| Inline edit | Simple, reversible, low-risk, single-field, non-regulated values. | Permissions, financial values, regulated statuses, legal copy, anything needing an audit reason. |

| Question | Route | Dialog | Drawer | Inline |
| --- | ---: | ---: | ---: | ---: |
| More than 5 fields? | Strong | Weak | Weak | No |
| Multi-step or save draft? | Strong | No | Weak | No |
| Deep validation or audit reason? | Strong | Weak | Medium | No |
| Regulated or financial? | Strong | Only if approved | Review only | No |
| Needs URL, share, bookmark, or abandon-and-return? | Strong | No | No | No |
| Parent list context important? | Medium | Medium | Strong | Medium |
| One or two simple fields? | Weak | Strong | Medium | Strong |

Defaults: primary object create/edit = route; child or supporting object = dialog; inspect or triage = drawer; simple low-risk field = inline. If unsure, use a route.

## Page anatomy

Every screen must answer: Where am I? What is this about? What can I do? What matters most? What needs attention? What happens next?

```text
Page shell
  Breadcrumbs, on deep detail pages
  Page header: title, subtitle or status summary, primary action, secondary actions / overflow menu
  Context or status strip, where useful
  Main content: summary cards or key facts; form, table, details, or workflow
  Supporting content: activity, evidence, help, related records
```

Titles: back-office uses `<Noun> <identifier or name>` (for example "Order OR-10092"). Customer-facing uses plain, user-centred language (for example "Complete your verification").

## Visual direction

Modern does not mean confusing. Use strong hierarchy, confident whitespace, elegant cards, subtle depth, a premium typography scale, high-quality iconography, restrained gradients, refined motion, crisp status indicators, and polished empty states. Glass or glow effects only where they do not reduce readability.

Avoid colour overload, low contrast, decorative shadows everywhere, competing accent colours, unclear glassmorphism, childish gamification, and dark patterns.

Motion: subtle, never delays task completion, respects reduced-motion preferences, no infinite animation outside loading. Use for page transitions, overlay entrance, skeletons, hover/focus, progress, success. Avoid for critical warnings, dense tables, dramatically changing financial numbers, and regulated decision moments.

## PrimeNG component catalogue

Use the component that matches the job. This is not permission to use every component everywhere.

### Buttons and commands

| Component | Use for | Avoid when |
| --- | --- | --- |
| Button | Primary, secondary, tertiary actions | Too many competing buttons |
| SplitButton | Primary action plus closely related alternatives | Alternatives are unrelated or risky |
| SpeedDial | Floating quick actions, mostly mobile | Back-office tables or regulated actions |
| ConfirmDialog | Risky, destructive, irreversible confirmation | Lightweight reversible actions |
| ConfirmPopup | Small contextual confirmation | High-risk or regulated actions |
| Menu / TieredMenu | Grouped secondary actions | Primary workflow navigation |
| ContextMenu | Expert back-office shortcuts | Main discoverable actions |

One primary action per section. Secondary actions visible but quieter. Destructive actions are never primary by colour alone. Risky actions need confirmation with consequence. Disabled buttons explain why where useful.

### Layout and containers

| Component | Use for | Avoid when |
| --- | --- | --- |
| Card | Summary panels, entity cards, metric cards | Dense grids where a table is better |
| Panel | Contained, optionally collapsible sections | Primary page structure everywhere |
| Accordion | Progressive disclosure of secondary content | Required content |
| Tabs | Peer sections on the same object | Sequential workflows |
| Fieldset | Grouped form sections | Where a card or section is cleaner |
| Splitter | Resizable operational workspaces | Customer journeys or simple forms |
| Toolbar | Page or list action bars | Generic content layout |
| Stepper / Steps | Multi-step process, must show where the user is | Non-linear sections |

### Overlays

| Component | Use for | Avoid when |
| --- | --- | --- |
| Dialog | Focused modal task | Complex primary flow |
| Drawer | Contextual side panel | Full-page workflow |
| Popover / OverlayPanel | Small contextual content or action | Critical information, long forms |
| Tooltip | Short hints | Required instructions |
| Toast | Temporary confirmation or error | Only evidence of important state |
| Message / InlineMessage | Persistent inline feedback | Global temporary notices |

Required guidance is visible inline, never tooltip-only. Toasts disappear; never rely on them for audit-level or high-risk confirmation.

### Forms and inputs

| Component | Use for | Notes |
| --- | --- | --- |
| InputText / Textarea | Text | Always a visible label; character guidance where needed |
| Password / InputOtp | Credentials, OTP | Follow the IAM pattern; do not invent auth flows |
| InputNumber | Simple numeric UI | Not money truth |
| InputMask | Structured values | Only when the format is stable |
| DatePicker | Dates | Server-approved date rules |
| Select / MultiSelect / AutoComplete | Single, multiple, or searched choice | Server-provided options where configurable; search for large sets |
| Checkbox / RadioButton / SelectButton | Boolean or small exclusive sets | Radio beats dropdown for 2 to 5 options; label states consequence |
| ToggleSwitch | Immediate binary setting | Confirm high-risk changes |
| Slider / Rating / ColorPicker | Approximate or config-tool values | Never for precise money or regulatory values |
| Chips | Token input | Validate tokens server-side |

### Data display

| Component | Use for | Avoid when |
| --- | --- | --- |
| DataTable | Operational lists and back-office grids, server-side | Cards are more scannable |
| TreeTable / Tree | Hierarchical data or navigation | Flat data |
| DataView | Customer-facing card/list switch | Dense operational data |
| OrderList / PickList | Reordering, moving between sets | Large sets without search |
| Timeline | History, audit, status trail | Current editable data |
| Carousel / Galleria / Image | Media browsing and previews, with alt text and fallbacks | Required content, sensitive documents without access control |
| Tag / Badge | Status, severity, counts | Long text; badge as only status cue |
| Skeleton / ProgressSpinner | Page loading / small blocking waits | Spinner for page content |
| ProgressBar / MeterGroup | Progress toward a target | Values not server-confirmed |
| Chart | Trends and KPIs | When a table is needed for evidence |

### Navigation and utilities

| Component | Use for | Avoid when |
| --- | --- | --- |
| Menubar / MegaMenu | Top-level app or portal navigation | Deep back-office navigation |
| PanelMenu | Back-office side navigation | Customer-facing primary nav |
| Breadcrumb | Location on deep detail pages | Very shallow flows |
| TabMenu | Peer section switching | Sequential forms |
| Paginator / VirtualScroller | Server-side paging; large read-only option sets | Client-side paging of server-sized data |
| FocusTrap | Dialog and drawer accessibility | Skipping it on custom overlays |
| Ripple / StyleClass / AnimateOnScroll | Polish, controlled style toggles, content pages | Critical workflows; use consistently or not at all |

Navigation labels use user language. Active state is visible. Back-office preserves context between list and detail.

## Forms

Every field: label, helper text where useful, input, validation message.

* Labels always visible, close to the field, plain language, describe the data not the column. Placeholder is never a label; use it only for examples.
* Required and optional are clearly marked.
* Helper text when the field has consequences, affects another step, has a non-obvious format, is configurable, is shown to users, feeds reporting or audit, or cannot be changed later. Not for obvious fields.
* Group fields by the user mental model, not the database. Never "Miscellaneous", "General", "Other".
* Long forms: sections, stepper for sequential processes, sticky summary or action bar, progress, save draft only if the backend supports it, no required fields in collapsed panels.
* Validation is layered: client for fast feedback, server as source of truth, ProblemDetails as the canonical response, field mapping for recovery. Client validation is convenience only; never rely on it for eligibility, limits, payment, tax, or KYC rules.
* Never hardcode option lists for countries, currencies, payment methods, legal choices, or limits. Use server-provided options.
* Do not mark an action successful until the server confirms it.
* Show validation on blur or submit. Messages say what to fix in plain language. Preserve input unless sensitive. Focus the first invalid field on submit. Form-level summary for long forms; field errors next to the field.
* Submit button near the end, stating the outcome. Predictable cancel/back.

## Copy

Clear, calm, confident, human, concise, precise, non-manipulative. Customer-facing may be warmer; back-office is direct.

* Buttons state the action: "Save changes", "Send invitation", "Download report". Never "OK", "Submit", "Yes".
* Confirmation explains consequence: title as a question, body with what happens and whether it is audited, primary action named after the action, secondary action that keeps the current state.
* Error copy identifies the problem, says what the user can do, avoids jargon and blame, and includes a support or correlation reference where useful.
* Empty state copy says what is missing, why it matters, what to do next.
* Blocked state copy gives the safe reason and what happens next, without shaming.
* Where localized copy is required, provide every required language (typically English and Greek) in a table of UI element, English, Greek. Legal, tax, payment, consent, privacy, marketing-consent, and eligibility copy comes from approved configurable content and is never translated freely.

## Screen states

Define only the states the screen can actually reach. Asynchronous screens normally have loading, error, and success; empty, forbidden, not found, validation error, pending, and partial apply only when reachable.

* Loading: skeleton for page, card, table; spinner for small blocking actions; button loading state on submit; no layout shift.
* Empty: clear title, short explanation, next action if allowed, no fake data.
* Error: safe message, retry where useful, correlation reference where provided, never a raw stack trace or provider message.
* Forbidden: neutral explanation, no existence leak, route back to a safe place.
* Success: what happened, what is next, a persistent record where relevant. Never toast-only for major operations.

Back-office screens may also reach: partial data unavailable, action unavailable, evidence missing, manual review required, export pending or failed, provider callback delayed. Customer-facing screens may also reach: action blocked, verification pending, limit reached, payment pending or failed, not available in this region.

## Tables and lists

* Back-office tables are server-side: pagination, sorting, filtering, default sort, allowed filters, page size.
* Search: minimum 3 characters unless specified, debounced, visible searching state, only fields the API supports, state preserved when returning from detail where useful.
* Filters match API allowed filters, use server-provided options, show as removable chips, have a clear reset, and are never hover-only.
* Row actions: most common safe action may be visible; secondary actions in a menu; risky actions confirmed; forbidden actions hidden or disabled from server capabilities, with a reason where useful. Primary list-wide action lives outside the table.
* Show empty, loading, error, and forbidden states. Avoid horizontal scroll and frozen columns unless density justifies them.
* Totals state their scope: current page, selected rows, filtered result, or all matching. Show the total count when the API provides it; the API provides authoritative totals where they matter. Never present client-side page totals as global financial truth.
* Exports only through an approved, safe flow; bulk actions only when explicitly approved.

## Status

Same status = same label and same severity everywhere. No colour-only meaning. Use canonical status terms from the API. No synonyms ("Pending review" vs "Awaiting review", "Failed" vs "Error").

| Meaning | Severity |
| --- | --- |
| Success / complete / active | success |
| Info / neutral | info |
| Warning / needs attention / manual review | warning |
| Error / failed / blocked | danger |
| Draft / cancelled / pending | secondary |
| Restricted / forbidden | danger or contrast |

## Dashboards

Every metric card defines name, value, period, scope, source, trend meaning, and last-updated timestamp where relevant. No vanity metrics, unlabelled percentages, or charts without axes, legend, and context. No regulated figures without a backend-confirmed source. Do not mix figures from different periods without labels.

## Regulated UI

The browser may display regulated state. It must not decide it.

| Area | UI may display | UI must not decide |
| --- | --- | --- |
| Payments | server-confirmed payment status | success or failure without server or PSP confirmation |
| Ledger | server-confirmed facts and totals | financial truth from local calculations |
| KYC / AML | server-confirmed gate status | pass or fail |
| Tax | server-confirmed result | formula or calculation |
| Compliance reporting | server-confirmed report status | figures not provided by the backend |
| Legal copy / consent | approved copy and version | legal wording or consent validity |

The UI may display and format server-confirmed values. Display the `feeBreakdown` the API returned; do not recalculate fees. Display `canProceed=false` with the server-provided reason; do not decide eligibility from local flags. Display a progress value from the API; do not compute it from a client-side list.

Prefer API responses that carry capabilities, and render actions from them:

```json
{
  "id": "order_123",
  "status": "Open",
  "allowedActions": { "approve": false, "cancel": true },
  "blockedReasons": { "approve": "Required documents are missing." }
}
```

Render actions from `allowedActions`, show `blockedReasons` where helpful, still submit the command to the server, and never assume an allowed action from role alone.

## Errors and ProblemDetails

Map server ProblemDetails to user-facing errors; never invent client-side semantics for server decisions. Field errors go to the matching fields, action-wide errors to the form level, `403` to the forbidden state, `404` to the not-found state. Use safe generic wording where anti-enumeration matters, for example account, KYC, payment, or invite lookups. Preserve the correlation ID or support reference. Never reveal whether a sensitive record exists, and never render sensitive data the API did not return for the authenticated user and scope.

## Accessibility

Semantic HTML; labels programmatically associated with inputs; visible focus; dialogs and drawers trap focus; keyboard users can complete critical journeys; links are links and buttons are buttons; no colour-only meaning; errors associated with fields; meaningful table headers; accessible labels on icon-only buttons; loading and status changes announced where appropriate; no hover-only required functionality. No third-party accessibility widgets as a substitute.

## Performance

Use lazy-loaded routes, skeletons, button-level loading, optimistic UI only when safe and reversible, server-side paging/filtering/sorting, stable `trackBy`, virtual scroll only where it helps, debounced search, and cached reference data only when safe and scoped. Avoid loading huge reference sets on start, client-side filtering of server-sized data, repeated calls from uncontrolled effects, unnecessary large re-renders, and blocking the page for small actions. Never optimize by weakening authorization, tenant isolation, audit, idempotency, or server-confirmed truth.

## Error prevention

Good defaults, clear labels, constraints, helper text, confirmation for high-risk actions, disabled actions with reasons, a review step for high-risk forms, and server validation before irreversible transitions. Risky confirmations state what will happen, whether it is reversible, whether it is audited, and which records are affected.

## Page checklist

Before implementing any page, answer: Which app? Which route owns the screen? Is there an existing pattern? Route, dialog, drawer, or inline, and why? Primary user goal, primary action, secondary actions? What data is server-confirmed? Which states are reachable? Which permissions or capabilities? Which copy source, and which languages? Is a regulated area touched? What must not be computed client-side? What proportionate verification covers this UI?

If the answers are not in the approved requirement, record the UI decisions there or stop and ask. Do not implement UI first and rationalize it later.

## Workflow

1. Read the approved requirement and its UI decisions.
2. Identify the app and check existing routes, feature folders, shared wrappers, and the existing pattern for the same interaction.
3. Decide route, dialog, drawer, or inline.
4. Implement only the approved scope with generated API clients and server-confirmed values.
5. Add the reachable states and map ProblemDetails to fields.
6. Add or update the tests the verification plan requires, and record UI evidence in the review.

## Final review checklist

* Existing pattern reused; container choice justified; no raw PrimeNG accidentally creating a new pattern.
* Reachable states exist: loading, error, success, and empty or forbidden where relevant.
* Forms have visible labels, helper text where needed, no placeholder-as-label, server errors mapped to fields, ProblemDetails handled.
* Actions use server-confirmed capabilities; server-side authorization remains the boundary; no regulated logic or client-side financial totals in the UI.
* Copy source respected; required languages present; status labels and severity consistent.
* Lists are server-side; totals state scope; risky actions confirmed.
* Critical journeys work by keyboard.
* UI behaviour maps proportionately to verification.

When unsure: prefer route over modal for important workflows, drawer over modal for back-office inspection, visible text over icon-only, server capabilities over client role checks, inline help over tooltips, existing wrapper over raw PrimeNG, clarity over novelty, calm trust over excitement in regulated moments, and stopping over guessing.
