---
name: foundry-content-safety
description: "Apply and inspect Microsoft Foundry content safety — content filters (RAI policies), prompt shields / jailbreak detection, and groundedness — on deployments and agent responses. Use when the user wants to \"add a content filter\", \"block harmful content\", \"prompt shield / jailbreak protection\", \"check safety verdicts\", or \"set a RAI policy\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Content Safety (CLI-first)

Two layers: **RAI policies** attached to a deployment (control plane), and the
**per-response verdicts** returned inline at runtime. Auth/env from
**[foundry-config](../foundry-config/SKILL.md)**.

## Built-in RAI policies (verified)

```bash
SUB=$(az account show --query id -o tsv)
az rest --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/raiPolicies?api-version=2024-10-01" \
  --query 'value[].name' -o tsv
# Microsoft.Default      (baseline)
# Microsoft.DefaultV2    (adds prompt shields / jailbreak)
```

Attach a policy to a deployment with `--rai-policy-name` on
`az cognitiveservices account deployment create/update`
([foundry-model-catalog](../foundry-model-catalog/SKILL.md)).

## Runtime verdicts (verified)

Every Responses call returns `content_filters[]` inline:

```json
"content_filters":[{"blocked":false,"content_filter_results":{
  "hate":{"severity":"safe"}, "jailbreak":{"detected":false,"filtered":false} }}]
```

Check `blocked` and per-category `severity`/`detected` to gate or log.

## Load which sub-doc

| Need | Read |
|---|---|
| Custom RAI policy (per-category thresholds, prompt shields, blocklists), attaching to deployments, standalone Content Safety API (analyze text/image), groundedness detection | `references/filters.md` |
