# Microsoft Foundry — doc & REST index

Official docs (Microsoft Learn) and REST references. Foundry was formerly "Azure AI
Foundry"; the service id is `microsoft-foundry` and docs now read "Microsoft
Foundry".

## Concepts & quickstarts

| Topic | URL |
|---|---|
| What is Foundry Agent Service | https://learn.microsoft.com/azure/foundry/agents/overview |
| Agents, conversations, responses (runtime) | https://learn.microsoft.com/azure/foundry/agents/concepts/runtime-components |
| Get started with the Foundry SDK | https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code |
| Deploy a hosted agent | https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent |
| Manage hosted agents | https://learn.microsoft.com/azure/foundry/agents/how-to/manage-hosted-agent |

## REST references

| API | URL |
|---|---|
| Foundry REST root | https://learn.microsoft.com/rest/api/aifoundry/ |
| Agents (project) | https://learn.microsoft.com/rest/api/aifoundry/project/agents |
| Responses / OpenAI-compatible | `$ENDPOINT/openai/v1/{responses,evals,files,vector_stores,fine_tuning/jobs,embeddings}` |
| Content Safety | https://learn.microsoft.com/azure/ai-services/content-safety/ |

## Discover the live api-version

Docs drift; confirm against the resource provider rather than trusting a constant:

```bash
az provider show --namespace Microsoft.CognitiveServices \
  --query "resourceTypes[?resourceType=='accounts'].apiVersions[0]" -o tsv
```

For data-plane surfaces, the project uses `v1` (stable) and dated previews (e.g.
`2025-11-15-preview` for hosted-agent versions). The map lives in
[foundry-config/references/endpoints.md](../../foundry-config/references/endpoints.md)
— update it in one place when a version moves.

## When docs and reality disagree

The live API is the source of truth. Probe with a harmless `GET` (e.g.
`$ENDPOINT/agents?api-version=v1`) and read the error body — Foundry's 400s name the
exact missing/renamed field (this is how the agent-core and tool schemas in these
skills were verified).
```
