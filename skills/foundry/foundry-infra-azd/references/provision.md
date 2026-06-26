# Provisioning — azd, Bicep, Terraform, teardown

## azd up

Layout:

```
infra/
  main.bicep          # account + project + deployment + role assignment
  main.parameters.json
azure.yaml            # azd metadata
```

```bash
azd init
azd up                # provisions everything, prints the project endpoint
azd down --purge      # teardown (purge soft-deleted Cognitive resources)
```

`azure.yaml` minimal:

```yaml
name: foundry-stack
infra:
  provider: bicep
  path: infra
```

## Bicep module (account + project + deployment)

```bicep
param location string = resourceGroup().location
param resourceName string
param projectName string

resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: resourceName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: { customSubDomainName: resourceName, publicNetworkAccess: 'Enabled' }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: account
  name: projectName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {}
}

resource gpt 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: account
  name: 'gpt-4.1'
  sku: { name: 'GlobalStandard', capacity: 50 }
  properties: { model: { format: 'OpenAI', name: 'gpt-4.1', version: '2025-04-14' } }
}

output projectEndpoint string = 'https://${resourceName}.services.ai.azure.com/api/projects/${projectName}'
```

Grant a caller the data role (so they can run agents):

```bicep
resource role 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: account
  name: guid(account.id, principalId, 'aiuser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions','53ca6127-db72-4b80-b1b0-d745d6d5456d') // Azure AI User
    principalId: principalId
  }
}
```

## Terraform variant

Use `azurerm_cognitive_account` (kind `AIServices`) +
`azurerm_cognitive_deployment`, plus an `azapi_resource` for the project sub-resource
(`Microsoft.CognitiveServices/accounts/projects@2025-06-01`) until a first-class
resource ships. Output the same endpoint string.

## Teardown

```bash
az cognitiveservices account delete -n "$RES" -g "$RG"
az cognitiveservices account purge -n "$RES" -g "$RG" -l "$LOC"   # purge soft-delete
az group delete -n "$RG" --yes
```
