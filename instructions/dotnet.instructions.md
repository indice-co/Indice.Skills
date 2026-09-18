---
applyTo: "**/*.cs"
---
# Indice .NET conventions (always on)
- Follow the common `dotnet-conventions` skill.
- Before writing new backend code, check Indice.Platform (see the `indice-platform` skill) and say what you checked.
- Where an imported skill (for example `dotnet/skills`) and an Indice skill disagree, the Indice skill wins.
- Never put secrets, credentials, or customer data in code or config files; reference Key Vault / App Configuration instead.
