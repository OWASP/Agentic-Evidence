# Example records, schema v0.1

Hand-written example records for every record kind in [ARCHITECTURE §3.2](../../../../ARCHITECTURE.md#32-record-kinds-v01), one example per file.
They are the fixtures the M1 schema has to validate (HANDOFF M1: "`make schema-check` validates hand-written example records for every kind in ARCHITECTURE §3.2").
Tracked in #27.

**Status:** draft, written before the schema exists.
Field names follow [ARCHITECTURE §3.1](../../../../ARCHITECTURE.md#31-evidencerecord) and §3.2 as written.
Where §3 leaves a choice open, the example makes one, marks it in the table below, and lists it under [Open questions](#open-questions).
Once the schema lands, these files either validate or are corrected with it.

## What the examples show

All examples belong to one synthetic run, `run_ex_0001`.
A helpdesk agent acting for `user:alice@example.com` reads a knowledge-base article, then calls `files.write` once (`inv_ex_0001`) to archive a ticket.
The records cross-reference each other by `record_id`, `invocation_id`, `caused_by` and `descriptor_digest`, so the set reads as one run rather than isolated fragments.

The examples illustrate record shapes and trust assignment.
They are not a scenario: they have no `expected.yaml`, assert no claim status, and make no statement about what an investigator can conclude from them.

## Coverage

Trust follows the channel, as [ARCHITECTURE §4](../../../../ARCHITECTURE.md#4-trust-model) assigns it: `self-report` gives `asserted`, `interception` from `recorder-tap` gives `observed`, `reference-check` gives `verified`.

| Kind | Component | Channel | Trust | File | Note |
|------|-----------|---------|-------|------|------|
| `run.start` | `agent-runtime` | `self-report` | `asserted` | [run.start--agent-runtime--asserted.json](run.start--agent-runtime--asserted.json) | |
| `run.end` | `agent-runtime` | `self-report` | `asserted` | [run.end--agent-runtime--asserted.json](run.end--agent-runtime--asserted.json) | |
| `input.received` | `agent-runtime` | `self-report` | `asserted` | [input.received--agent-runtime--asserted.json](input.received--agent-runtime--asserted.json) | |
| `retrieval.result` | `retriever` | `self-report` | `asserted` | [retrieval.result--retriever--asserted.json](retrieval.result--retriever--asserted.json) | |
| `retrieval.result` | `recorder-tap` | `interception` | `observed` | [retrieval.result--recorder-tap--observed.json](retrieval.result--recorder-tap--observed.json) | |
| `tool.descriptor.observed` | `agent-runtime` | `self-report` | `asserted` | [tool.descriptor.observed--agent-runtime--asserted.json](tool.descriptor.observed--agent-runtime--asserted.json) | `observed_via: invocation` |
| `tool.descriptor.observed` | `recorder-tap` | `interception` | `observed` | [tool.descriptor.observed--recorder-tap--observed.json](tool.descriptor.observed--recorder-tap--observed.json) | `observed_via: list_tools` |
| `tool.descriptor.observed` | `recorder-tap` | `reference-check` | `verified` | [tool.descriptor.observed--recorder-tap--verified.json](tool.descriptor.observed--recorder-tap--verified.json) | §4 (a): digest matches the pin. Provisional, Q2 and Q3 |
| `agent.decision` | `agent-runtime` | `self-report` | `asserted` | [agent.decision--agent-runtime--asserted.json](agent.decision--agent-runtime--asserted.json) | Q4 |
| `authz.decision` | `pdp` | `self-report` | `asserted` | [authz.decision--pdp--asserted.json](authz.decision--pdp--asserted.json) | |
| `authz.decision` | `gateway` | `self-report` | `asserted` | [authz.decision--gateway--asserted.json](authz.decision--gateway--asserted.json) | A gateway's own log is a self-report |
| `authz.decision` | `recorder-tap` | `reference-check` | `verified` | [authz.decision--recorder-tap--verified.json](authz.decision--recorder-tap--verified.json) | §4 (b): PDP and gateway agree. Provisional, Q2 and Q3 |
| `tool.invocation` | `agent-runtime` | `self-report` | `asserted` | [tool.invocation--agent-runtime--asserted.json](tool.invocation--agent-runtime--asserted.json) | Q4 |
| `tool.invocation` | `recorder-tap` | `interception` | `observed` | [tool.invocation--recorder-tap--observed.json](tool.invocation--recorder-tap--observed.json) | Q4 |
| `tool.result` | `tool:files.write` | `self-report` | `asserted` | [tool.result--tool-files.write--asserted.json](tool.result--tool-files.write--asserted.json) | Q4 |
| `tool.result` | `recorder-tap` | `interception` | `observed` | [tool.result--recorder-tap--observed.json](tool.result--recorder-tap--observed.json) | Q4 |
| `data.flow` | `recorder-tap` | `interception` | `observed` | [data.flow--recorder-tap--observed.json](data.flow--recorder-tap--observed.json) | |
| `reference.pin` | `scenario-fixture` | `self-report` | `asserted` | [reference.pin--scenario-fixture--asserted.json](reference.pin--scenario-fixture--asserted.json) | Provisional, Q1 |

File names are `<kind>--<component>--<trust>.json`, with `:` in a component name replaced by `-`.

### Combinations deliberately absent

- **`self-report` with `observed` or `verified`.** §4 assigns trust from the channel, so a self-report is `asserted` whatever it claims.
- **`interception` from any component other than `recorder-tap`.** §4 grants `observed` only to a recorder-controlled tap.
- **`interception` for `run.start`, `run.end`, `input.received` and `agent.decision`.** §3.2 lists only `agent-runtime` as their emitter and defines no tap point for them.
- **`authz.decision` from `pdp` or `gateway` at `observed`.** Neither is a recorder tap. An authorization decision reaches `verified` only through §4 (b), shown above.
- **`verified` for kinds §4 gives no reference for.** §4 defines `verified` through a `reference.pin` (descriptors) or two independent sources agreeing on an `invocation_id` and decision (authorization). The examples show those two cases only.
- **Gaps.** "Unknown" is a Gap, not a record (§4, EV-1), so it has no example here.

## Digests

`payload_digest` and `record_digest` are `sha256:` over the canonical form of the payload and of the record without `record_digest`: sorted keys, compact separators (`,` and `:`), UTF-8 (CONSTRAINTS DT-3).
That is a stand-in for the M1 canonical serializer.
When the serializer lands, the digests are recomputed with it, and any difference is the serializer's to explain.

The content digests stand for synthetic inputs:

| Field | Input |
|-------|-------|
| `input_digest` | The string `Please archive ticket T-1001.` |
| `content_digest` (doc-7) | The string `Synthetic knowledge-base article doc-7: tickets older than 30 days are archived.` |
| `descriptor_digest` | The canonical form of the `files.write` descriptor `{name, description, input_schema}` |
| `args_digest` | The canonical form of `{path: "/archive/T-1001.txt", content_digest: sha256("ticket T-1001 archived")}` |
| `output_digest` | The canonical form of `{status: "written", path: "/archive/T-1001.txt"}` |
| `policy_digest` | The string `permit agent:helpdesk-bot files.write on /archive/*` |

Raw content stays out of the records, as DA-3 requires.

## Open questions

These come from writing the examples against §3 as it stands, and are raised in #27.

1. **Q1. Emitter of `reference.pin`.** §3.2 names "scenario fixture" as its emitter, but `source.component` in §3.1 has no such value.
   The example uses `scenario-fixture` on `self-report`, so the pin is `asserted`, and lets `pin_source` say where it came from.
2. **Q2. Emitter of a `verified` record.** §4 has `verified` arrive on `reference-check`, but no component in §3.1 obviously performs the check.
   The examples use `recorder-tap`.
3. **Q3. Where a verified record lists what it checked.** §4 says "the verifying record lists what it verified against" but names no field.
   The examples use `payload.verified_against`, a list of `record_id`s.
4. **Q4. Fields named in both places.** §3.2 lists `invocation_id` (and `caused_by` for `agent.decision`) as payload fields, and §3.1 also carries them under `correlation`.
   The examples carry both with the same value. If the schema keeps one place, the other is dropped from these files.

## Not covered

- Record kinds proposed after v0.1 (`tool.dispatch`, `effect.observation` in #26, grant and revocation records in #21).
- `taxonomy_refs`, which §3.1 marks optional and informational.
- Malformed records. Those belong in the schema's negative tests, once the schema exists.
