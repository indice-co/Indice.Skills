---
mode: agent
description: Scaffold a new .NET service that follows Indice conventions.
---

Create a new .NET service named `${input:serviceName}` for `${input:purpose}`.

Before writing code:

1. Load the `dotnet-conventions`, `indice-web-api`, and `indice-platform` skills.
2. Check Indice.Platform for existing building blocks that cover the purpose above and list what you found.

Then:

- Create the solution and project layout defined in `dotnet-conventions`.
- Wire DI, `IOptions` configuration, structured logging, and problem-details error handling.
- Follow `indice-web-api` for the endpoint layer: route groups, handlers, `TypedResults`, and OpenAPI metadata.
- Add an integration test project following `dotnet-testing`.
- Summarize which Indice libraries you reused and why.
