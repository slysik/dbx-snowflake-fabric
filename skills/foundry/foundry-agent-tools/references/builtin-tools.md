# Built-in tools — code_interpreter & file_search

Both are managed by Foundry — you attach them in `definition.tools[]`; the runtime
executes them inside a response/run.

## code_interpreter

```json
{ "type": "code_interpreter" }
```

Sandboxed Python for math, data wrangling, chart/file generation. No extra config.
The model decides when to run code; results come back inline in
`output[].content[]`. Generated files surface as file annotations in the output.

## file_search (RAG over your docs)

```json
{ "type": "file_search", "vector_store_ids": ["vs_abc123"] }
```

- `vector_store_ids` is **required** (verified: omitting it →
  `Required properties ["vector_store_ids"] are not present`).
- Build/populate the vector store in
  [foundry-rag-search](../../foundry-rag-search/SKILL.md), then paste its id here.
- At answer time the model retrieves chunks and grounds the response; citations
  appear as annotations on the output text.

### Wire-up order

1. Create a vector store + upload/index files (`foundry-rag-search`).
2. Attach `file_search` with that `vs_…` id to the agent.
3. Ask a question via the Responses API — the answer cites the indexed docs.

## Inspecting tool activity

The Responses output includes the tool steps the model took; pull the full object
(drop the `--query`) to see code runs and retrieval citations. For deeper traces
use [foundry-observability](../../foundry-observability/SKILL.md).
