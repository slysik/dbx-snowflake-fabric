---
name: foundry-agents-runtime
description: "Run Microsoft Foundry agents and get answers via the Responses API and threads/runs, using az rest. Use when the user wants to \"run a foundry agent\", \"ask the agent\", \"get a response\", \"start a conversation/thread\", \"stream agent output\", or \"continue a thread\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Agent Runtime (CLI-first)

Invoke agents with `az rest`. Auth + `$ENDPOINT` come from
**[foundry-config](../foundry-config/SKILL.md)**. Author agents first with
**[foundry-agents-authoring](../foundry-agents-authoring/SKILL.md)**.

Two ways to call an agent:

| Path | When | Endpoint |
|---|---|---|
| **Responses** (stateless) | One-shot Q&A, simplest | `/openai/v1/responses` |
| **Threads / runs** (stateful) | Multi-turn conversation, tool loops | `/threads`, `/threads/{id}/runs` |

## Responses — one call (verified)

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/responses" --headers "Content-Type=application/json" \
  --body '{"input":"say PONG","agent_reference":{"name":"triage","type":"agent_reference"}}' \
  --query 'output[].content[].text' -o tsv
```

> **Verified gotchas:** the field is `agent_reference` (not `agent` — that's
> deprecated), and it **requires** `"type":"agent_reference"`. Add `"version":"1"`
> to pin a version. The responses path is version-in-URL (`/openai/v1`), so no
> `?api-version`.

## Load which sub-doc

| Need | Read |
|---|---|
| Response object shape, output/text extraction, pinning version, streaming (SSE via `curl --no-buffer`), content-filter fields | `references/responses.md` |
| Threads: create → add message → create run → poll status → read messages; tool-call loop | `references/threads.md` |
