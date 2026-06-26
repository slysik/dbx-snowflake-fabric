---
name: foundry-evaluation
description: "Evaluate Microsoft Foundry agents and models — create evals, run them over a dataset, score with graders (string check, label model, AI judge). Use when the user wants to \"evaluate an agent\", \"score outputs\", \"build an eval\", \"add a judge/grader\", \"regression-test prompts\", or \"measure quality\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Evaluation (CLI-first)

Evals use the OpenAI-compatible `/openai/v1/evals` surface on the project endpoint.
Auth/env from **[foundry-config](../foundry-config/SKILL.md)**. Two parts: an **eval**
(schema + grading criteria) and a **run** (data + the thing under test).

## Create an eval (verified shape)

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/evals" --headers "Content-Type=application/json" --body '{
    "name":"qa-quality",
    "data_source_config":{"type":"custom","include_sample_schema":true,
      "item_schema":{"type":"object","properties":{"question":{"type":"string"},"answer":{"type":"string"}}}},
    "testing_criteria":[{"type":"string_check","name":"matches","input":"{{sample.output_text}}","operation":"like","reference":"{{item.answer}}"}]
  }'
# -> { "id": "eval_…", "data_source_config": { "schema": { "item": …, "sample": … } } }
```

`{{item.*}}` = your dataset row; `{{sample.output_text}}` = the model output.

## List / delete

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/openai/v1/evals" --query 'data[].id'
az rest --resource https://ai.azure.com --method delete --url "$ENDPOINT/openai/v1/evals/<eval_id>"
```

## Load which sub-doc

| Need | Read |
|---|---|
| Grader types (string_check, text_similarity, label_model / AI judge, python), creating a **run** with inline or file data, reading scores, CI gating | `references/evals.md` |

Score live agents → pair with [foundry-agents-runtime](../foundry-agents-runtime/SKILL.md).
Safety verdicts → [foundry-content-safety](../foundry-content-safety/SKILL.md).
