# Azure AI Search backend for RAG

Use when the corpus is large/shared, you need hybrid (vector + keyword) search with
filters, or an index already exists. Heavier than the built-in vector store —
prefer that unless you need Search.

## 1. Connect Search to the project

Register a connection (see
[foundry-connections](../../foundry-connections/references/connections.md)):

```json
{ "properties": { "category": "CognitiveSearch",
  "target": "https://<search>.search.windows.net", "authType": "AAD" } }
```

Grant the project managed identity **Search Index Data Reader** on the service.

## 2. Create an index with a vector field

```bash
SKEY=$(az search admin-key show --service-name <search> -g "$RG" --query primaryKey -o tsv)
curl -sS -X PUT "https://<search>.search.windows.net/indexes/kb?api-version=2024-07-01" \
  -H "api-key: $SKEY" -H "Content-Type: application/json" -d '{
    "name":"kb",
    "fields":[
      {"name":"id","type":"Edm.String","key":true},
      {"name":"content","type":"Edm.String","searchable":true},
      {"name":"contentVector","type":"Collection(Edm.Single)","dimensions":1536,
       "vectorSearchProfile":"vp","searchable":true}
    ],
    "vectorSearch":{"profiles":[{"name":"vp","algorithm":"hnsw"}],
                    "algorithms":[{"name":"hnsw","kind":"hnsw"}]}
  }'
```

`dimensions: 1536` matches `text-embedding-3-small`
([foundry-model-catalog](../../foundry-model-catalog/SKILL.md)).

## 3. Embed + push documents

Embed each chunk via the deployed embedding model, then upload:

```bash
# embedding for one chunk
R(){ az rest --resource https://ai.azure.com "$@"; }
VEC=$(R --method post --url "$ENDPOINT/openai/v1/embeddings" --headers "Content-Type=application/json" \
  --body '{"model":"text-embedding-3-small","input":"chunk text"}' --query 'data[0].embedding' -o json)

curl -sS -X POST "https://<search>.search.windows.net/indexes/kb/docs/index?api-version=2024-07-01" \
  -H "api-key: $SKEY" -H "Content-Type: application/json" \
  -d "{\"value\":[{\"@search.action\":\"upload\",\"id\":\"1\",\"content\":\"chunk text\",\"contentVector\":$VEC}]}"
```

## 4. Ground an agent on Search

Attach an Azure AI Search tool referencing the connection + index, then query via the
Responses API:

```json
{ "type": "azure_ai_search",
  "azure_ai_search": { "connection_id": "<connection-name>", "index_name": "kb",
                       "query_type": "vector_semantic_hybrid", "top_k": 5 } }
```

Hybrid + semantic ranking gives the best grounding; results come back cited like
`file_search`. For small/simple corpora, the built-in vector store
([vector-store-rag.md](vector-store-rag.md)) needs none of this.
