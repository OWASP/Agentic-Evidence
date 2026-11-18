# Agentic session log

The stored log of a single agent run. 

Agnetic process evidence statements point at the session logs by **uri + digest**.

May be queried by the subject that run produced (commit, PR, version), and by tools, agent, and suspected policy issues. 

Some products must keep logs at least 6 months (EU AI Act, Article 19).

## Example

```json
{
  "sessionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "parentSessionId": "4o7g54cd-8957-7503-45ga-495867457986",
  "affectedEntities": [{ "gitCommit": "bf02510c8ce0b804a099797510af" }],
  "provider": {
    "harness": { "name": "cursor", "version": "3.5.33" },
    "agent": { "id": "spiffe://example.com/agent/helpdesk", "name": "cursor-agent", "version": "1.0" },
    "languageModels": [
      { "inferenceProvider": "anthropic/claude-opus-4-8", "resolved": "anthropic/claude-opus-4-8-20260701" },
      { "inferenceProvider": "openai/gpt-4.1", "resolved": "openai/gpt-4.1" }
    ]
  },
  "timeline": [
    {
      "eventId": "evt_01",
      "event": "beforeSubmitPrompt",
      "ts": "2026-04-08T08:51:02.114Z",
      "hook_event_name": "beforeSubmitPrompt",
      "prompt": "Implement rate limiting on /api/orders"
    },
    {
      "eventId": "evt_02",
      "event": "preToolUse",
      "ts": "2026-04-08T08:51:18.441Z",
      "hook_event_name": "preToolUse",
      "tool_name": "Write",
      "tool_use_id": "toolu_01ABC",
      "tool_input": { "path": "src/orders/rate_limit.py" },
      "path_hashes": { "src/orders/rate_limit.py": null }
    },
    {
      "eventId": "evt_03",
      "event": "postToolUse",
      "ts": "2026-04-08T08:51:19.102Z",
      "hook_event_name": "postToolUse",
      "tool_name": "Write",
      "tool_use_id": "toolu_01ABC",
      "path_hashes": { "src/orders/rate_limit.py": "e3b0c44298fc1c149afbf4c8996fb924" }
    },
    {
      "eventId": "evt_04",
      "event": "afterAgentResponse",
      "ts": "2026-04-08T08:52:01.880Z",
      "text": "Added token-bucket rate limiting on /api/orders."
    },
    {
      "eventId": "evt_05",
      "event": "sessionEnd",
      "ts": "2026-04-08T08:52:05.010Z"
    }
  ]
}
```

The overlay is `eventId`, `event`, `ts`. Other properties keep the producer’s names (`hook_event_name`, `tool_name`, `tool_use_id`, `path_hashes`). `path_hashes` is optional. `sessionEnd`, or the harness equivalent, flushes the log. `languageModels` lists every model selected in the session; see [Language model](../agentic-process-evidence/agent-identifier.md#language-model).

## Log object


| Field              | Type                | Required | Constraints                                                     | Description                                              |
| ------------------ | ------------------- | -------- | --------------------------------------------------------------- | -------------------------------------------------------- |
| `sessionId`        | String              | yes      | non-empty                                                       | Session id. Process evidence `sessionsLogs` points here. |
| `parentSessionId`  | String              | no       | non-empty when present                                          | Parent session                                           |
| `affectedEntities` | Object array        | no       | subject keys, such as `gitCommit`                               | Entities this run produced or handled                    |
| `provider`         | Provider            | yes      | see [Provider](../agentic-process-evidence/agent-identifier.md) | Harness, agent, and the models used                      |
| `timeline`         | TimelineEvent array | yes      | ≥1; see [Timeline event](#timeline-event)                       | Ordered hook events                                      |




## Timeline event

Harness event plus the overlay. Extra producer properties MAY appear and MUST NOT be renamed. Do not copy `sessionId` onto the event.


| Field     | Type      | Required | Constraints                                               | Description        |
| --------- | --------- | -------- | --------------------------------------------------------- | ------------------ |
| `eventId` | String    | yes      | unique within the log                                     | Dedup and citation |
| `event`   | String    | yes      | SHOULD be a [kind](#timeline-event-kind) when one applies | Event kind         |
| `ts`      | Timestamp | yes      | ISO 8601                                                  | Event time         |




## Timeline event kind

Use one of these when it fits. Other values MAY be used for harness events with no equivalent. `hook_event_name` MAY repeat the native name.


| Value                | Meaning                      |
| -------------------- | ---------------------------- |
| `beforeSubmitPrompt` | Prompt about to be submitted |
| `preToolUse`         | Tool invocation about to run |
| `postToolUse`        | Tool invocation finished     |
| `afterAgentResponse` | Agent produced a response    |
| `sessionEnd`         | Session finished; flush      |




## Searchable attributes


| Property          | Type       | Required | Constraints                                                                          | Description             |
| ----------------- | ---------- | -------- | ------------------------------------------------------------------------------------ | ----------------------- |
| `tools`           | Tool array | no       | 0..*; see [Tool](../agentic-process-evidence/agentic-process-evidence.md#tool)       | Tools used              |
| `agent`           | Agent      | no       | `provider.agent`; see [Agent](../agentic-process-evidence/agent-identifier.md#agent) | Agent metadata          |
| `subject`         | Object     | no       | subject keys                                                                         | Commit or other subject |
| `sessionId`       | String     | yes      | same as the log `sessionId`                                                          | Session id              |
| `parentSessionId` | String     | no       |                                                                                      | Parent session          |


