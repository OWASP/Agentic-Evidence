# Agent identifier

**Provider** and its nested types **Harness**, **Agent**, and **LanguageModel**: the runtime stack on a log or a process-evidence statement. Traceability runs **harness → agent → language models**.

**Required** below: `yes` = present and non-empty; `no` = optional. **MUST** / **SHOULD** / **MAY** follow [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## Provider

```json
{
  "harness": { "name": "cursor", "version": "3.5.33" },
  "agent": { "id": "spiffe://example.com/agent/helpdesk", "name": "cursor-agent", "version": "1.0" },
  "languageModels": [
    { "inferenceProvider": "anthropic/claude-opus-4-8", "resolved": "anthropic/claude-opus-4-8-20260701" },
    { "inferenceProvider": "openai/gpt-4.1", "resolved": "openai/gpt-4.1" }
  ]
}
```

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `harness` | Harness | yes | see [Harness](#harness) | Product that hosts the session |
| `agent` | Agent | no | see [Agent](#agent) | Agent running in the harness |
| `languageModels` | LanguageModel array | no | 0..*; one entry per model selected, including a mid-session IDE switch; see [Language model](#language-model) | Every model that participated |

`predicate.providers` on [process evidence](./agentic-process-evidence.md) is one Provider per distinct stack. A [session log](../agentic-session-log/agentic-session-log.md) carries one `provider`. Alignment evidence is not in this copy.

## Harness

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `name` | String | yes | non-empty | Product name (IDE, CI runner, review bot) |
| `version` | String | yes | non-empty | Version the producer emits (not necessarily SemVer) |

## Agent

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `id` | String | no | non-empty when present | Stable id, such as a SPIFFE ID |
| `name` | String | no | non-empty when present | Agent name |
| `version` | String | no | non-empty when present | Version the producer emits (not necessarily SemVer) |

## Language model

One object in `languageModels`. A session holds every model selected in it. An IDE model switch adds another object.

`inferenceProvider` and `resolved` name this object only: the model requested, the model that ran, or both. A second model is a second object.

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `inferenceProvider` | String | no | non-empty when present | Model requested for this entry |
| `resolved` | String | no | non-empty when present | Model that ran for this entry |
