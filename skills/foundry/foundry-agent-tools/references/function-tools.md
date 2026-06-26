# Custom function tools

A function tool lets the agent ask *you* to run code. The model emits a structured
call; your script executes it and returns the result. Foundry never runs your
function — it only describes and routes the call.

## Schema (flat — verified)

```json
{
  "type": "function",
  "name": "get_weather",
  "description": "Get current weather for a city",
  "parameters": {
    "type": "object",
    "properties": { "city": { "type": "string" } },
    "required": ["city"]
  },
  "strict": true
}
```

- **Flat**, not nested. Putting `name`/`parameters` under a `function` object fails
  with `Required properties ["name"] are not present`.
- `strict: true` enforces the JSON schema on the model's arguments (defaults to
  `null`/off when omitted).

## The function-call loop (Responses API)

1. Send the user input to `/openai/v1/responses` with the agent (its definition
   carries the function tool).
2. If the model wants the tool, the response `output[]` contains a
   `function_call` item with `name` + JSON `arguments` + a `call_id`.
3. Run the function yourself; build a `function_call_output`.
4. Send a follow-up response chaining `previous_response_id` and passing the
   tool output in `input`:

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/responses" --headers "Content-Type=application/json" \
  --body "{
    \"previous_response_id\": \"$RID\",
    \"agent_reference\": {\"name\":\"helper\",\"type\":\"agent_reference\"},
    \"input\": [{
      \"type\": \"function_call_output\",
      \"call_id\": \"$CALL_ID\",
      \"output\": \"{\\\"tempC\\\": 21}\"
    }]
  }"
```

5. The model uses the tool output to finish the answer. Loop if it calls again.

## Tips

- Keep `description`s action-oriented — they are the model's only signal for *when*
  to call.
- Validate `arguments` against your own schema before executing; never `eval`
  model output.
- For legacy Assistants (`asst_…`) the equivalent is
  `submit_tool_outputs` on the run — see
  [foundry-agents-runtime](../../foundry-agents-runtime/references/threads.md).
