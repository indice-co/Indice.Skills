---
mode: agent
description: Add a new Angular feature that follows Indice conventions and reuses Indice.Angular.
---
Add an Angular feature named `${input:featureName}` that `${input:behaviour}`.

Before writing code:
1. Load the `angular-conventions` and `indice-angular` skills.
2. Check Indice.Angular for existing components, directives, or services that cover this feature and list what you found.

Then:
- Follow the folder structure, state management, and RxJS patterns from `angular-conventions`.
- Use reactive forms and the accessibility baseline from `angular-forms` where forms are involved.
- Add tests following `angular-testing`.
- Summarize which Indice.Angular pieces you reused and why.
