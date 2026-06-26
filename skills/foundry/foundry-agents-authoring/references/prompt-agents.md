# Prompt agents — full reference

A prompt agent is a versioned `definition` of kind `prompt`. Every edit produces a
new version under the same agent name.

## Create body (all common fields)

```json
{
  "name": "triage",
  "definition": {
    "kind": "prompt",
    "model": "gpt-4.1",
    "instructions": "You route support tickets. Be terse.",
    "tools": [
      { "type": "code_interpreter" },
      { "type": "file_search" }
    ],
    "response_format": { "type": "text" },
    "temperature": 0.2,
    "metadata": { "team": "support" }
  }
}
```

- `model` — a **deployed** model name in the project (not a catalog id).
- `tools` — see [foundry-agent-tools](../../foundry-agent-tools/SKILL.md) for each type's schema.
- `response_format` — `{"type":"text"}` or `{"type":"json_schema", "json_schema":{…}}`.

## Verified create + lifecycle (run end-to-end)

```bash
# create
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/agents?api-version=$AV" --headers "Content-Type=application/json" \
  --body '{"name":"triage","definition":{"kind":"prompt","model":"gpt-4.1","instructions":"Reply with exactly: PONG"}}'

# get -> shows versions.latest.definition.{kind,model,instructions}
az rest --resource https://ai.azure.com \
  --url "$ENDPOINT/agents/triage?api-version=$AV" \
  --query '{id:id, model:versions.latest.definition.model, kind:versions.latest.definition.kind}'

# delete -> {"deleted": true, "object": "agent.deleted"}
az rest --resource https://ai.azure.com --method delete \
  --url "$ENDPOINT/agents/triage?api-version=$AV"
```

## Update = new version

Re-POST (or PATCH) with changed `definition`; `versions.latest.version` advances
(`"1"` → `"2"`). Pin a specific version when running by passing
`"version":"1"` inside `agent_reference` (see runtime skill).

```bash
# list every version of one agent
az rest --resource https://ai.azure.com \
  --url "$ENDPOINT/agents/triage/versions?api-version=$AV" --query 'data[].version'
```

## Notes

- Agent names are the addressable id; keep them stable.
- Each agent gets a **managed identity** (`blueprint.principal_id`) — grant it
  data access (Search, Storage) via roles when it needs grounding.
- `protocols: ["responses"]` on the created agent confirms it is callable through
  the Responses API.
