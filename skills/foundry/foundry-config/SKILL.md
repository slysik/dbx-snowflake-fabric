---
name: foundry-config
description: "Connect to Microsoft Foundry (Azure AI Foundry / Foundry Agent Service): pick resource + project, build the project endpoint, get a data-plane token, and verify access via az rest. Use when the user mentions \"foundry login\", \"which foundry project\", \"set foundry endpoint\", \"az foundry auth\", \"foundry 401/403\", or \"connect to foundry\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Connection (CLI-first)

**Primary path = Azure CLI** (`az` ≥ 2.81) + `az rest` against the Foundry
**project endpoint**. No MCP server, no SDK required — `az` ships the auth and the
REST client. The Azure AI Projects SDK is an optional convenience only.

Mental model: **resource → project → endpoint → token**. Every other `foundry-*`
skill links here for auth instead of re-explaining it.

```bash
export FOUNDRY_RESOURCE=<your-resource-name>     # the *.services.ai.azure.com host prefix
export FOUNDRY_PROJECT=<your-project-name>
export ENDPOINT="https://$FOUNDRY_RESOURCE.services.ai.azure.com/api/projects/$FOUNDRY_PROJECT"
export AV=v1                                       # stable agents/responses; hosted-agent versions use 2025-11-15-preview
```

> **Token gotcha:** `az rest` defaults to an ARM token. The Foundry data plane
> needs audience `https://ai.azure.com` — always pass
> `--resource https://ai.azure.com`. Omitting it is the #1 cause of 401s.

Standard connection contract: **Interactive · Service principal · Verify · Troubleshoot**.

## Interactive (dev default)

```bash
az login                                          # device/browser
az account set --subscription <sub-id-or-name>
az account show --query user.name -o tsv          # who am I
```

The endpoint comes from the Foundry portal (Project → Overview → "Project endpoint")
or `az cognitiveservices account show -n $FOUNDRY_RESOURCE -g <rg> --query properties.endpoint`.

## Service principal (headless / cron / CI)

```bash
az login --service-principal -u "$AZURE_CLIENT_ID" -p "$AZURE_CLIENT_SECRET" --tenant "$AZURE_TENANT_ID"
# OIDC/federated (GitHub Actions, no secret): az login --service-principal -u "$AZURE_CLIENT_ID" --tenant "$AZURE_TENANT_ID" --federated-token "$ID_TOKEN"
```

The SP needs the **Azure AI User** role on the project (or **Azure AI Developer**
to author). Assign with `az role assignment create`.

## Verify (single command)

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/agents?api-version=$AV"
```

Returns `200` + a (possibly empty) agent list when token + endpoint + RBAC are all
healthy. This one call proves the whole contract.

## Troubleshoot

| Symptom | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | ARM token sent to data plane | Add `--resource https://ai.azure.com` to `az rest`. |
| `403 Forbidden` | Missing role on project | Grant **Azure AI User** (run) / **Azure AI Developer** (author) via `az role assignment create`. |
| `404` on the URL | Wrong endpoint shape or project name | Endpoint must be `…/api/projects/<project>`; confirm `$FOUNDRY_PROJECT`. |
| `Unsupported api-version` | Wrong `$AV` | `v1` for agents/responses; `2025-11-15-preview` for hosted-agent versions. |
| `az: command not found` / old | CLI missing/stale | Install/upgrade `az` ≥ 2.81. |
| Token expired mid-session | `az` token TTL | Re-run `az login` (interactive) or re-auth the SP. |

## Load which sub-doc

| Need | Read |
|---|---|
| Endpoint discovery, api-version map, env bootstrap, reusable `frest()` helper | `references/endpoints.md` |
| RBAC role assignment commands, federated/OIDC SP setup, extended error decoding | `references/auth.md` |
