---
name: foundry-fine-tuning
description: "Fine-tune models on Microsoft Foundry — prepare JSONL training data, launch and monitor a fine-tuning job, then deploy the tuned model. Use when the user wants to \"fine-tune a model\", \"train on my data\", \"create a fine-tuning job\", \"check training status\", or \"deploy a fine-tuned model\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Fine-tuning (CLI-first)

Fine-tuning uses the OpenAI-compatible `/openai/v1/fine_tuning/jobs` surface
(verified reachable on the project endpoint). Auth/env from
**[foundry-config](../foundry-config/SKILL.md)**. Flow: **data → job → deploy**.

> Prefer prompt engineering + RAG ([foundry-rag-search](../foundry-rag-search/SKILL.md))
> first; fine-tune for style/format/latency, not for fresh knowledge.

## 1. Upload training data (JSONL, chat format)

```bash
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
FID=$(curl -sS "$ENDPOINT/openai/v1/files" -H "Authorization: Bearer $TOKEN" \
      -F purpose=fine-tune -F file=@train.jsonl \
      | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")
```

Each line: `{"messages":[{"role":"system","content":"…"},{"role":"user","content":"…"},{"role":"assistant","content":"…"}]}`.

## 2. Launch the job

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/fine_tuning/jobs" --headers "Content-Type=application/json" \
  --body "{\"model\":\"gpt-4.1\",\"training_file\":\"$FID\"}"
```

## 3. Monitor

```bash
az rest --resource https://ai.azure.com --url "$ENDPOINT/openai/v1/fine_tuning/jobs" --query 'data[].{id:id,status:status}'
```

## Load which sub-doc

| Need | Read |
|---|---|
| JSONL prep + validation, hyperparameters, events/checkpoints, deploying the tuned model, cost notes | `references/jobs.md` |
