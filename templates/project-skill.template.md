# Project skill starter

Copy this into your product repo's agent-config folder. A project skill captures
*what this product is and the business rules it enforces*. It should point to the
common skills in Indice.Skills rather than repeat them.

Keep secrets, credentials, and customer data **out** of skills. Reference where
they live (Key Vault, App Configuration), never the values.

## 1. On-demand skill: `<product>-domain/SKILL.md`

Use `SKILL.template.md` for the body. Fill in:
- **Domain glossary**: entities, statuses, roles, in the product's own words.
- **Business rules & invariants**: e.g. "an invoice can't be cancelled after settlement".
- **Architecture map**: main modules/services, how they talk, where new code goes.
- **Integrations**: external systems and which Indice / 3rd-party libraries are used.
- **Do / Do not**: product-specific guardrails and known traps.

## 2. Always-on instructions: `<product>.instructions.md`

```markdown
---
applyTo: "**/*.cs"
---
# <Product> backend conventions
- Follow the common `dotnet-conventions` skill.
- Persist money as <type>; never use double for currency.
- All external calls go through <Indice library / internal client>.
```

## 3. Recurring workflow: `new-feature.prompt.md` (optional)

Pair the project skill with a prompt so recurring work is one command that
already carries the right context:

```markdown
---
mode: agent
description: Add a feature to <Product> following its domain rules.
---
Load the `<product>-domain` skill and the relevant common skills, check the
Indice libraries for existing functionality, then implement: ${input:feature}
```
