---
applyTo: "**/*.{ts,html,scss}"
---
# AI engineering rules: front-end

Scoped companion to [`engineering-rules.instructions.md`](engineering-rules.instructions.md). The core file's precedence, definitions, and non-overridable rules apply here.

## Front-end rules

* Use the Angular patterns and shared component library already established in the repository.
* Do not duplicate regulated decision logic in the UI. Use server-provided configuration for legal copy, limits, currencies, countries, payment methods, and product availability.
* Handle loading, empty, error, forbidden, and success states.
* Keep accessibility and responsive behaviour consistent with the design system.
* UI checks are never the security boundary; see Security rules in the core file.
