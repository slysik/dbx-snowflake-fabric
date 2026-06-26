---
name: foundry-connections
description: "Register and inspect Microsoft Foundry connections — Azure AI Search, Storage, Key Vault, other AI services — so agents and projects can reach external resources. Use when the user wants to \"add/list a connection\", \"connect to AI Search/Storage\", \"wire a resource to the project\", or hits a missing-connection error."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Connections (CLI-first)

A connection links the project to an external resource (Search, Storage, Key Vault,
another AI service) with a defined auth mode. Auth/env from
**[foundry-config](../foundry-config/SKILL.md)**.

Connections follow the same contract as auth: **Interactive · Service principal ·
Verify · Troubleshoot** — applied per target.

## List (verified)

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/connections?api-version=$AV"
# -> {"value": []}   (empty on a fresh project)
```

## Interactive (create a connection)

```bash
SUB=$(az account show --query id -o tsv)
az rest --method put \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/projects/$PROJECT/connections/my-search?api-version=2025-06-01" \
  --headers "Content-Type=application/json" --body @connection.json
```

## Service principal

The project's **managed identity** is the preferred auth target — set
`authType: AAD` in `connection.json` and grant that identity a role on the resource
(e.g. **Search Index Data Reader**). Avoid embedding keys.

## Verify

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/connections/my-search?api-version=$AV"
```

## Troubleshoot

| Symptom | Cause | Fix |
|---|---|---|
| `value: []` after create | Created on account vs project scope | Use the `/projects/$PROJECT/connections/...` path. |
| Agent can't read target | Managed identity lacks role | Grant the project identity the data role on the target. |
| `401` from target at run time | Key expired / wrong authType | Prefer `AAD`; rotate keys in Key Vault. |

## Load which sub-doc

| Need | Read |
|---|---|
| `connection.json` per target (AI Search, Blob, Key Vault, AI Services), authType options, AAD role grants | `references/connections.md` |
