---
name: foundry-agent-tools
description: "Give Microsoft Foundry agents tools — code interpreter, file search (RAG), custom function tools, and connected/grounded agents — in the agent definition via az rest. Use when the user wants an agent to \"run code\", \"search my files/documents\", \"call my function/API\", \"use a tool\", or \"ground answers\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Agent Tools (CLI-first)

Tools live in the agent's `definition.tools[]` array (authored via
**[foundry-agents-authoring](../foundry-agents-authoring/SKILL.md)**; auth/env via
**[foundry-config](../foundry-config/SKILL.md)**). Schemas below are **verified
live** — note they are **flat** (Responses-style), not nested.

| Tool type | Minimal schema (verified) | Notes |
|---|---|---|
| `code_interpreter` | `{"type":"code_interpreter"}` | Sandboxed Python. |
| `function` | `{"type":"function","name":"…","description":"…","parameters":{…}}` | **Flat** — `name`/`parameters` at tool level, not under a `function` object. You execute it. |
| `file_search` | `{"type":"file_search","vector_store_ids":["vs_…"]}` | `vector_store_ids` **required**; build the store in [foundry-rag-search](../foundry-rag-search/SKILL.md). |

## Attach tools (verified)

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/agents?api-version=$AV" --headers "Content-Type=application/json" \
  --body '{"name":"helper","definition":{"kind":"prompt","model":"gpt-4.1","instructions":"Use tools.",
    "tools":[
      {"type":"code_interpreter"},
      {"type":"function","name":"get_weather","description":"Get weather","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}
    ]}}'
```

Round-trip echoes each tool back; `function` gains `"strict": null` by default.

## Load which sub-doc

| Need | Read |
|---|---|
| `code_interpreter` + `file_search` usage, file/vector-store wiring, citations in output | `references/builtin-tools.md` |
| Custom `function` tools: schema, the function-call loop (read tool call → run it → return output), `strict` mode | `references/function-tools.md` |

Grounding pipelines → [foundry-rag-search](../foundry-rag-search/SKILL.md).
