# Glossary

Shared vocabulary for issues, docs, code, and reviews.
Where a term has a normative definition elsewhere, this page links to it, and that source wins if the two disagree.

## Evidence and trust

**Evidence record.**
The unit of evidence: a schema-validated JSON object describing one security-relevant event in an agent run (see [ARCHITECTURE.md §3.1](../ARCHITECTURE.md#31-evidencerecord)).
An OpenTelemetry span is not an evidence record (ADR-0002).

**Channel.**
How a record reached the recorder: `self-report`, `interception`, or `reference-check`.
The recorder assigns trust from the channel, never from what the emitter says about itself.

**Trust level.**
One of three values carried by every record (ADR-0004, [ARCHITECTURE.md §4](../ARCHITECTURE.md#4-trust-model)):

| Term in README/FAQ | `trust` value | Meaning |
|---|---|---|
| Component assertion | `asserted` | A component's statement about itself or its view of the world, for example an agent runtime log, a tool's self-report, or a policy engine's own log. |
| Observed record | `observed` | The recorder itself saw the bytes at an interception point it controls. It is only as trustworthy as the recorder and where the tap is placed. |
| Independently verified | `verified` | The record was checked against a reference outside the agent's control, or two independent sources agree. The record states what it was verified against. |
| Unknown | *(no record)* | Required evidence is absent. This is represented as a **gap**, never as a record with an "unknown" trust value. |

**Gap.**
A missing or insufficient record that a specific conclusion needs.
Every gap names the rule that raised it (`G-AREA-NNN`), the records involved, what is missing, and which conclusion it blocks.
A gap is a result, not an error.

**Claim.**
A statement about a run that the analyzer evaluates, such as "`email.send` was authorised".
The status of a claim is exactly one of:

| Status | Meaning |
|---|---|
| `supported` | Every required element is present, at least one at `observed` or `verified`, and nothing contradicts it. |
| `supported_by_assertion_only` | Every required element is present, but all of them are `asserted`. |
| `contradicted` | A required element exists and conflicts with the claim. |
| `insufficient_evidence` | At least one required element is missing (a blocking gap exists). |

There is no numeric confidence score in v0.1 (EV-3).

## Integrity and identity

**Digest.**
A SHA-256 hash of canonical bytes.
A digest shows only whether bytes differ from a reference.
It does not show who produced them, whether they were used, or that nothing was omitted (EV-5).

**Reference pin.**
A `reference.pin` record that states the expected digest of a subject, such as a tool descriptor, and where that expectation came from.
It only supports a `verified` result if its source is outside the agent's control.

**Bundle integrity.**
In v0.1 an evidence bundle carries a SHA-256 manifest.
That detects accidental change.
It is not a signature and does not make a bundle tamper-proof (EV-7).

## Time and correlation

**Event time.**
The time a component reports for an event (`event_time`).
It is asserted by that component.

**Collection time.**
The time the recorder received the record (`collected_at`), taken from the recorder's own clock.
Any ordering conclusion states which of the two clocks it used (EV-6).

**Correlation.**
A link between records built only from explicit fields: trace parentage, `invocation_id`, `caused_by`, `descriptor_digest`, and the delegation chain ([ARCHITECTURE.md §5](../ARCHITECTURE.md#5-correlation)).
Records that happened close together in time are not correlated for that reason.

**Influence.**
A claim that one input (for example a retrieved document) affected a later action.
Correlation is not causation.
A shared trace or a later timestamp does not establish influence.
Only an explicit `caused_by` link can, and its trust is the trust of the record that asserts it.
A finer-grained "influence evidence ladder" is an open question (HANDOFF.md Q6).

## Scenarios

**Scenario.**
A deterministic, synthetic, scripted agent run under `scenarios/sN-short-name/`.
The agent is a stub with no live LLM (ADR-0007).

**Variant.**
A version of a scenario that changes **which evidence is emitted**, not what the agent does (ADR-0013).
It shows the same execution leading to different provable conclusions.

**Oracle.**
A scenario's `expected.yaml`: the gaps and claim statuses each variant must produce.
It is the test that decides whether the implementation is right.
