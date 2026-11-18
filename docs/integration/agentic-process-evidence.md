# Integrate Agentic Process Evidence

Agentic Process Evidence (APE) is a protocol and implementation for governing agentic processes, such as coding or client interactions. The core protocol is logging the agent's sessions, and sigining a provenance evidence before they affect real world applications. For example, logging coding sessions and sigining them wrt the commit they have generated.

This approach creates an easy provenance and audit trail, it protects the sessions (signed) and allows for Policy as Code for the agent process management, allowing the user to intervene when some evidence breaks a policy at a gate.

## Artifacts


| Artifact         | Unit                                                                                                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Process evidence | One provenance, as an in-toto attestation v1. Subject is a git commit, an artifact digest, an application version, or the session when that session is the agentic process outcome. |
| Session log      | One agent run: providers, prompts, reasoning, tool calls, responses.                                                                                                                |


A process evidence references many logs (`predicate.sessionsLogs`). A session belongs to one process. Neither artifact is an [evidence record](../glossary.md#evidence-and-trust). Keep both addressable by `uri` + `digest`, and extract events out of them.

## Rules

1. One `run_id` per process evidence. Every record from that statement and its logs shares it.
2. Match each `sessionsLogs[]` target to its `digest` before reading it. On mismatch, keep the reference and skip that timeline.
3. Do not invent OpenTelemetry ids, `descriptor_digest`, `caused_by`, `side_effect`, `delegation_chain` entries, or `authz.decision`. Absence is a gap.

4. Store session logs for all agentic sessions, these include data such as prompts, tool use, replies and thinking tokens, see [agentic session log](../../schemas/agentic-session-log/agentic-session-log.md)

5. The Agentic-process-evidence along with its session logs will be used for generating the agentic evidence.



## Statement to records


| Record      | `event_time`     | Taken from the statement                                                                                                                                |
| ----------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `run.start` | `startTimestamp` | `traceId` as a process id. Not `trace.trace_id`. No `scenario_id`.                                                                                      |
| `run.end`   | `endTimestamp`   | `result`: `COMPLETED`, `FAILED`, `CANCELLED`, `APPROVED`, `REJECTED`, `ALIGNED`, `MISALIGNED`. This is an open list, A verdict is not `authz.decision`. |



| APE field                             | Record field                                                                                                   | Rule                                                                                                                                 |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `owner`                               | `identity.principal`                                                                                           | Not `createdBy`.                                                                                                                     |
| `providers[].agent.name`              | `identity.agent` on the run records                                                                            | Only when the statement has exactly one provider that names an agent. Several providers: leave it empty. Do not pick one.            |
| session log `provider.agent.name`     | `identity.agent` on that log's records                                                                         | The session's provider, not the statement's.                                                                                         |
| `providers[]`, session log `provider` | whole [Provider](../../schemas/agentic-process-evidence/agent-identifier.md#provider) object, by digest or ref | No v0.1 fields for harness, agent id, or models. Keep every `languageModels` entry. Do not rename `inferenceProvider` or `resolved`. |
| —                                     | `delegation_chain`                                                                                             | Empty. `owner`, agent name, and `reviewers` are not a chain.                                                                         |



| APE field                   | Projection                                                                                                                                                 |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `subject[]`                 | `uri` + `digest` on `run.start`. No new record kind.                                                                                                       |
| `sessionsLogs[]`            | One ref each (`uri`, `digest`). Timeline only after rule 2.                                                                                                |
| `tools[]`                   | Name + version list on the run. Not a `tool.invocation`.                                                                                                   |
| `contextArtifacts[]`        | `input.received`: `input_ref`, and `input_digest` when `digest` is present. Not `retrieval.result` unless a timeline event is that retrieval. Keep `tags`. |
| `custom`                    | On `run.start` (`baseCommit`, `requirements`, other keys). Not a correlation field.                                                                        |
| `intents`, `processSummary` | Digest + ref on `run.end`. Not `caused_by`.                                                                                                                |
| `reviewers`                 | String list on `run.end`. Not authorization, and not proof a person saw the outcome.                                                                       |
| `predicateType`, `_type`    | Informational. `_type` must be `https://in-toto.io/Statement/v1`.                                                                                          |
| `createdAt`, `createdBy`    | On `run.end`. Not `collected_at`, not `identity.principal`.                                                                                                |


When `subject[].digest` and a log's `affectedEntities` disagree, project both. Neither becomes `verified`.

## Timeline to records

Walk `timeline[]` in source order. The overlay is `eventId`, `event`, `ts`. Every other name stays as the producer wrote it. `tool_use_id` and `tool_input` are harness fields, not part of the overlay.


| `event`              | Record                                                             | Payload                                                                                                                                                                                              |
| -------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `beforeSubmitPrompt` | `input.received`                                                   | Digest of the prompt. No raw `prompt`.                                                                                                                                                               |
| `preToolUse`         | `tool.invocation`                                                  | `tool_name`. `invocation_id` = `tool_use_id` when present, otherwise empty. `args_digest` over `tool_input` when present. No `descriptor_digest`. No `side_effect` unless the source classifies one. |
| `postToolUse`        | `tool.result` only when the event has a status or an output digest | Those fields only. Same `tool_use_id`.                                                                                                                                                               |
| `afterAgentResponse` | none                                                               | Not `agent.decision`. Leave the text in the log.                                                                                                                                                     |
| `sessionEnd`         | none                                                               | Not `run.end`. Later sessions may still belong to the process.                                                                                                                                       |
| any other value      | none                                                               | Do not coerce it into a v0.1 kind.                                                                                                                                                                   |


`session_id` in the payload is carried source data. v0.1 has no session field, and it is not `run_id`. When `conversation_id` repeats `sessionId`, do not mint a second id. `parentSessionId` is not `parent_span_id` and not `caused_by`. `path_hashes` are file fingerprints, not `descriptor_digest` or `output_digest`. Emit `agent.decision` only when a source field names the earlier event. A later `ts` does not.

Harness-emitted events use component `agent-runtime`. Use `tool:<name>` only when the tool itself emitted the record. The APE runtime tool is not `recorder-tap`.

## Example

A `preToolUse` whose log digest already matched. The recorder assigns `record_id`, `run_id`, `collected_at`, `payload_digest`, and `record_digest`. No `trace` in the source. No `tool_input`, so no `args_digest`. `delegation_chain` is empty on purpose.

```json
{
  "eventId": "evt_01EXAMPLE",
  "event": "preToolUse",
  "ts": "2026-04-08T08:51:18.441Z",
  "tool_name": "Write",
  "tool_use_id": "toolu_01EXAMPLE",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

```json
{
  "schema_version": "0.1.0",
  "kind": "tool.invocation",
  "source": { "component": "agent-runtime", "channel": "self-report" },
  "trust": "asserted",
  "event_time": "2026-04-08T08:51:18.441Z",
  "correlation": { "invocation_id": "toolu_01EXAMPLE" },
  "identity": {
    "principal": "dev@example.com",
    "agent": "cursor-agent",
    "delegation_chain": []
  },
  "payload": {
    "tool_name": "Write",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
}
```

`session_id` is not a v0.1 invocation field.