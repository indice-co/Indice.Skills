---
name: indice-cases
description: >
  Use when an application integrates with an existing Indice Cases deployment:
  letting signed-in customers browse case types and create, fill in, submit,
  attach files to and track their own cases through the My API, or letting
  back-office users and integrations work cases (assign, edit, approve, comment,
  trigger actions, search, report) through the Manage API. Defines the API
  contracts, IAM scopes, client setup, boundaries and what must never be
  duplicated. For creating or hosting a Cases service, use the
  `indice-templates` skill instead.
---

# Indice Cases integration

This skill covers **consuming** Indice Cases. It does not cover hosting it.
To scaffold a Cases host, use the `indice-templates` skill (`indice.cases`).

## Contracts

The OpenAPI documents next to this file are the source of truth. Generate clients from them; do not hand-write DTOs.

| Spec | Consumer | Base path | Flow | Scope |
|---|---|---|---|---|
| [cases-my.json](cases-my.json) — *My cases API* | Signed-in customers (web, mobile, BFF) | `/api/my` | OAuth2 authorization code + PKCE | `cases` |
| `/api/manage` | Authorization code + PKCE (users); **client credentials (machine-to-machine)** | `cases` |

- The `servers`, `authorizationUrl` and `tokenUrl` values in the specs (`cases.indice.gr`, `my.indice.gr`) are examples only. Read the Cases base URL and the IAM authority from configuration for each environment.
- The Manage API supports machine-to-machine access with client credentials, even though the spec only shows the authorization code flow. Use a dedicated client approved in IAM (see `indice-iam`), and give it only the access rules it needs.
- Every error response is a `ProblemDetails`. Validation errors (400) are an `HttpValidationProblemDetails`. Handle 401, 403, 404 and 500 explicitly.

## Case lifecycle

1. **Create a draft:** `POST .../cases` with `CreateDraftCaseRequest`. It needs a `caseTypeCode`; `groupId`, `owner`, `metadata` and `channel` are optional. The response is a `CreateCaseResponse` containing the case `id`.
2. **Fill in the data:** `PUT .../cases/{caseId}` with `UpdateCaseRequest.data`. The data must match the JSON schema of the case type, which you can get from the case-type endpoints. You can only update a case while it is a draft.
3. **Attach files:** `POST .../cases/{caseId}/attachments` (`multipart/form-data`). It returns a `CasesAttachmentLink`.
4. **Submit:** `POST .../cases/{caseId}/submit` takes the case out of draft and starts the workflow.
5. **Track:** the workflow moves the case through checkpoints. Status is one of `Submitted`, `InProgress`, `Completed`, `Deleted`.

Validate `data` against the case type's schema before sending it, and still handle a 400 from the server. The case type's schema and layout define the form; do not hardcode form fields.

## My API (customer)

Every call is made as the signed-in customer. The API limits all results and actions to that user's own cases, and ownership comes from the token. Never pass an owner or user ID, and do not filter by owner on the client. For a customer-facing identifier, show `referenceNumber`, not `caseId`.

| Operation | Endpoint | Notes |
|---|---|---|
| List case types | `GET /api/my/case-types` | Filters: `CaseTypeTags`; paged. |
| Get case type | `GET /api/my/case-types/{caseTypeCode}` | Schema, layout and translations for rendering the form. |
| List my cases | `GET /api/my/cases` | Paged. Filters: `Statuses`, `CaseTypeCodes`, `CaseTypeTags`, `Checkpoints`, `CreatedFrom/To`, `CompletedFrom/To`, `ReferenceNumbers`, `Data`, `Metadata`, `IncludeDrafts`, `IncludeData`. |
| Create draft | `POST /api/my/cases` | `CreateDraftCaseRequest` → `CreateCaseResponse`. |
| Get case | `GET /api/my/cases/{caseId}` | `Case`. |
| Update draft | `PUT /api/my/cases/{caseId}` | `UpdateCaseRequest`. |
| Upload attachment | `POST /api/my/cases/{caseId}/attachments` | `multipart/form-data` → `CasesAttachmentLink`. |
| Download PDF | `GET /api/my/cases/{caseId}/download` | File. |
| Submit | `POST /api/my/cases/{caseId}/submit` | Leaves draft mode. |

Rules:

- Only ask for `IncludeData=true` when you are going to show the data. The list is lighter without it.
- Show the customer the `message` and `checkpointType` translations that come back with the case. Do not map internal checkpoint codes to your own wording.
- For browser apps, keep tokens server-side using a BFF (see `duende-bff`).

## Manage API (back office)

What a caller can do depends on Cases **access rules** (role, group, user, case type, checkpoint), not just on the `cases` scope. Before showing actions, always call `GET /api/manage/cases/{caseId}/actions`, and only show what it returns (`hasAssignment`, `hasUnassignment`, `hasEdit`, `hasApproval`, `customActions`).

Working a case:

| Operation | Endpoint | Body |
|---|---|---|
| Search cases | `GET /api/manage/cases` | Query: `CaseTypeCodes`, `CheckpointTypeCodes`, `GroupIds`, `OwnerIds`, `OwnerTins`, `ReferenceNumbers`, `AssignedTo`, `From/To`, `Data`, `Metadata`, `IncludeData`; paged |
| Get case | `GET /api/manage/cases/{caseId}` | `fetchPublicData` query |
| Create / update / delete draft | `POST /api/manage/cases`, `PUT` and `DELETE /api/manage/cases/{caseId}` | `CreateDraftCaseRequest`, `UpdateCaseRequest` |
| Initialize draft data | `POST /api/manage/cases/{caseId}/data/init` | — |
| Submit | `POST /api/manage/cases/{caseId}/submit` | — |
| Assign to me | `POST /api/manage/cases/{caseId}/assign` | — |
| Edit (workflow) | `POST /api/manage/cases/{caseId}/edit` | `EditCaseRequest` |
| Approve / reject | `POST /api/manage/cases/{caseId}/approve` | `ApprovalRequest` (`action`, `comment`); reasons from `GET .../reject-reasons` |
| Custom action | `POST /api/manage/cases/{caseId}/trigger-action` | `ActionRequest` (`id` taken from `customActions`, `value`) |
| Comment | `POST /api/manage/cases/{caseId}/comment` | `SendCommentRequest` (`comment`, `privateComment`, `replyToCommentId`) |
| Patch metadata | `PATCH /api/manage/cases/{caseId}/metadata` | — |
| Publish private data | `POST /api/manage/cases/{caseId}/publish-private-data` | — |
| Timeline / related cases | `GET .../timeline`, `GET .../related-cases` | — |
| Attachments | `GET`/`POST .../attachments`, `GET .../attachments/{attachmentId}`, `GET .../attachments/{fieldName}`, `GET /api/manage/attachments/{attachmentId}/download` | — |
| PDF | `GET /api/manage/cases/{caseId}.pdf` | — |

Administration and supporting endpoints:

- **Case types:** `GET/POST /api/manage/case-types` (`canCreate` filter); `GET/PUT/DELETE /api/manage/case-types/{caseTypeId}`.
- **Access rules:**
  - Global: `GET/POST /api/manage/access-rules`, `/batch`, `PUT .../{ruleId}/{accessLevel}`, `DELETE .../{ruleId}`.
  - Per case: `GET/POST /api/manage/cases/{caseId}/access-rules`, `/batch`, `/replace`.
- **Lookups and integrations:** `GET /api/manage/lookups/{lookupName}`, `GET /api/manage/integrations/contacts` and `GET /api/manage/integrations/contacts/{reference}`, `GET /api/manage/checkpoint-types`.
- **User features:** saved queries (`GET/POST /api/manage/queries`, `DELETE .../{queryId}`), notification subscriptions (`GET/POST /api/manage/my/notifications`), reports (`GET /api/manage/reports?reportTag=`).

Rules:

- **Workflow first.** Change a submitted case only through workflow actions: `edit`, `approve`, `trigger-action`, `assign`. Never try to get around a checkpoint by writing data directly.
- **Configuration is product behaviour.** Creating or changing case types and access rules changes who can see what and how cases flow. Do it only through an approved, audited change, never as a side effect of business code.
- **PII.** Search results contain owner names, TINs and emails. Never log them, and only request the fields and data you need (`IncludeData=false` by default).
- **Comments.** Set `privateComment: true` for internal notes that customers must not see.

## Client setup (.NET)

1. Generate typed clients for each spec (for example NSwag or Kiota) and use them behind your own service interfaces. Never expose the generated models as your application's domain contracts.
2. **User-facing calls (My API, back-office UI):** forward the user's access token from the authenticated session, for example with the BFF or `Duende.AccessTokenManagement` user token handler. Never swap it for a service token.
3. **Machine-to-machine calls (Manage API):** use a dedicated IAM client with the client credentials grant and the `cases` scope only, with its secret in user-secrets or Key Vault.

```csharp
builder.Services.AddClientCredentialsTokenManagement()
	.AddClient("cases", client => {
		client.TokenEndpoint = new Uri($"{builder.Configuration.GetAuthority(tryInternal: true)!.TrimEnd('/')}/connect/token");
		client.ClientId = ClientId.Parse(builder.Configuration.GetApiSecret("CasesClientId"));
		client.ClientSecret = ClientSecret.Parse(builder.Configuration.GetApiSecret("CasesClientSecret"));
		client.Scope = Scope.Parse("cases");
	});

builder.Services.AddHttpClient<CasesManageClient>(http => http.BaseAddress = new Uri(builder.Configuration.TryGetEndpoint("Cases")!))
	.AddClientCredentialsTokenHandler(ClientCredentialsClientName.Parse("cases"));
```

Fail closed at startup if the authority, endpoint, client ID, secret or scope is missing.

## Boundary

- Cases owns case data, drafts, attachments, checkpoints, workflow state, comments, timeline, access rules and case types. Do not copy any of these into application tables; keep only the `caseId` and `referenceNumber` as references.
- Business decisions belong to the workflow and its approved actions. Do not reimplement approval, assignment or checkpoint logic in your own module.
- Cases authorization happens on the server. Hiding buttons in the UI is never enough on its own.

## Do not copy

Do not copy any of the following from a reference project or from the specs:
- case type codes, schemas or layouts
- checkpoint codes
- access-rule defaults, role names, group IDs or lookup names
- client IDs, secrets or scopes beyond `cases`
- authority and endpoint URLs
- workflow behaviour
