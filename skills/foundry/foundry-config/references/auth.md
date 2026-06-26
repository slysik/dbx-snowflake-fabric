# Foundry auth — roles, service principals, error decoding

## RBAC roles

| Role | Grants | Use for |
|---|---|---|
| **Azure AI User** | Run agents, create threads/runs, call responses | App / runtime identities |
| **Azure AI Developer** | Author agents, deploy models, manage connections | Builders, CI that creates resources |
| **Azure AI Project Manager** | Manage project, role assignments | Admins |

### Assign a role to a service principal (or user)

```bash
# scope = the project's parent AI Services resource
SCOPE=$(az cognitiveservices account show -n "$FOUNDRY_RESOURCE" -g "<rg>" --query id -o tsv)

az role assignment create \
  --assignee "<sp-object-id-or-app-id>" \
  --role "Azure AI User" \
  --scope "$SCOPE"
```

Verify:

```bash
az role assignment list --assignee "<app-id>" --scope "$SCOPE" -o table
```

## Service principal patterns

### Secret-based (cron, local headless)

```bash
az login --service-principal \
  -u "$AZURE_CLIENT_ID" \
  -p "$AZURE_CLIENT_SECRET" \
  --tenant "$AZURE_TENANT_ID"
```

### Federated / OIDC (GitHub Actions, no stored secret)

```bash
az login --service-principal \
  -u "$AZURE_CLIENT_ID" \
  --tenant "$AZURE_TENANT_ID" \
  --federated-token "$ID_TOKEN"
```

In GitHub Actions, prefer `azure/login@v2` with `client-id` / `tenant-id` /
`subscription-id` and `permissions: id-token: write`.

### Managed identity (when running on Azure compute)

```bash
az login --identity                       # system-assigned
az login --identity --username "<client-id>"   # user-assigned
```

## Decoding errors in full

| HTTP | Body hint | Real cause | Fix |
|---|---|---|---|
| 401 | `invalid_token` / `audience` | Token audience is `management.azure.com`, not `ai.azure.com` | Pass `--resource https://ai.azure.com` (or use `frest`). |
| 401 | `expired` | Token TTL elapsed | Re-`az login` / re-auth SP. |
| 403 | `AuthorizationFailed` | No data-plane role | Grant **Azure AI User**/**Developer** on the resource scope. |
| 403 | `does not have authorization to perform action 'Microsoft.CognitiveServices/...'` | Control-plane action without contributor | Add **Cognitive Services Contributor** for resource-level ops. |
| 404 | `ResourceNotFound` | Wrong project segment or resource host | Re-check `$ENDPOINT`; project is case-sensitive. |
| 400 | `Unsupported api-version` | Wrong `$AV` for the surface | See the api-version map in `endpoints.md`. |

## Sanity script

```bash
echo "sub:      $(az account show --query name -o tsv)"
echo "identity: $(az account show --query user.name -o tsv)"
echo "endpoint: $ENDPOINT"
az rest --resource https://ai.azure.com --url "$ENDPOINT/agents?api-version=$AV" \
  --query 'data | length(@)' -o tsv 2>/dev/null \
  && echo "✓ reachable" || echo "✗ see troubleshoot table"
```
