# Connections — per-target bodies & roles

Create via PUT on the project connections path:

```
https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/projects/$PROJECT/connections/<name>?api-version=2025-06-01
```

Prefer `authType: AAD` (project managed identity) over keys everywhere possible.

## Azure AI Search

```json
{
  "properties": {
    "category": "CognitiveSearch",
    "target": "https://<search>.search.windows.net",
    "authType": "AAD",
    "metadata": { "ApiType": "Azure" }
  }
}
```

Role to grant the project identity on the Search service:
**Search Index Data Reader** (query) / **Search Index Data Contributor** (write).

```bash
SCOPE=$(az resource show -g "$RG" -n "<search>" --resource-type Microsoft.Search/searchServices --query id -o tsv)
az role assignment create --assignee "<project-principal-id>" --role "Search Index Data Reader" --scope "$SCOPE"
```

## Azure Blob Storage

```json
{
  "properties": {
    "category": "AzureBlob",
    "target": "https://<account>.blob.core.windows.net/<container>",
    "authType": "AAD"
  }
}
```

Role: **Storage Blob Data Contributor** on the account/container.

## Key Vault

```json
{
  "properties": {
    "category": "AzureKeyVault",
    "target": "https://<vault>.vault.azure.net",
    "authType": "AAD"
  }
}
```

Role: **Key Vault Secrets User**.

## Other Azure AI services (key-based, when AAD unavailable)

```json
{
  "properties": {
    "category": "AIServices",
    "target": "https://<svc>.cognitiveservices.azure.com",
    "authType": "ApiKey",
    "credentials": { "key": "<key-or-keyvault-ref>" }
  }
}
```

Store the key in Key Vault and reference it rather than inlining.

## Find the project principal id

```bash
az rest --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$RES/projects/$PROJECT?api-version=2025-06-01" \
  --query 'identity.principalId' -o tsv
```
