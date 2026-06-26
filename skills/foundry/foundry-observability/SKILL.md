---
name: foundry-observability
description: "Trace and monitor Microsoft Foundry agents — wire Application Insights, capture OpenTelemetry traces of agent/tool calls, and query usage, latency, and errors. Use when the user wants to \"trace an agent\", \"add monitoring/observability\", \"connect Application Insights\", \"see token usage/latency\", or \"debug what the agent did\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Observability (CLI-first)

Foundry emits **OpenTelemetry** traces (agent runs, tool calls, model calls) to an
**Application Insights** resource connected to the project. Auth/env from
**[foundry-config](../foundry-config/SKILL.md)**.

## Connect Application Insights

```bash
# create (or reuse) an App Insights component
APPI=$(az monitor app-insights component create --app foundry-ai -g "$RG" -l <region> \
       --query connectionString -o tsv)

# register it as a project connection
SUB=$(az account show --query id -o tsv)
az rest --method put \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/projects/$PROJECT/connections/appinsights?api-version=2025-06-01" \
  --headers "Content-Type=application/json" \
  --body "{\"properties\":{\"category\":\"AppInsights\",\"target\":\"$APPI\",\"authType\":\"AAD\"}}"
```

Once connected, agent runs/tool calls/model calls are traced automatically.

## Query traces (KQL)

```bash
AID=$(az monitor app-insights component show --app foundry-ai -g "$RG" --query appId -o tsv)
az monitor app-insights query --app "$AID" \
  --analytics-query 'dependencies | where timestamp > ago(1h) | summarize calls=count(), p95=percentile(duration,95) by name | order by calls desc'
```

## Load which sub-doc

| Need | Read |
|---|---|
| OTel span attributes for gen-ai (model, tokens, tool name), useful KQL (token usage, error rate, slow tool calls), local trace capture, content-recording toggle | `references/tracing.md` |
