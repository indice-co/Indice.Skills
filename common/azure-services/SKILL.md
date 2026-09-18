---
name: azure-services
description: >
  Use when choosing or configuring Azure services for an Indice product: which
  services we default to (App Service / Container Apps, Azure SQL, Storage,
  Service Bus, Key Vault, App Configuration, Application Insights) and when to
  pick each.
---

# Azure services

## Purpose
The Azure services Indice standardizes on and the decision rules for picking
between them. For hands-on Azure operations, the pinned `microsoft/azure-skills`
baseline applies; this skill records Indice defaults on top of it.

## Default services
| Need | Default | When to choose something else |
| --- | --- | --- |
| Hosting | App Service / Container Apps | TODO |
| Relational data | Azure SQL | TODO |
| Files / blobs | Storage | TODO |
| Messaging | Service Bus | TODO |
| Secrets | Key Vault | Never store secrets elsewhere. |
| Configuration | App Configuration | TODO |
| Observability | Application Insights | TODO |

## Identity
- Managed Identity first; Key Vault for secrets. See the `azure-auth-identity` skill.

## Examples
TODO
