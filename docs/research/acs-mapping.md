<!-- SPDX-License-Identifier: Apache-2.0 -->

# Mapping OWASP Agent Control Standard (ACS) decisions to Agentic Evidence records

**Status:** Research write-up.
Nothing here is a decision, a schema change or an implemented capability.
It does not propose adopting ACS or depending on it (ADR-0012, OD-1).

**Informs:** [#15](https://github.com/OWASP/Agentic-Evidence/issues/15), [#6](https://github.com/OWASP/Agentic-Evidence/issues/6) (claim-status derivation), [#26](https://github.com/OWASP/Agentic-Evidence/issues/26) (dispatch and effect evidence), OD-4 (agent identity) and OD-5 (real ingestion).
**Related:** [#4](https://github.com/OWASP/Agentic-Evidence/issues/4) (which bytes `descriptor_digest` covers), [MCP approval binding](mcp-approval-binding-and-digest-provenance.md) (#5, #7).

"AR §n" below means a section of [ARCHITECTURE.md](../../ARCHITECTURE.md); a bare "§n" is a section of this write-up.
"The spec" means the ACS normative text, [specification.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md).

## 1. Questions

- **Q1, mapping.** Which ACS outputs can be projected into which v0.1 record kinds ([AR §3.2](../../ARCHITECTURE.md#32-record-kinds-v01)), mainly `authz.decision`, `tool.invocation`, `tool.result` and `retrieval.result`?
- **Q2, trust.** What trust level can each projected record honestly carry under [AR §4](../../ARCHITECTURE.md#4-trust-model)?
- **Q3, gaps.** Which investigation questions does ACS evidence still leave open?

Out of scope: code, runtime integration, ACS as a dependency, and changes to the v0.1 schema.

## 2. Method and sources

1. **Version read.** The ACS repository, [GenAI-Security-Project/agent-control-standard](https://github.com/GenAI-Security-Project/agent-control-standard), default branch `integration`, commit `b1d2abc8a1194f4909907a07ffdc03f07f37b9f9` (2026-11-27).
   `version.txt` reads `0.1.5` (the release); the specification and the wire format are **v0.1.0** ([specification.md line 3](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L3)).
   The ACS changelog says release 0.1.5 changes the v0.1.0 schema files in place and asks claimants to name the release or its commit ([CHANGELOG.md line 7](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/CHANGELOG.md#L7)), so every ACS link below is pinned to that commit.
2. **Primary sources.** The normative specification, the JSON Schemas under `specification/v0.1.0/`, [conformance.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/conformance.md), the trace pages ([events.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/events.md), [extend_opentelemetry.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/extend_opentelemetry.md), [otel-mapping.json](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/trace/otel-mapping.json), [ocsf-mapping.json](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/trace/ocsf-mapping.json)) and the identity pages.
3. **Implementations.** What the reference Guardians, the adapters and the lab gateway actually emit, from their READMEs and mapping pages, to separate "the spec defines it" from "something sends it".
4. **Record walk-through** of each ACS output against the v0.1 record kinds, trust model, correlation ([AR §5](../../ARCHITECTURE.md#5-correlation)) and gap rules ([AR §6](../../ARCHITECTURE.md#6-gap-rules-v01)), applying the four rules in #15: no invented `caused_by`, `delegation_chain`, `descriptor_digest` or `policy_digest`; `modify` is not `allow`; `ask` is not authorization until a record of the answer exists; ACS reasoning is referenced by digest only.

Facts are labelled **[spec]** (normative v0.1.0 text or schema) or **[lab]** (a reference-implementation convention the spec does not define).
No code was written and no ACS component was run.

## 3. ACS in one page

ACS puts a **Guardian** beside an agent (the spec's "Observed Agent").
At each lifecycle hook the agent's host sends a JSON-RPC request (`steps/<hook>`) and waits for a decision.

- **Hooks [spec].** Nineteen `steps/*` methods, from `sessionStart` to `sessionEnd` ([specification.md lines 128-148](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L128-L148)).
  The ACS-Core profile requires `sessionStart`, `userMessage` or `agentTrigger`, `toolCallRequest`, `toolCallResult`, `agentResponse` and `sessionEnd` (plus `subagentStart` for subagent-capable clients); the retrieval, memory, turn, compact and skill hooks are SHOULD "when observable" ([conformance.md line 32](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/conformance.md#L32)).
  Nobody verifies a conformance claim ([conformance.md line 50](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/conformance.md#L50)).
- **Request [spec].** `params` carries `acs_version`, `request_id` (a UUID), `timestamp`, `metadata` (`agent_id`, `session_id`, and optional `user_context`, `turn_id` and others) and a hook payload ([request-envelope.json](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/request-envelope.json)).
  `toolCallRequest` carries `tool` {`name`, `version`, `provider`} and `arguments`; `toolCallResult` carries `tool`, `exit_status` (`success|failure|timeout|blocked`), `outputs` and an optional `request_id_ref` back to the request ([tool-call-request.json](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/hooks/tool-call-request.json), [tool-call-result.json lines 19-23](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/hooks/tool-call-result.json#L19-L23)).
- **Decision [spec].** `decision` ∈ `allow|deny|modify|ask|defer` ([response-envelope.json line 42](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/response-envelope.json#L42)), with `reasoning`, `reason_codes`, `policy_references[]` {`policy_id`, `policy_version`, `policy_name`, `rule_id`}, `modifications`, `ask_details`, `defer_details`, `chain_hash`, `signature` and `metadata` {`evaluator`, `model_id`, `confidence`, ...}.
- **Failure posture [spec].** If no usable decision arrives, `on_decision_failure` (`proceed` or `deny`, negotiated at handshake) decides. The v0.1.0 text defaults to `proceed`; a note in release 0.1.5 records the leads' decision to make `deny` the default (D-036), not yet in the text, and the implementations split: the adapters, the gateway, the example Guardian and the Go Guardian deny, while the TypeScript Guardian (AGT) declares `proceed` ([specification.md lines 228-236](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L228-L236)). Every failure MUST be audited in the Observed Agent's own log, and emitting an `acs.decision.failure` event is SHOULD ([handshake.json lines 127-131](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/handshake.json#L127-L131), [specification.md line 225](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L225)).
- **Trace [spec].** OTel spans `gen_ai.tool.call` and `gen_ai.tool.result`, a decision event `acs.decision` and a failure event `acs.decision.failure`, all keyed by `acs.session.id` + `acs.request_id`; OCSF classes 1007, 2004 and 6002 ([events.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/events.md)).
  Both the Guardian and the Observed Agent write trace streams.
- **Integrity [spec].** The baseline signature is HMAC-SHA256 with a per-session key that both parties derive. The Guardian also keeps a hash-chained log of ContextEntries and publishes a signed `chain_hash` ([specification.md lines 343-349](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L343-L349), [line 388](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L388)).
  Non-repudiation needs the asymmetric ACS-Crypto profile.

ACS's own trace page already draws the line this project cares about: no decision event proves enforcement on its own ([events.md line 53](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/events.md#L53)).

## 4. Findings

### 4.1 Field mapping (Q1)

Correlation first.
An ACS `request_id` is unique per step, and `toolCallResult.request_id_ref` points back to the `toolCallRequest`.
`session_id` + the `toolCallRequest`'s `request_id` is therefore the only candidate for `correlation.invocation_id`, joining the decision on that request, the invocation and the result.
`request_id_ref` is optional, so a result without it does not join (§4.3, gap 6).

| ACS output | AE record kind | AE field ← ACS field | Rule |
|---|---|---|---|
| `toolCallRequest` request [spec] | `tool.invocation` (attempt) | `tool_name` ← `tool.name`; `args_digest` ← digest of the canonical `arguments`; `invocation_id` ← `session_id`:`request_id`; `event_time` ← `timestamp` | A request to call, sent **before** the decision. It is not dispatch (#26). |
| Same | `tool.invocation` | `descriptor_digest` | **Gap.** The spec has no tool descriptor digest. The lab gateway puts `sha256:` + JCS of the tool declaration into `tool.version` [lab] ([tool_digest.py](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/adapters/gateway/src/acs_gateway/tool_digest.py)) and says the digest is no tamper evidence on its own. It could be carried as a separately labelled `asserted` value, not as `descriptor_digest` by default (see #4 on digest profiles). |
| Same | `tool.invocation` | `side_effect` | **Gap.** No ACS field; `capability` and `operation` are optional host classifications. |
| Response with `decision` `allow` or `deny` [spec] | `authz.decision` | `decision` ← `allow`/`deny`; `policy_id` ← `policy_references[].policy_id`; `subject` ← `metadata.agent_id` (and `user_context.user_id` when present) | `policy_references` is optional (§4.3, gap 4). With several references, keep all of them. |
| Same | `authz.decision` | `policy_digest` | **Gap.** ACS has `policy_version`, a label, not a digest. Hashing the label would not make it a policy digest. |
| Response with `decision` `modify` [spec] | `authz.decision`, plus the dispatched arguments | `decision` cannot be `allow`: v0.1 has only `allow`/`deny` | **Not representable in v0.1.** An investigator needs both the requested arguments (`args_digest` from the request) and what was dispatched after `modifications`. Today only the request side is reported, and what was dispatched is the host's assertion (§4.2). A `modify` value and a dispatched-arguments digest belong in a schema-change issue. |
| Response with `decision` `ask` [spec] | none on its own | | Not authorization; only the approver's answer is. The spec defines no wire method for the answer and no trace event for how an ASK ends ([events.md line 109](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/events.md#L109)). On `scope: session` the Guardian writes a ContextEntry with `step_type: "intent_extension"` naming the approver ([specification.md lines 361-365](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L361-L365)); for a single-step ASK nothing is required. |
| Response with `decision` `defer` [spec] | none on its own | | Neither allow nor deny. Its outcome (`timeout_decision`, default `deny`) comes later and has no defined trace event. |
| `ask_details.approver` and the `intent_extension` ContextEntry [spec]; the gateway's `x_acs_lab_ask_answer` and `ask_resolved` audit line [lab] | `authz.decision` sourced from the answer | `decision` ← the answer; `subject` ← approver `id` | Only with a record of the answer. The lab gateway labels its own answer `assurance: "declared"`. |
| `reasoning`, `acs.reasoning` [spec] | reference only | a digest in a `*_ref`/`*_digest` field | Possibly model-generated: `metadata.evaluator` may be `agent` or `composite` with a `model_id` ([response-envelope.json lines 102-108](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/specification/v0.1.0/response-envelope.json#L102-L108)), and Guardian reasoning can quote tool arguments. Keep a digest, never treat it as a rationale an investigator can rely on, never render it. |
| `toolCallResult` request [spec] | `tool.result` | `status` ← `exit_status`; `output_digest` ← digest of the canonical `outputs`; `invocation_id` ← `session_id`:`request_id_ref` | `blocked` means the call did not run, which is the host's statement. A decision on the result hook (`allow`/`deny`/`modify` only) governs what the agent sees, not what the tool did. |
| `knowledgeRetrieval` request [spec] | `retrieval.result`, one per `results[]` item | `doc_id` ← `results[].source_id`; `source_uri` ← `source.name` (there is no URI field); `content_digest` ← digest of `results[].value` | A SHOULD-only hook that no adapter or the lab gateway sends today (§4.3, gap 7). |
| `memoryContextRetrieval` request [spec] | `retrieval.result` | `doc_id` ← `memory_id`; `content_digest` ← digest of `value` | Same. |
| `sessionStart.user_identity`, `metadata.user_context`, `metadata.agent_id` [spec] | `identity.principal`, `identity.agent` | `principal` ← `user_id`; `agent` ← `agent_id` | All optional except `agent_id`. |
| `subagentStart` {`parent_session_id`, `parent_step_id`, `subagent_descriptor`} [spec] | `identity.delegation_chain` | | **Gap.** It links a subagent session to its parent session. It says nothing about on whose behalf, or with what authority; a chain built from it would be invented. |
| any field | `correlation.caused_by` | | **Gap.** ACS has `cited_provenance_ids` (the provenance the Guardian cited in its decision) and per-field `provenance`, but nothing links an action to the input that caused it. `cited_provenance_ids` is the Guardian's statement about its own decision, not `caused_by`. |
| `acs.decision.failure` event or audit-log failure entry [spec] | none in v0.1 | | The record of a decision that never arrived. Under `proceed` the step ran ungoverned. v0.1 has no kind for "authorization skipped"; today it surfaces only as G-AUTHZ-001. |
| OTel `trace_id` / `span_id` of ACS spans [spec] | `trace` | `parent_span_id` ← the step span's parent (turn or session span) | Only when a deployment claims ACS-Trace, which builds a session → turn → step span tree ([extend_opentelemetry.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/extend_opentelemetry.md)). The request envelope carries no trace context. |

### 4.2 Trust per record (Q2)

Trust is assigned from the arrival channel (AR §4), so the question is where a recorder could stand.

| Projected record | Default | Why | What would raise it |
|---|---|---|---|
| `authz.decision` from the Guardian's decision event or ContextEntry | `asserted` | The Guardian reports on its own decision: a PDP log, `self-report`. | Nothing inside ACS. A tap on the Guardian's response would make the **sent** decision `observed`, not its enforcement. |
| Same, with a verified HMAC signature | `asserted` | HMAC shows that a holder of the session key wrote it. Both the Guardian and the Observed Agent hold that key, so it shows integrity against a third party, not attribution or independence ([specification.md line 349](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/instrument/specification.md#L349)). | |
| Same, with an ACS-Crypto signature (e.g. ML-DSA-65) verified against a key pinned outside the agent's control | `asserted`, with its origin established | It shows which Guardian issued the decision. It says nothing about enforcement, and the Guardian is still reporting on itself. It is closer to a `reference.pin` check of where the record came from than to a verified decision. | |
| `tool.invocation` from `toolCallRequest` | `asserted` | The host reports what it intends to call, before the decision. | A recorder tap between the host shim and the **tool** (not the Guardian), seeing the call go out: the tool name, the arguments actually sent (after any `modify`) and a call identity that joins the decision. Only that gives an `observed` dispatch, and it is outside ACS. |
| `tool.result` from `toolCallResult` | `asserted` | The host reports the output and its own `exit_status`. | A tap on the tool's response, or an effect observation outside the executor (#26). |
| `retrieval.result` from the retrieval hooks | `asserted` | Host self-report. | A tap at the retriever. |
| One decision reported in both the Guardian's and the Observed Agent's streams | `asserted` | They agree on the same `request_id`, but they share a session key and usually a deployment and an operator. Agreement shows the two did not diverge; it is not two **independent** sources for AR §4 path (b). | Two producers under separate control, e.g. the Guardian's decision and a recorder tap at the tool boundary that saw whether the call went out. |
| The approver's answer (`intent_extension` ContextEntry, or the lab `ask_resolved` line) | `asserted` | Written by the Guardian or the gateway about an answer it received; the gateway labels its own `assurance: "declared"`. | A record from the approval system itself, outside the Guardian's trust domain. |

**Finding A (a Guardian audit log is a component reporting on itself).**
It holds for every ACS-native record: all of them are self-report.
An ACS record deserves more than `asserted` only when a second producer outside the Guardian–host trust domain sees the same bytes, and ACS v0.1.0 defines no such producer.

**Finding B (if an ACS `authz.decision` is only asserted, can an authorization claim be supported?).**
Under AR §4 as written, yes: "invocation was authorized" can reach `supported` if another required element, such as a tapped invocation, is `observed`.
Under the carrying-element rule discussed on #6, the decision is the carrying element of an authorization claim, so the claim stops at `supported_by_assertion_only` until the decision has an `observed` or `verified` route.
ACS gives it neither, so ACS evidence alone cannot take an authorization claim past `supported_by_assertion_only`.
A dispatch observation answers a different question ("did the call go out after a deny?"), which is #26's ground.

**Finding C (Guardian and host shim in one trust domain: two independent sources?).**
No.
They share the HMAC key by construction, the spec says HMAC binds neither party, and in the reference deployments they share an operator.
Their agreement should count as one source.
ACS-Crypto changes the attribution of the Guardian's messages, not the independence of the two parties.

### 4.3 Gaps ACS evidence cannot close (Q3)

1. **No dispatch or enforcement record.** The decision is sent; whether the host applied it is recorded only by the host. ACS says so itself ([events.md line 53](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/events.md#L53)).
2. **Fail-open leaves only the host's word.** Under `on_decision_failure: proceed` a step runs without a decision. The spec requires an audit entry, but in the Observed Agent's own log, and the trace event is SHOULD. A host that under-reports leaves no trace. `proceed` is still the default in the v0.1.0 text and what AGT declares; D-036 and D-045 move the default to `deny` and let only the agent's own configuration opt back into `proceed`.
3. **No principal or delegation chain.** `user_context` and `user_identity` are optional, and `subagentStart` links sessions, not authority. ACS's identity pages propose no wire format ([docs/identity/overview.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/identity/overview.md)). G-ID-001 stays open, and OD-4 is unaffected.
4. **No policy digest, and policy references are optional.** `policy_version` is a label, not content, and the AGT reference Guardian sends `policy_references` with `policy_version` left empty ([its README, line 69](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/reference-implementations/agt/packages/guardian/README.md#L69)). A deployment that omits the references leaves `policy_id` empty.
5. **No tool descriptor binding.** There is no spec field, and the lab gateway's `tool.version` digest is the client's assertion. G-DESC-001, 002 and 003 stay open.
6. **The result-to-request link is optional.** Without `request_id_ref`, a `tool.result` does not join, and G-OUT-001 fires although a result exists.
7. **Hooks defined but not emitted.** The retrieval and memory hooks are SHOULD. None of the adapters (Claude Code, Cursor, NAT) or the lab gateway sends them: NAT surfaces retrievers and memory functions as generic `toolCallRequest`s ([nat/mapping.md lines 20-21](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/adapters/docs/nat/mapping.md#L20-L21)), Cursor leaves its read gates unmapped, and the gateway and AGT emit only the tool hooks (plus session start and end for the gateway). The Go Guardian defines the methods on the receiving side. The inputs S2's influence question needs are absent in practice. Nothing emits OCSF yet ([trace/README.md](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/README.md)).
8. **No `caused_by`.** Provenance tags data with an origin, but nothing links an action to the input that led to it. G-INFL-001 stays open.
9. **ASK and DEFER outcomes.** No wire method for the answer, no trace event for how either one ends, and no required record for a single-step ASK.
10. **No trace context on the wire, and the trace is best-effort.** ACS spans exist only under ACS-Trace, the request carries no `trace_id`, and trace export MUST NOT block enforcement, so a lost span is expected behaviour ([extend_opentelemetry.md line 275](https://github.com/GenAI-Security-Project/agent-control-standard/blob/b1d2abc8a1194f4909907a07ffdc03f07f37b9f9/docs/spec/trace/extend_opentelemetry.md#L275)). G-TRACE-001 depends on the deployment.
11. **`modify` has no dispatched-arguments record.** The Guardian states the change; only the host knows what was sent.

### 4.4 Open questions for the ACS maintainers

1. Could `toolCallRequest` carry a digest of the tool declaration the host holds, under a named profile (the gateway's `tool.version` convention, specified)? It would still be the host's assertion, but it would make G-DESC-001 answerable and digests comparable across hosts (#4).
2. Could `policy_references` carry a content digest of the policy evaluated, next to `policy_version`?
3. Is a host-side "applied outcome" record planned (decision applied, or modified arguments dispatched), so that a reader can tell sent decisions from enforced ones without relying on silence?
4. Will ASK and DEFER get a resolution record (answer, approver identity, time) for every scope, not only `scope: session`?
5. Is `request_id_ref` meant to become required on `toolCallResult`?
6. Is a delegation field (on-behalf-of, or token-exchange `act` semantics) planned for `metadata`, beyond `user_context`?
7. Should `reasoning` from an `agent` or `composite` evaluator be marked as model-generated in the decision itself, beyond `model_id`?

## 5. Recommendation

ACS is worth naming as an evidence **source** in a later ADR, when OD-5 (real ingestion) is taken up, on these terms:

- Records projected from ACS arrive as `self-report` and are `asserted`, whatever their signature. A signature verified against a pinned ACS-Crypto key can be recorded as a statement of origin, but it does not change `trust`.
- Only `allow` and `deny` map to `authz.decision`. `modify`, `ask`, `defer` and decision failures need their own representation, through a schema-change issue (with #26 for dispatch).
- No mapped field fills `caused_by`, `delegation_chain`, `descriptor_digest` or `policy_digest`. Where ACS lacks them, the gap rules fire, which is the intended result.
- The ADR pins the ACS release and commit it read, because v0.1.0 schemas change in place between releases.

ACS strengthens the policy side of a run (which Guardian decided, under which policy label, with what result).
It does not reach the parts this project treats as hardest: dispatch, effect, delegation and influence.
For those, a recorder tap at the tool boundary remains the only route to `observed`.

## 6. Limitations

- One commit of a fast-moving repository was read, and release 0.1.5 already edits v0.1.0 schemas in place.
- The reference Guardians (AGT, Go) were read through their READMEs and conformance pages, not in full.
- The A2A hook pages and `extend_mcp.md` were not examined, and neither was the [genai.owasp.org ACS page](https://genai.owasp.org/resource/agent-control-standard-acs/) named in #15: the repository was taken as the primary source.
- Nothing was run. "Not emitted" statements come from the implementations' own documentation.
- The trust assignments apply AR §4 as written and the carrying-element direction from #6, which is not an accepted ADR.
