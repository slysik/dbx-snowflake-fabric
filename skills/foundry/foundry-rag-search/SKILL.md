---
name: foundry-rag-search
description: "Build retrieval-augmented generation on Microsoft Foundry: index documents into a built-in vector store (or Azure AI Search) and ground agent answers via file_search. Use when the user wants to \"add RAG\", \"ground answers in my docs\", \"search my documents\", \"build a vector store\", \"upload and index files\", or \"cite sources\"."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — RAG & Search (CLI-first)

Two grounding backends. Pick by scale:

| Backend | When | Setup |
|---|---|---|
| **Built-in vector store** | Up to ~10k files, fastest path, no extra resource | This skill — verified end-to-end. |
| **Azure AI Search** | Large/shared corpora, hybrid + filters, existing index | `references/ai-search.md` + a connection. |

Auth/env from **[foundry-config](../foundry-config/SKILL.md)**. The vector-store id
goes into a `file_search` tool ([foundry-agent-tools](../foundry-agent-tools/SKILL.md)).

## Built-in vector store — verified pipeline

```bash
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
R(){ az rest --resource https://ai.azure.com "$@"; }

VS=$(R --method post --url "$ENDPOINT/openai/v1/vector_stores" --headers "Content-Type=application/json" \
     --body '{"name":"kb"}' --query id -o tsv)                                   # vs_…  status: completed

FID=$(curl -sS "$ENDPOINT/openai/v1/files" -H "Authorization: Bearer $TOKEN" \
     -F purpose=assistants -F file=@./doc.txt | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

R --method post --url "$ENDPOINT/openai/v1/vector_stores/$VS/files" \
  --headers "Content-Type=application/json" --body "{\"file_id\":\"$FID\"}"      # status -> completed
```

Then attach `{"type":"file_search","vector_store_ids":["'"$VS"'"]}` to an agent and
ask — the answer is grounded and cited. Full run (upload → index → query → cleanup)
in `references/vector-store-rag.md`.

## Load which sub-doc

| Need | Read |
|---|---|
| Verified end-to-end vector-store RAG run, indexing status polling, citations, file upload via curl multipart | `references/vector-store-rag.md` |
| Azure AI Search backend: connection, index schema, embeddings, hybrid query, attach to agent | `references/ai-search.md` |
