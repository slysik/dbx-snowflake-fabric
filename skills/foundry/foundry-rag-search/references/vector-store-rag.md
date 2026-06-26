# Built-in vector-store RAG — verified end-to-end

This exact run was executed against a live project: a secret was injected into a
file, indexed, and an agent retrieved it. Every call below succeeded.

```bash
export ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"
export AV=v1
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)
R(){ az rest --resource https://ai.azure.com "$@"; }

# 1. doc with distinctive content
echo "The Gates project access code is EMBER-7731. Do not share." > doc.txt

# 2. vector store  (returns status: completed immediately)
VS=$(R --method post --url "$ENDPOINT/openai/v1/vector_stores" \
     --headers "Content-Type=application/json" --body '{"name":"kb"}' --query id -o tsv)

# 3. upload file (multipart -> curl; az rest can't multipart). purpose=assistants
FID=$(curl -sS "$ENDPOINT/openai/v1/files" -H "Authorization: Bearer $TOKEN" \
      -F purpose=assistants -F file=@doc.txt \
      | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

# 4. index file into the store
R --method post --url "$ENDPOINT/openai/v1/vector_stores/$VS/files" \
  --headers "Content-Type=application/json" --body "{\"file_id\":\"$FID\"}"

# 5. poll until indexed
until [ "$(R --url "$ENDPOINT/openai/v1/vector_stores/$VS/files/$FID" --query status -o tsv)" = completed ]; do sleep 2; done

# 6. RAG agent
R --method post --url "$ENDPOINT/agents?api-version=$AV" --headers "Content-Type=application/json" \
  --body "{\"name\":\"kb-agent\",\"definition\":{\"kind\":\"prompt\",\"model\":\"gpt-4.1\",
           \"instructions\":\"Answer only from retrieved files.\",
           \"tools\":[{\"type\":\"file_search\",\"vector_store_ids\":[\"$VS\"]}]}}"

# 7. grounded query
R --method post --url "$ENDPOINT/openai/v1/responses" --headers "Content-Type=application/json" \
  --body '{"input":"What is the Gates project access code?","agent_reference":{"name":"kb-agent","type":"agent_reference"}}' \
  --query 'output[].content[].text' -o tsv
# -> The Gates project access code is EMBER-7731. Do not share this information.

# 8. cleanup
R --method delete --url "$ENDPOINT/agents/kb-agent?api-version=$AV"
R --method delete --url "$ENDPOINT/openai/v1/vector_stores/$VS"
curl -sS -X DELETE "$ENDPOINT/openai/v1/files/$FID" -H "Authorization: Bearer $TOKEN"
```

## Notes

- **Upload uses multipart** — `curl -F` with the bearer from foundry-config; `az
  rest` cannot send multipart.
- `purpose=assistants` for files used by `file_search`.
- Small text files index in seconds (`status: completed` on first poll); large PDFs
  take longer — always poll the file's status under the vector store.
- The model returns citations as annotations on `output[].content[]`; drop the
  `--query` to see them.
- Re-use one vector store across many agents; attach the same `vs_…` id.
