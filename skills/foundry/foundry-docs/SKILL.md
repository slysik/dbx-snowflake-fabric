---
name: foundry-docs
description: "Authoritative Microsoft Foundry documentation index — use as a fallback when another foundry-* skill doesn't cover a topic, to look up an unfamiliar Foundry feature, REST path, or api-version. Use when the user asks about a Foundry capability not covered elsewhere, or wants the official docs/REST reference."
license: MIT
metadata:
  author: slysik
  version: "0.1.0"
  updated: "2026-06-26"
---

# Microsoft Foundry — Docs Index (fallback)

When a task falls outside the other `foundry-*` skills, start here, then drop back
to `az rest` against the project endpoint
([foundry-config](../foundry-config/SKILL.md)). House rule still holds: **CLI/REST,
no MCP**.

## First, the skill that fits

| Topic | Skill |
|---|---|
| Auth, endpoint, api-version | `foundry-config` |
| Create/version agents | `foundry-agents-authoring` |
| Run agents (Responses, threads) | `foundry-agents-runtime` |
| Tools (code, file_search, function) | `foundry-agent-tools` |
| Deploy models | `foundry-model-catalog` |
| Connections (Search/Storage/KV) | `foundry-connections` |
| RAG / vector store / Search | `foundry-rag-search` |
| Evals & judges | `foundry-evaluation` |
| Content filters, shields, groundedness | `foundry-content-safety` |
| Tracing & monitoring | `foundry-observability` |
| Fine-tuning | `foundry-fine-tuning` |
| Provision resource/project | `foundry-infra-azd` |

## Otherwise, the docs

| Need | Read |
|---|---|
| Curated doc + REST reference links (agents, responses, models, evals, safety, REST root), how to discover the live api-version | `references/index.md` |
