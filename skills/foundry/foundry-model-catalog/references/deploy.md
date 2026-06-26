# Model catalog & deployments — reference

Deployments live on the **AIServices account** (control plane). The `az
cognitiveservices account deployment` CLI is the primary path; ARM `az rest` is the
fallback.

## Browse the catalog

```bash
# models offered to this account (ARM)
SUB=$(az account show --query id -o tsv)
az rest --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/models?api-version=2024-10-01" \
  --query 'value[].{name:model.name, version:model.version, format:model.format}' -o table
```

The Foundry portal catalog is broader (partner/OSS models); deployable ids surface
through the account `models` list and each model's allowed SKUs.

## SKUs

| SKU | What | Use |
|---|---|---|
| `GlobalStandard` | Pay-per-token, global capacity | Default for chat models (e.g. gpt-4.1). |
| `Standard` | Regional pay-per-token | Embeddings, region-pinned needs. |
| `ProvisionedManaged` (PTU) | Reserved throughput | High, steady load with latency SLOs. |

## Deploy (verified shape)

```bash
az cognitiveservices account deployment create -n "$RES" -g "$RG" \
  --deployment-name gpt-4.1 \
  --model-name gpt-4.1 --model-version "2025-04-14" --model-format OpenAI \
  --sku-name GlobalStandard --sku-capacity 50

# embedding model for RAG
az cognitiveservices account deployment create -n "$RES" -g "$RG" \
  --deployment-name text-embedding-3-small \
  --model-name text-embedding-3-small --model-version "1" --model-format OpenAI \
  --sku-name Standard --sku-capacity 120
```

## Update capacity / delete

```bash
az cognitiveservices account deployment list -n "$RES" -g "$RG" -o table
az cognitiveservices account deployment show -n "$RES" -g "$RG" --deployment-name gpt-4.1
az cognitiveservices account deployment delete -n "$RES" -g "$RG" --deployment-name gpt-4.1
```

Capacity is set by `--sku-capacity` (units depend on SKU); raising it may need quota
(`az cognitiveservices usage list -l <region>`).

## Model router

Deploy a `model-router` deployment, then point an agent at it; it auto-routes each
request to the best underlying model for cost/quality. Treat it like any other
deployment name in `definition.model`.
