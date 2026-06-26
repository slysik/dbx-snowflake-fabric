# Responses API — reference (verified against a live project)

## Request

```json
{
  "input": "say PONG",
  "agent_reference": { "name": "triage", "type": "agent_reference", "version": "1" }
}
```

- `agent_reference.type` is **required** (`"agent_reference"`).
- `version` optional — omit for `@latest`.
- `input` can be a string or the structured message array (`[{ "role":"user",
  "content":[{ "type":"input_text", "text":"…" }] }]`).

## Extract just the answer text

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/responses" --headers "Content-Type=application/json" \
  --body '{"input":"say PONG","agent_reference":{"name":"triage","type":"agent_reference"}}' \
  --query 'output[].content[].text' -o tsv
# -> PONG
```

## Response object (shape that matters)

```jsonc
{
  "agent_reference": { "name": "triage", "type": "agent_reference", "version": "1" },
  "completed_at": 1782508686,
  "content_filters": [ { "blocked": false, "content_filter_results": { "hate": {"severity":"safe"}, "jailbreak": {"detected":false} } } ],
  "output": [ { "content": [ { "type": "output_text", "text": "PONG" } ] } ]
}
```

- `output[].content[].text` — the model text.
- `content_filters[]` — Azure content-safety verdicts inline (see
  [foundry-content-safety](../../foundry-content-safety/SKILL.md)).
- `completed_at` present when finished; `background:true` requests poll instead.

## Streaming (SSE)

`az rest` buffers, so for token streaming use `curl` with the bearer from
foundry-config and `"stream": true`:

```bash
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
curl -sS --no-buffer "$ENDPOINT/openai/v1/responses" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"input":"stream a haiku","stream":true,"agent_reference":{"name":"triage","type":"agent_reference"}}'
# -> event: response.output_text.delta  data: {...}
```

The SDK is the ergonomic option for heavy streaming, but it is never required —
`curl` is the contract here.

## Errors seen live

| Code | Message | Fix |
|---|---|---|
| `invalid_payload` | `'agent' property is deprecated. Use 'agent_reference'` | Rename the field. |
| `invalid_payload` | `Required properties ["type"] are not present` | Add `"type":"agent_reference"`. |
