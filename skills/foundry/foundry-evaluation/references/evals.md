# Evaluation — graders, runs, gating

## Grader (testing_criteria) types

| type | What it checks |
|---|---|
| `string_check` | Exact/like/contains match vs a reference (`operation`: `eq`,`ne`,`like`,`ilike`). |
| `text_similarity` | Fuzzy/semantic similarity to reference (BLEU/cosine), with a threshold. |
| `label_model` | An **AI judge** — a model labels the output (e.g. `pass`/`fail`) from a rubric prompt. |
| `python` | Arbitrary scoring code. |

### AI-judge (label_model) criterion

```json
{
  "type": "label_model",
  "name": "grounded-judge",
  "model": "gpt-4.1",
  "input": [
    {"role":"system","content":"Label PASS if the answer is supported by {{item.context}}, else FAIL."},
    {"role":"user","content":"Q: {{item.question}}\nA: {{sample.output_text}}"}
  ],
  "passing_labels": ["PASS"],
  "labels": ["PASS","FAIL"]
}
```

## Create a run (execute the eval)

Inline data:

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/evals/<eval_id>/runs" --headers "Content-Type=application/json" --body '{
    "name":"run-1",
    "data_source":{
      "type":"responses",
      "model":"gpt-4.1",
      "input_messages":{"type":"template","template":[{"role":"user","content":"{{item.question}}"}]},
      "source":{"type":"file_content","content":[
        {"item":{"question":"capital of France?","answer":"Paris"}}
      ]}
    }}'
```

Swap `source` to `{"type":"file_id","id":"<file>"}` for a large uploaded dataset
(upload like in [foundry-rag-search](../../foundry-rag-search/references/vector-store-rag.md)).

## Read results

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/openai/v1/evals/<eval_id>/runs/<run_id>" \
  --query '{status:status, counts:result_counts}'
# poll until status=completed; result_counts has passed/failed/errored
```

## CI gating

In a pipeline: create eval (or reuse), start a run over a fixed golden dataset, poll
to `completed`, then fail the build if `result_counts.failed > threshold`. Pure
`az rest` + `jq` — no SDK, no MCP.
