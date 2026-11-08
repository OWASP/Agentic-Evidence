# ARCHITECTURE.md

Status: **Proposed (v0.1 target)**. Nothing here is implemented until `HANDOFF.md` says so. Decisions referenced as ADR-NNNN live in `DECISIONS.md`; constraints as XX-N live in `CONSTRAINTS.md`.

---

## 1. Purpose in one paragraph

A scripted agent runs a deterministic scenario. Every security-relevant step emits an **evidence record** (validated, trust-labelled, stored append-only) and an OpenTelemetry span (for trace correlation). The analyzer builds an **execution graph** from the records, runs **gap rules** that flag missing or insufficient evidence, and evaluates **claims** ("tool X was invoked under authorization Y", "action Z was influenced by retrieved document D") to one of four statuses. The result is exported as a deterministic, hash-manifested **evidence bundle** and shown in an investigation UI. The scenario's `expected.yaml` is the oracle that tests compare against.

## 2. Component view

```mermaid
flowchart LR
  subgraph Scenario["Scenario (deterministic)"]
    SY[scenario.yaml + fixtures] --> SIM[Stub agent<br/>sim/]
    SIM --> MT[Mock tools]
    SIM --> MR[Mock retriever]
    SIM --> PDP[Mock policy<br/>decision point]
  end

  SIM -- emit --> REC
  MT -- emit --> REC
  MR -- emit --> REC
  PDP -- emit --> REC
  TAP[Recorder taps<br/>(interception points)] -- observe --> REC

  SIM -. spans .-> OTEL[OTel SDK<br/>telemetry/]
  OTEL -. trace/span ids .-> REC

  REC[Recorder<br/>validate · trust · limits] --> ST[(SQLite<br/>append-only)]
  ST --> COR[Correlator<br/>graph]
  COR --> AN[Analyzer<br/>gap rules · claims]
  AN --> ST
  ST --> BX[Bundle export/verify]
  ST --> API[FastAPI read-only<br/>127.0.0.1]
  API --> UI[Streamlit UI]
  OTEL -. optional OTLP .-> COL[Local OTel Collector<br/>compose only]
```

| Component | Responsibility | Must not |
|-----------|---------------|----------|
| `clock`, `ids` | Only sources of time and identifiers. `FixedStepClock(start, step)`; IDs derived as `uuid5(namespace, f"{run_seed}:{counter}")`. | Read system time or OS randomness. |
| `sim/` | Execute scenario steps verbatim. The stub agent has no reasoning; its "decisions" are scripted. | Call a model, the network, or the filesystem outside `scenarios/`. |
| `telemetry/` | Configure OTel `TracerProvider` with deterministic ID generator; attach `run_id` as resource attribute; bridge span context into records. | Be the evidence store (ADR-0002). |
| `recorder/` | Validate against schema, enforce size limits, assign `trust` from the emitting channel, stamp `collected_at`, compute `record_digest`, append. | Modify a record's payload after receipt; upgrade trust. |
| `store/` | SQLite, single `records` table, insert-only (no UPDATE/DELETE via the store API); tables for `gaps`, `claims`, `runs`. | Expose mutation of records. |
| `correlate/` | Build graph: nodes = records; edges = `parent_span`, `invocation_id` join, `caused_by`, `descriptor_digest` join, identity chain. Pure. | Infer edges from timing or proximity. |
| `analyze/` | Run gap rules; evaluate claims from `expected.yaml` + built-in claims. Pure. | Emit anything except Gap and Claim objects. |
| `bundle/` | Deterministic zip export; `verify` recomputes digests and validates schema. | Describe the output as signed. |
| `api/` | Read-only JSON over the store. `POST /runs` only in dev mode. | Bind to non-loopback by default. |
| `ui/` | Timeline, event detail, graph, gaps, claims. Calls API only. | Render payloads as HTML/Markdown; access SQLite directly. |

## 3. Data model

All objects are defined in `schemas/evidence/v0.1/*.schema.json` (canonical, ADR-0003) and mirrored by pydantic models.

### 3.1 EvidenceRecord

```jsonc
{
  "schema_version": "0.1.0",
  "record_id": "rec_…",            // from ids.py
  "run_id": "run_…",
  "kind": "tool.invocation",        // enum, see 3.2
  "source": {                       // who produced the claim
    "component": "agent-runtime",   // agent-runtime | tool:<name> | retriever | pdp | gateway | recorder-tap
    "channel": "self-report"        // self-report | interception | reference-check
  },
  "trust": "asserted",              // observed | asserted | verified  (assigned by recorder, §4)
  "event_time": "2026-01-01T00:00:03Z",     // component-reported (asserted)
  "collected_at": "2026-01-01T00:00:03.001Z",// recorder clock
  "trace": { "trace_id": "…", "span_id": "…", "parent_span_id": "…" },
  "correlation": {
    "invocation_id": "inv_…",       // joins invocation ↔ authz ↔ result
    "caused_by": ["rec_…"],         // explicit causal links, as asserted by the emitter
    "descriptor_digest": "sha256:…"
  },
  "identity": {
    "principal": "user:alice@example.com",
    "agent": "agent:helpdesk-bot",
    "delegation_chain": ["user:alice@example.com", "agent:helpdesk-bot"]
  },
  "payload": { /* kind-specific, digests not raw content by default (DA-3) */ },
  "payload_digest": "sha256:…",
  "record_digest": "sha256:…",       // over canonical serialization excluding this field
  "taxonomy_refs": ["OWASP-ASI:…"]   // optional, informational only
}
```

### 3.2 Record kinds (v0.1)

| kind | Emitted by | Key payload fields |
|------|-----------|-------------------|
| `run.start` / `run.end` | agent-runtime | scenario_id, variant, seed, status |
| `input.received` | agent-runtime | input_digest, input_ref |
| `retrieval.result` | retriever / recorder-tap | doc_id, source_uri, content_digest |
| `tool.descriptor.observed` | recorder-tap / agent-runtime | tool_name, descriptor_digest, descriptor_ref, observed_via (`list_tools` / `invocation`) |
| `agent.decision` | agent-runtime | chosen_action, rationale_ref (scripted), caused_by |
| `authz.decision` | pdp / gateway | invocation_id, decision (allow/deny), policy_id, policy_digest, subject |
| `tool.invocation` | agent-runtime / recorder-tap | invocation_id, tool_name, descriptor_digest, args_digest, side_effect (`none` / `internal` / `external`) |
| `tool.result` | tool / recorder-tap | invocation_id, status, output_digest |
| `data.flow` | recorder-tap | from_ref, to_ref, classification |
| `reference.pin` | scenario fixture | subject (e.g. tool descriptor), expected_digest, pin_source |

### 3.3 Gap

```jsonc
{ "gap_id": "gap_…", "run_id": "run_…", "rule_id": "G-AUTHZ-001",
  "subject_record_ids": ["rec_…"],
  "missing": "authz.decision with matching invocation_id",
  "blocks_conclusion": "invocation was authorized",
  "severity": "high" }            // high = blocks a security conclusion; low = degrades it
```

### 3.4 Claim

```jsonc
{ "claim_id": "C-S2-01", "run_id": "run_…",
  "statement": "tool.invocation email.send was influenced by retrieval doc-7",
  "status": "insufficient_evidence",  // supported | supported_by_assertion_only | contradicted | insufficient_evidence
  "supporting": ["rec_…"], "contradicting": [], "gaps": ["gap_…"],
  "evaluator": "influence_v1" }
```

## 4. Trust model

Trust is assigned **by the recorder from the channel a record arrived on**, never by the emitter's say-so.

| Level | Meaning | How a record gets it |
|-------|---------|---------------------|
| `asserted` | A component's statement about itself or its view of the world. | Default for `channel: self-report`. Agent runtime logs, tool self-reports, PDP logs. |
| `observed` | The recorder itself saw the bytes at an interception point it controls (e.g. computed the digest of a descriptor as it passed through a tap). | `channel: interception` from a `recorder-tap`. Only as trustworthy as the recorder and the tap placement — say so in the UI. |
| `verified` | A record checked against an **independent** reference. | `channel: reference-check`: (a) digest matches a `reference.pin` whose source is outside the agent's control, or (b) two independent sources (e.g. PDP and gateway tap) agree on the same `invocation_id` + decision. The verifying record lists what it verified against. |
| *(unknown)* | Required evidence is absent. | Represented as a `Gap`, not a record (EV-1). |

Claim status derivation:
- `supported` — all required elements present, at least one at `observed` or `verified`, no contradiction.
- `supported_by_assertion_only` — all required elements present, all `asserted`.
- `contradicted` — a required element exists that conflicts (e.g. invocation digest ≠ pinned digest; authz `deny` followed by invocation).
- `insufficient_evidence` — at least one required element missing (a blocking Gap exists).

## 5. Correlation

Edges are created only from explicit fields — never from time proximity (EV-1; AGENTS.md principle 6, correlation is not causation):

1. `trace.parent_span_id` → parent record (trace tree).
2. `correlation.invocation_id` → joins `authz.decision`, `tool.invocation`, `tool.result`.
3. `correlation.caused_by` → causal edge, carries the trust of the asserting record.
4. `correlation.descriptor_digest` → joins invocation to `tool.descriptor.observed` and `reference.pin`.
5. `identity.delegation_chain` → identity path for the action.

Ordering: within a run, order by `collected_at` (recorder clock) by default; the UI can toggle to `event_time` and marks any inversion between the two.

## 6. Gap rules (v0.1)

| Rule | Fires when | Blocks conclusion |
|------|-----------|-------------------|
| G-AUTHZ-001 | `tool.invocation` with no `authz.decision` sharing `invocation_id` | "invocation was authorized" |
| G-AUTHZ-002 | `authz.decision` exists but `collected_at` is after the invocation | "authorization preceded action" |
| G-DESC-001 | `tool.invocation` without `descriptor_digest` | "which descriptor was used" |
| G-DESC-002 | invocation `descriptor_digest` not matched by any `tool.descriptor.observed` in run | "descriptor in use was the one listed" |
| G-DESC-003 | No `reference.pin` for a tool that was invoked | "descriptor is the expected version" |
| G-INFL-001 | `tool.invocation` with `side_effect: external` after ≥1 `retrieval.result` in the run, and no `caused_by` path linking them either way | "action was / was not influenced by retrieved content" |
| G-ID-001 | `tool.invocation` with empty `delegation_chain` | "on whose behalf" |
| G-TRACE-001 | `parent_span_id` refers to a span with no record | "complete execution path" |
| G-OUT-001 | `tool.invocation` with no `tool.result` | "outcome of action" |
| G-TIME-001 | `|event_time − collected_at|` exceeds tolerance (default 5s) | ordering by event_time |

## 7. Scenarios (v0.1)

Each scenario has **variants that change the evidence emitted, not the agent behaviour**. That's the core teaching device: same execution, different conclusions.

### S1 — Benign execution (`s1-benign`)
User asks the agent to summarise ticket T-100. Agent retrieves KB doc, calls `ticket.read` (side_effect none), PDP allows, returns summary.
- `full`: zero gaps; all built-in claims `supported` or `supported_by_assertion_only`.
- `runtime-only`: only agent-runtime self-reports → every claim `supported_by_assertion_only`. Demonstrates that a clean log is not evidence of a clean run.

### S2 — Retrieval poisoning (`s2-retrieval-poisoning`)
Retrieved doc `doc-7` (synthetic) contains an instruction to email the ticket to `attacker@example.invalid`. The scripted agent calls `email.send` (side_effect external). PDP policy permits `email.send`.
- `with-influence-link`: runtime emits `agent.decision` with `caused_by: [retrieval doc-7]` → C-S2-01 "email.send influenced by doc-7" = `supported_by_assertion_only`.
- `no-influence-link`: identical run, no `caused_by` → G-INFL-001 fires, C-S2-01 = `insufficient_evidence`. Temporal order alone is not accepted.
- `authz-missing`: PDP record absent → G-AUTHZ-001; C-S2-02 "email.send was authorized" = `insufficient_evidence`.
Expected non-claim: the project does **not** claim the injection was "detected" in any variant.

### S3 — Tool descriptor modification (`s3-descriptor-modification`)
`files.search` descriptor listed at t0 with digest A; before invocation it changes (description adds an exfiltration instruction) to digest B.
- `tapped-both`: recorder tap observes descriptor at list and at invocation → digest mismatch observed; C-S3-01 "descriptor used = descriptor listed" = `contradicted`.
- `pinned`: plus `reference.pin` with digest A from an out-of-band manifest → invocation record `verified`-contradicted against pin.
- `name-only`: invocation records `tool_name` only → G-DESC-001; C-S3-01 = `insufficient_evidence`. Shows the common real-world log shape can't answer the question.

Taxonomy mapping is informational via `taxonomy_refs` (S3 relates to agentic supply-chain risk).

## 8. Evidence bundle

```
bundle-<run_id>.zip
├── manifest.json        # schema_version, run_id, scenario, variant, seed, tool versions, file list
├── records.jsonl        # canonical JSON, one record per line, ordered by collected_at then record_id
├── gaps.json
├── claims.json
├── expected.json        # copy of oracle for this variant (for comparison)
└── SHA256SUMS           # over all files above
```
Deterministic zip (sorted entries, fixed mtime 1980-01-01, no extra attrs). `ae verify` recomputes digests, re-validates schemas, re-runs analysis, and reports any divergence. The manifest states `integrity: "sha256-manifest"` — not signed (EV-7).

## 9. Threat model of the tool itself (summary)

| Threat | Mitigation |
|--------|-----------|
| Malicious record content (XSS, markdown/prompt injection) in UI | Escaped-text rendering only (SE-2); never fed to LLM/interpreter (SE-3) |
| Oversized / malformed records (DoS) | Size and count limits, schema validation, fail closed (SE-1) |
| Malicious bundle import (zip slip, zip bomb, symlink) | SE-5 checks before extraction |
| Record tampering in local store | Insert-only API + per-record digest; acknowledged: local SQLite is not tamper-proof |
| Exposed API | Loopback bind, read-only (SE-4) |
| Dependency compromise | Lockfile, SBOM, Dependabot (SE-6) |
| Overclaiming in docs/UI misleads users | EV-3/EV-4, CONTRIBUTING.md ground rule 1, PR checklist |

## 10. Extension points (post-v0.1)

- **Ingestion adapters**: OTLP receiver and log adapters mapping external formats to EvidenceRecord (trust always `asserted` unless a tap is proven).
- **Signing**: DSSE/in-toto envelopes per record or per bundle (OD-3).
- **External schema alignment**: mapping layer to other agentic process-evidence formats (OD-1).
- **New gap rules / claim evaluators**: plugin registry keyed by rule id.
