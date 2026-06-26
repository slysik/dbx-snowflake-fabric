---
name: foundry-model-catalog
description: "Browse the Microsoft Foundry model catalog and deploy models (serverless GlobalStandard or managed) so agents can use them. Use when the user wants to \"list/deploy a model\", \"what models are available\", \"add gpt-4.1 / an embedding model\", \"create a deployment\", or \"set up a model for my agent\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Model Catalog & Deployments (CLI-first)

Agents reference a **deployed** model by name (not a catalog id). Deployments are an
**account-level (control-plane)** resource — managed with the `az cognitiveservices`
CLI. Auth/sub from **[foundry-config](../foundry-config/SKILL.md)**.

```bash
export RES=<resource>   RG=<resource-group>     # the AIServices account holding your project
```

## List what's deployed (verified)

```bash
az cognitiveservices account deployment list -n "$RES" -g "$RG" \
  --query '[].{name:name, model:properties.model.name, sku:sku.name}' -o table
# gpt-4.1                 gpt-4.1                 GlobalStandard
# text-embedding-3-small  text-embedding-3-small  Standard
```

## Deploy a model

```bash
az cognitiveservices account deployment create -n "$RES" -g "$RG" \
  --deployment-name gpt-4.1 \
  --model-name gpt-4.1 --model-version "2025-04-14" --model-format OpenAI \
  --sku-name GlobalStandard --sku-capacity 50
```

The `--deployment-name` is what agents put in `definition.model`.

## Load which sub-doc

| Need | Read |
|---|---|
| Browse the full catalog, SKUs (GlobalStandard vs Standard vs ProvisionedManaged), capacity/quota, model-router, update & delete deployments | `references/deploy.md` |

Use the deployment in an agent → [foundry-agents-authoring](../foundry-agents-authoring/SKILL.md).
Embedding deployments power RAG → [foundry-rag-search](../foundry-rag-search/SKILL.md).
