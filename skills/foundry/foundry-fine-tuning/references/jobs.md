# Fine-tuning jobs — prep, tune, deploy

## Data prep & validation

JSONL, one chat sample per line:

```jsonl
{"messages":[{"role":"system","content":"You are a terse SRE bot."},{"role":"user","content":"disk full on db-1"},{"role":"assistant","content":"Run: df -h; rotate logs in /var/log; expand volume."}]}
```

Validate before upload:

```bash
python3 - <<'PY'
import json
ok=0
for i,l in enumerate(open("train.jsonl")):
    o=json.loads(l); assert "messages" in o and len(o["messages"])>=2, f"line {i}"
    ok+=1
print("valid samples:", ok)
PY
```

Aim for ≥ 50 high-quality examples (hundreds is better). Keep a held-out file for
`validation_file`.

## Hyperparameters

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/openai/v1/fine_tuning/jobs" --headers "Content-Type=application/json" \
  --body "{\"model\":\"gpt-4.1\",\"training_file\":\"$FID\",\"validation_file\":\"$VID\",
           \"hyperparameters\":{\"n_epochs\":3,\"batch_size\":\"auto\",\"learning_rate_multiplier\":\"auto\"},
           \"suffix\":\"sre-bot\"}"
```

## Monitor events & checkpoints

```bash
JID=<job_id>
az rest --resource https://ai.azure.com --url "$ENDPOINT/openai/v1/fine_tuning/jobs/$JID" --query '{status:status,model:fine_tuned_model}'
az rest --resource https://ai.azure.com --url "$ENDPOINT/openai/v1/fine_tuning/jobs/$JID/events" --query 'data[].message'
az rest --resource https://ai.azure.com --url "$ENDPOINT/openai/v1/fine_tuning/jobs/$JID/checkpoints"
# cancel: POST …/jobs/$JID/cancel
```

When `status=succeeded`, `fine_tuned_model` holds the new model id.

## Deploy the tuned model

Deploy it like any model ([foundry-model-catalog](../../foundry-model-catalog/SKILL.md)),
using the `fine_tuned_model` id as `--model-name`:

```bash
az cognitiveservices account deployment create -n "$RES" -g "$RG" \
  --deployment-name sre-bot \
  --model-name "<fine_tuned_model_id>" --model-format OpenAI \
  --sku-name Standard --sku-capacity 10
```

Then reference `sre-bot` as an agent's `definition.model`.

## Cost & care

Fine-tuning bills for training tokens + hosting the deployment. Tune for
style/format/tool-use reliability/latency — use RAG for knowledge that changes.
