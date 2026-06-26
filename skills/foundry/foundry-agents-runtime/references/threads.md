# Multi-turn state — threads vs Responses continuation (verified)

There are **two stateful surfaces** on the project endpoint. Pick by which object
you authored.

## TL;DR

| You have… | Use | Continuation |
|---|---|---|
| A new **agent** (`foundry-agents-authoring`) | **Responses API** | `previous_response_id` |
| A legacy **assistant** (`asst_…`) | **threads + runs** | the thread holds history |

> Verified live: creating a run with an `agent` name fails —
> `Invalid 'assistant_id': expected an ID that begins with 'asst'`. Runs belong to
> the Assistants API, **not** to the new agent objects. For agents, drive
> multi-turn through the Responses API.

## Multi-turn with agents (Responses continuation)

```bash
# turn 1 — capture the response id
RID=$(az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/responses" --headers "Content-Type=application/json" \
  --body '{"input":"My name is Sam.","agent_reference":{"name":"triage","type":"agent_reference"}}' \
  --query id -o tsv)

# turn 2 — chain with previous_response_id
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/responses" --headers "Content-Type=application/json" \
  --body "{\"input\":\"What's my name?\",\"previous_response_id\":\"$RID\",\"agent_reference\":{\"name\":\"triage\",\"type\":\"agent_reference\"}}" \
  --query 'output[].content[].text' -o tsv
```

## Threads object (verified create/message/list/delete)

Threads exist and are usable for storing conversation state:

```bash
TID=$(az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/threads?api-version=$AV" --headers "Content-Type=application/json" \
  --body '{}' --query id -o tsv)                       # -> thread_…

az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/threads/$TID/messages?api-version=$AV" \
  --headers "Content-Type=application/json" --body '{"role":"user","content":"say PONG"}'

az rest --resource https://ai.azure.com \
  --url "$ENDPOINT/threads/$TID/messages?api-version=$AV" --query 'data[].role'

az rest --resource https://ai.azure.com --method delete \
  --url "$ENDPOINT/threads/$TID?api-version=$AV"        # -> {"deleted": true}
```

## Legacy Assistants run loop (only when you have an `asst_` id)

```bash
RID=$(az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/threads/$TID/runs?api-version=$AV" --headers "Content-Type=application/json" \
  --body '{"assistant_id":"asst_XXXX"}' --query id -o tsv)

# poll until terminal
until az rest --resource https://ai.azure.com \
  --url "$ENDPOINT/threads/$TID/runs/$RID?api-version=$AV" --query status -o tsv \
  | grep -qE 'completed|failed|requires_action'; do sleep 2; done
```

`requires_action` = the run is waiting on a tool result; submit it to
`/threads/$TID/runs/$RID/submit_tool_outputs`. For new builds prefer agents +
Responses; reach for runs only with existing Assistants resources.
