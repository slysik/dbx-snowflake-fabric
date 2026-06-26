# Content safety — custom policies, shields, groundedness

## Custom RAI policy

```bash
SUB=$(az account show --query id -o tsv)
az rest --method put \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/raiPolicies/strict?api-version=2024-10-01" \
  --headers "Content-Type=application/json" --body '{
    "properties":{
      "mode":"Blocking",
      "contentFilters":[
        {"name":"Hate","blocking":true,"enabled":true,"severityThreshold":"Medium","source":"Prompt"},
        {"name":"Hate","blocking":true,"enabled":true,"severityThreshold":"Medium","source":"Completion"},
        {"name":"Violence","blocking":true,"enabled":true,"severityThreshold":"High","source":"Completion"},
        {"name":"Jailbreak","blocking":true,"enabled":true,"source":"Prompt"},
        {"name":"ProtectedMaterialText","blocking":true,"enabled":true,"source":"Completion"}
      ]
    }}'
```

Categories: `Hate`, `Sexual`, `Violence`, `SelfHarm`, `Jailbreak` (prompt shield),
`IndirectAttack` (XPIA), `ProtectedMaterialText/Code`. `severityThreshold`:
`Low|Medium|High`. `source`: `Prompt|Completion`.

## Attach to a deployment

```bash
az cognitiveservices account deployment update -n "$RES" -g "$RG" \
  --deployment-name gpt-4.1 --rai-policy-name strict
```

## Standalone Content Safety API (pre-screen arbitrary text)

> **Verified gotcha:** this surface lives on the **resource host**, not the
> project path. Use `https://$FOUNDRY_RESOURCE.services.ai.azure.com/contentsafety/…`
> (the `/api/projects/…` endpoint returns `API version not supported`).

```bash
CS="https://$FOUNDRY_RESOURCE.services.ai.azure.com/contentsafety"
az rest --resource https://ai.azure.com --method post \
  --url "$CS/text:analyze?api-version=2024-09-01" \
  --headers "Content-Type=application/json" \
  --body '{"text":"...","categories":["Hate","Violence","SelfHarm","Sexual"]}'
# verified -> {"categoriesAnalysis":[{"category":"Hate","severity":0}, …], "blocklistsMatch":[]}
```

Image variant: `image:analyze`. Use to screen user input *before* it reaches an
agent, or to moderate retrieved/generated content.

## Groundedness detection

For RAG, detect ungrounded ("hallucinated") claims:

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$CS/text:detectGroundedness?api-version=2024-09-15-preview" \
  --headers "Content-Type=application/json" \
  --body '{"domain":"Generic","task":"QnA","text":"<answer>","groundingSources":["<retrieved chunk>"],"qna":{"query":"<question>"}}'
# -> ungroundedDetected + ungroundedPercentage + details
```

Pair with [foundry-rag-search](../../foundry-rag-search/SKILL.md) to reject or flag
answers that aren't supported by the retrieved sources.
