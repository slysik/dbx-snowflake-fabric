# Hosted (container) agents — reference

A hosted agent is your own code, packaged as a container, that Foundry runs with a
managed endpoint, autoscaling, identity, and observability. Versions are created
under the **preview** api-version.

> Requires a container image in a registry Foundry can pull (e.g. Azure Container
> Registry the project can access). Prompt agents need none of this — prefer them
> unless you need custom framework code.

## Create a hosted-agent version

```bash
az rest --resource https://ai.azure.com --method post \
  --url "$ENDPOINT/agents/<name>/versions?api-version=2025-11-15-preview" \
  --headers "Content-Type=application/json" \
  --body @hosted-agent.json
```

`hosted-agent.json`:

```json
{
  "definition": {
    "kind": "hosted",
    "container": {
      "image": "<acr-name>.azurecr.io/my-agent:1.0.0",
      "port": 8088,
      "env": [ { "name": "LOG_LEVEL", "value": "info" } ]
    },
    "resources": { "cpu": "1", "memory": "2Gi" },
    "scaling": { "min_replicas": 0, "max_replicas": 3 }
  }
}
```

## Manage versions / rollout

```bash
# list versions
az rest --resource https://ai.azure.com \
  --url "$ENDPOINT/agents/<name>/versions?api-version=2025-11-15-preview" --query 'data[].version'

# get a version
az rest --resource https://ai.azure.com \
  --url "$ENDPOINT/agents/<name>/versions/2?api-version=2025-11-15-preview"

# delete a version
az rest --resource https://ai.azure.com --method delete \
  --url "$ENDPOINT/agents/<name>/versions/2?api-version=2025-11-15-preview"
```

Traffic is steered by the agent's `agent_endpoint.version_selector`
(`version_selection_rules` with `agent_version` + `traffic_percentage`) — use it
for canary/blue-green between versions.

## Registry access

The agent's managed identity (or the project identity) needs **AcrPull** on the
registry:

```bash
az role assignment create --assignee "<agent-or-project-principal-id>" \
  --role AcrPull --scope "$(az acr show -n <acr-name> --query id -o tsv)"
```

> The preview api-version (`2025-11-15-preview`) moves; it is centralized in
> [foundry-config](../../foundry-config/references/endpoints.md). Update there once.
