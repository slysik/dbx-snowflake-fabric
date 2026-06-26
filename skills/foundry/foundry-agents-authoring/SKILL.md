---
name: foundry-agents-authoring
description: "Create, update, version, and delete Microsoft Foundry agents via az rest — both prompt agents (serverless) and hosted agents (container). Use when the user wants to \"create a foundry agent\", \"update agent instructions\", \"new agent version\", \"deploy a hosted agent\", \"delete an agent\", or define an agent's model/tools."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Agent Authoring (CLI-first)

Author agents with `az rest` against the project endpoint. Auth + `$ENDPOINT` +
`$AV` come from **[foundry-config](../foundry-config/SKILL.md)** — set those first.
No SDK, no MCP required.

Two kinds, one resource shape (`versions.latest.definition.kind`):

| Kind | What it is | api-version |
|---|---|---|
| `prompt` | Serverless agent = model + instructions + tools. No infra. | `v1` |
| `hosted` | Your container, Foundry runs it (scaling, identity, observability). | `2025-11-15-preview` |

## Create a prompt agent (verified)

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/agents?api-version=$AV" --headers "Content-Type=application/json" \
  --body '{"name":"triage","definition":{"kind":"prompt","model":"gpt-4.1","instructions":"Be terse."}}'
```

`model` must be a **deployed** model name in this project (see
[foundry-model-catalog](../foundry-model-catalog/SKILL.md)). Response includes the
agent `id`, a managed identity (`blueprint`/`instance_identity`), and
`versions.latest` with `version:"1"`.

## Inspect / update / version / delete (verified)

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/agents?api-version=$AV"            # list
az rest --resource https://ai.azure.com --url "$ENDPOINT/agents/triage?api-version=$AV"     # get
az rest --resource https://ai.azure.com --method delete --url "$ENDPOINT/agents/triage?api-version=$AV"
```

Updating instructions/model/tools creates a **new version** under the same agent
(`versions.latest` advances; old versions stay addressable as `triage:1`, `triage:2`).

## Load which sub-doc

| Need | Read |
|---|---|
| Full prompt-agent body (tools array, response_format, update→new-version flow, version pinning) | `references/prompt-agents.md` |
| Hosted (container) agents: image, resources, `versions?api-version=2025-11-15-preview`, rollout | `references/hosted-agents.md` |

Run agents → [foundry-agents-runtime](../foundry-agents-runtime/SKILL.md).
Give them tools → [foundry-agent-tools](../foundry-agent-tools/SKILL.md).
