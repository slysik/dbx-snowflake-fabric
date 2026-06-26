# Tracing — spans, KQL, toggles

## Gen-AI span attributes (OpenTelemetry semantic conventions)

Foundry traces follow the `gen_ai.*` conventions. Key attributes on spans:

| Attribute | Meaning |
|---|---|
| `gen_ai.system` | `az.ai.inference` / provider |
| `gen_ai.request.model` | deployment used |
| `gen_ai.usage.input_tokens` / `output_tokens` | token counts |
| `gen_ai.operation.name` | `chat`, `execute_tool`, `agent` |
| `gen_ai.tool.name` | which tool ran |
| `server.address` | the project endpoint |

Spans land in App Insights `dependencies` (calls) and `traces` (logs).

## Useful KQL

```kusto
// token usage per model, last day
dependencies
| where timestamp > ago(1d) and isnotempty(customDimensions['gen_ai.request.model'])
| extend model=tostring(customDimensions['gen_ai.request.model']),
         inTok=toint(customDimensions['gen_ai.usage.input_tokens']),
         outTok=toint(customDimensions['gen_ai.usage.output_tokens'])
| summarize calls=count(), in=sum(inTok), out=sum(outTok) by model

// slow tool calls
dependencies
| where name == 'execute_tool' and duration > 2000
| project timestamp, tool=tostring(customDimensions['gen_ai.tool.name']), duration
| order by duration desc

// error rate
dependencies
| summarize errors=countif(success==false), total=count() by bin(timestamp, 5m)
| extend rate = todouble(errors)/total
```

## Content recording toggle

By default prompt/completion **content** is not recorded (privacy). To capture it
for debugging, set on the tracing client/env:

```bash
export AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true
```

Leave off in production unless you have a data-handling reason; content may contain
PII. Pair safety verdicts from
[foundry-content-safety](../../foundry-content-safety/SKILL.md) with traces to audit
blocked responses.

## Local trace capture (no App Insights)

Point OTLP at a local collector to eyeball spans during dev:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```
