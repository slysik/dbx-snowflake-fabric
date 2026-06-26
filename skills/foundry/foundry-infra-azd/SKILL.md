---
name: foundry-infra-azd
description: "Provision Microsoft Foundry infrastructure — resource (AIServices account), project, and model deployments — with the Azure CLI or azd / Bicep / Terraform. Use when the user wants to \"create a foundry resource/project\", \"provision foundry\", \"azd up\", \"bicep/terraform for foundry\", or \"stand up a new project from scratch\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Infrastructure (CLI-first)

Stand up the resource + project + a model deployment so the other `foundry-*`
skills have something to talk to. Auth from
**[foundry-config](../foundry-config/SKILL.md)**.

## Fast path — pure az CLI

```bash
RG=rg-foundry RES=my-foundry PROJECT=my-proj LOC=eastus2
az group create -n "$RG" -l "$LOC"

# AIServices account (the Foundry resource)
az cognitiveservices account create -n "$RES" -g "$RG" -l "$LOC" \
  --kind AIServices --sku S0 --custom-domain "$RES" --yes

# project under it
SUB=$(az account show --query id -o tsv)
az rest --method put \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/projects/$PROJECT?api-version=2025-06-01" \
  --headers "Content-Type=application/json" \
  --body '{"location":"'"$LOC"'","identity":{"type":"SystemAssigned"},"properties":{}}'

# a model so agents can run
az cognitiveservices account deployment create -n "$RES" -g "$RG" \
  --deployment-name gpt-4.1 --model-name gpt-4.1 --model-version "2025-04-14" \
  --model-format OpenAI --sku-name GlobalStandard --sku-capacity 50
```

Then build the endpoint per
[foundry-config](../foundry-config/references/endpoints.md) and verify.

## Load which sub-doc

| Need | Read |
|---|---|
| `azd up` template layout, Bicep module for account+project+deployment+role, Terraform variant, teardown | `references/provision.md` |
