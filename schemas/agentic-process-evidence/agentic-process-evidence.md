# Agentic Process Evidence

An in-toto Statement v1 about one agentic process. It references the [session logs](../agentic-session-log/agentic-session-log.md) of the sessions in that process. The **subject** is the outcome: a git commit, an application version, an artifact digest, or the session log when the process is that one session. One statement MAY reference many logs.

## Subject


| Process                                               | Subject                   |
| ----------------------------------------------------- | ------------------------- |
| Code development or review                            | git commit                |
| Version release approval                              | Application version       |
| Artifact promotion                                    | Artifact digest           |
| Single-session process (support case, standalone run) | Session log (`sessionId`) |


Use the session as subject only when there is no SDLC entity, or when that session is the accountable outcome.

## Example

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "uri": "https://github.com/example/app/commit/bf02510c8ce0b804a099797510afc19325",
      "digest": { "gitCommit": "bf02510c8ce0b804a099797510afc19325" }
    }
  ],
  "predicateType": "https://example.com/evidence/agentic-dev-process/v1",
  "predicate": {
    "providers": [
      {
        "harness": { "name": "cursor", "version": "3.5.33" },
        "agent": { "id": "spiffe://example.com/agent/helpdesk", "name": "cursor-agent", "version": "1.0" },
        "languageModels": [
          { "inferenceProvider": "anthropic/claude-opus-4-8", "resolved": "anthropic/claude-opus-4-8-20260701" },
          { "inferenceProvider": "openai/gpt-4.1", "resolved": "openai/gpt-4.1" }
        ]
      }
    ],
    "traceId": "ci-job-run-1842",
    "sessionsLogs": [
      {
        "uri": "https://example.com/logs/a1b2c3d4.json",
        "digest": { "sha256": "9f2b8c1d7a4530e6b8d0c7f1a2934ee41a" }
      }
    ],
    "tools": [{ "name": "Write", "version": "1.0" }],
    "contextArtifacts": [
      {
        "tags": ["policy"],
        "uri": "https://example.com/policies/intents-v4.md",
        "digest": { "sha256": "41c0e93b6d287fa5029b8c1d64" }
      }
    ],
    "custom": {
      "baseCommit": {
        "uri": "https://github.com/example/app/commit/aa11bb22",
        "digest": { "gitCommit": "aa11bb22" }
      },
      "requirements": [{ "issue": "https://example.com/browse/FIN-3678", "title": "Rate limit orders" }]
    },
    "result": "COMPLETED",
    "intents": ["add rate limiting"],
    "processSummary": "Added a token bucket on /api/orders.",
    "owner": "dev@example.com",
    "reviewers": ["reviewer@example.com"],
    "startTimestamp": "2026-04-08T08:51:02.114Z",
    "endTimestamp": "2026-04-08T08:55:17.242Z"
  },
  "createdAt": "2026-04-08T08:55:17.242Z",
  "createdBy": "dev-auto-reviewer"
}
```

Give a context artifact `uri` or `data`, not both. Provider fields are in `[agent-identifier.md](./agent-identifier.md)`.

## Resource descriptor

`uri` plus `digest`. in-toto allows further fields; examples here use these two. `subject[]` and `sessionsLogs[]` are arrays of this type. `custom.baseCommit` is one.


| Field    | Type      | Required | Constraints                                     | Description                    |
| -------- | --------- | -------- | ----------------------------------------------- | ------------------------------ |
| `uri`    | String    | yes      | URI                                             | Where the artifact is          |
| `digest` | DigestSet | yes      | ≥1 algorithm key; see [Digest set](#digest-set) | Identity of the bytes at `uri` |




## Tool


| Field     | Type   | Required | Constraints            | Description                                           |
| --------- | ------ | -------- | ---------------------- | ----------------------------------------------------- |
| `name`    | String | yes      | non-empty              | Name the harness reports                              |
| `version` | String | no       | non-empty when present | Version the producer reports (not necessarily SemVer) |


`predicate.tools` is a Tool array. Session-log search uses the same type ([session log](../agentic-session-log/agentic-session-log.md)).

## Context artifact

A policy, guideline, instruction, or other input. A [Resource descriptor](#resource-descriptor) plus tags and an optional inline body.


| Field    | Type         | Required    | Constraints                                                                    | Description           |
| -------- | ------------ | ----------- | ------------------------------------------------------------------------------ | --------------------- |
| `tags`   | String array | no          | SHOULD use [Context artifact tags](#context-artifact-tags); other tags allowed | Labels                |
| `uri`    | String       | conditional | URI; exactly one of `uri` or `data`                                            | Where the artifact is |
| `data`   | String       | conditional | exactly one of `uri` or `data`                                                 | Inline body           |
| `digest` | DigestSet    | no          | ≥1 key when present; SHOULD include `sha256`                                   | Identity of the bytes |


`predicate.contextArtifacts` is a ContextArtifact array.

### Context artifact tags

Other tags MAY be used.


| Value          | Meaning                                   |
| -------------- | ----------------------------------------- |
| `policy`       | Policy the process was expected to follow |
| `guideline`    | Architecture or development guideline     |
| `instructions` | Prompt, system, or agent instructions     |
| `priorLog`     | Earlier session log used as input         |




## Statement fields


| Field           | Type      | Required | Constraints                               | Description                  |
| --------------- | --------- | -------- | ----------------------------------------- | ---------------------------- |
| `_type`         | String    | yes      | exactly `https://in-toto.io/Statement/v1` | Statement type               |
| `predicateType` | String    | yes      | URI of this evidence kind                 | Filter and existence checks  |
| `createdAt`     | Timestamp | yes      | ISO 8601                                  | When the statement was built |
| `createdBy`     | String    | yes      | non-empty                                 | Who built the statement      |




## Predicate


| Field              | Type                     | Required | Constraints                                                                           | Description                              |
| ------------------ | ------------------------ | -------- | ------------------------------------------------------------------------------------- | ---------------------------------------- |
| `providers`        | Provider array           | yes      | ≥1; see [Provider](./agent-identifier.md)                                             | Stacks used in the process               |
| `traceId`          | String                   | no       | non-empty when present                                                                | Process id, such as a CI job URI         |
| `sessionsLogs`     | ResourceDescriptor array | no       | 0..*; each `digest` SHOULD include `sha256`; omit when the subject is the session log | Links to the logs                        |
| `tools`            | Tool array               | no       | 0..*; see [Tool](#tool)                                                               | Tools used                               |
| `contextArtifacts` | ContextArtifact array    | no       | 0..*; see [Context artifact](#context-artifact)                                       | Policies, instructions, and other inputs |
| `custom`           | Object                   | no       | process-specific keys                                                                 | Data for this kind of process            |
| `result`           | String                   | yes      | [Process result](#process-result)                                                     | How the process ended                    |
| `intents`          | String array             | no       | 0..*                                                                                  | Short intent strings                     |
| `processSummary`   | String                   | no       |                                                                                       | Summary of the process                   |
| `owner`            | String                   | yes      | login or email                                                                        | Accountable person                       |
| `reviewers`        | String array             | no       | 0..*; each a login or email                                                           | People who oversaw the process           |
| `startTimestamp`   | Timestamp                | yes      | ISO 8601                                                                              | Process start                            |
| `endTimestamp`     | Timestamp                | yes      | ISO 8601                                                                              | Process end                              |


Kept for the release lifetime. Used for audit, policy checks, and review. Retention of the logs is on the [session log](../agentic-session-log/agentic-session-log.md).

## Process result

`predicate.result` is the outcome of the process, not of one session. That is an open list, few examples are listed below:


| Value        | Meaning                     |
| ------------ | --------------------------- |
| `COMPLETED`  | Finished successfully       |
| `FAILED`     | Ended unsuccessfully        |
| `CANCELLED`  | Stopped before completion   |
| `APPROVED`   | Review approved the subject |
| `REJECTED`   | Review rejected the subject |
| `ALIGNED`    | Alignment check passed      |
| `MISALIGNED` | Alignment check failed      |




## Custom data

`custom` MAY hold any process-specific object. Development evidence uses:


| Field                  | Type               | Required | Constraints                         | Description  |
| ---------------------- | ------------------ | -------- | ----------------------------------- | ------------ |
| `baseCommit`           | ResourceDescriptor | no       | `digest` SHOULD include `gitCommit` | Base commit  |
| `requirements`         | Object array       | no       | 0..*                                | Linked tasks |
| `requirements[].issue` | String             | yes      | URI                                 | Task URL     |
| `requirements[].title` | String             | no       |                                     | Task title   |


