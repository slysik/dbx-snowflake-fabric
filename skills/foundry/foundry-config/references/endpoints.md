# Foundry endpoints, api-versions, and env bootstrap

## Endpoint shape

```
https://{resource}.services.ai.azure.com/api/projects/{project}
```

- `{resource}` — the Foundry (Azure AI Services) resource name; it is the host prefix.
- `{project}` — the project under that resource. A resource can hold many projects.

### Discover it without the portal

```bash
# the resource's base endpoint
az cognitiveservices account show -n "$FOUNDRY_RESOURCE" -g "<rg>" \
  --query 'properties.endpoint' -o tsv

# list resources of kind AIServices in the subscription
az cognitiveservices account list \
  --query "[?kind=='AIServices'].{name:name, rg:resourceGroup, endpoint:properties.endpoint}" -o table
```

The data-plane project endpoint adds `/api/projects/{project}` to the resource host.

## api-version map

| Surface | api-version |
|---|---|
| Agents (create/list/get/delete) | `v1` |
| Responses API (`/openai/v1/responses`) | path-versioned (`/openai/v1`), no `?api-version` |
| Threads / runs / messages | `v1` |
| Hosted-agent **versions** (container deploy) | `2025-11-15-preview` |
| Connections, evaluations, deployments (control-plane via ARM) | per-RP, see that skill |

Keep `$AV=v1` as the default; override only for hosted-agent version calls.

## Env bootstrap (paste once per shell)

```bash
export FOUNDRY_RESOURCE=<resource>
export FOUNDRY_PROJECT=<project>
export ENDPOINT="https://$FOUNDRY_RESOURCE.services.ai.azure.com/api/projects/$FOUNDRY_PROJECT"
export AV=v1
```

## Reusable helper — `frest()`

Wraps `az rest` with the correct data-plane audience so you never forget
`--resource`. Add to your shell or a sourced script:

```bash
frest() {
  # usage: frest GET /agents
  #        frest POST /agents @body.json
  local method="$1" path="$2" body="$3"
  local url="$ENDPOINT$path"
  case "$path" in *\?*) ;; */openai/*) ;; *) url="$url?api-version=$AV";; esac
  if [ -n "$body" ]; then
    az rest --resource https://ai.azure.com --method "$method" --url "$url" --body "$body" --headers "Content-Type=application/json"
  else
    az rest --resource https://ai.azure.com --method "$method" --url "$url"
  fi
}
```

Examples:

```bash
frest GET  /agents
frest POST /agents '{"name":"triage","model":"gpt-4o","instructions":"Be terse."}'
frest POST /agents/triage/versions?api-version=2025-11-15-preview @hosted-agent.json
```

## Raw token (when a tool needs the bearer directly)

```bash
az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv
```
