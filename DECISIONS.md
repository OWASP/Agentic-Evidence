# DECISIONS.md — Architecture Decision Log

Lightweight ADRs. Every decision is **Proposed** until a project maintainer marks it **Accepted** in a merged PR. Superseded decisions stay in the log with a pointer to the replacement.

Format: Context → Decision → Consequences → Alternatives considered.

| ID | Title | Status |
|----|-------|--------|
| ADR-0001 | Python 3.12 for the MVP, not Go | Proposed |
| ADR-0002 | Evidence record is the unit; OpenTelemetry is the correlation transport | Proposed |
| ADR-0003 | JSON Schema is the canonical contract; pydantic mirrors it | Proposed |
| ADR-0004 | Three trust levels on records; "unknown" is a Gap | Proposed |
| ADR-0005 | Gaps and claims are first-class outputs; four claim statuses | Proposed |
| ADR-0006 | Determinism via injected clock and derived IDs | Proposed |
| ADR-0007 | Scripted stub agent; no live LLM | Proposed |
| ADR-0008 | SQLite append-only store + deterministic zip bundles | Proposed |
| ADR-0009 | Bundle integrity = SHA-256 manifest; no signing in v0.1 | Proposed |
| ADR-0010 | UI accesses data only through the read-only API | Proposed |
| ADR-0011 | Minimization: digests and references, not raw content | Proposed |
| ADR-0012 | OTel GenAI semantic conventions inform naming, not the contract | Proposed |
| ADR-0013 | Scenario variants vary evidence, not behaviour | Proposed |
| ADR-0014 | Tooling: uv, ruff, mypy, pytest, Typer | Proposed |
| OD-1 … OD-6 | Open decisions | Open |

---

## ADR-0001 — Python 3.12 for the MVP, not Go

**Context.** README lists "Python with FastAPI, or Go where appropriate". Two languages in an incubation-stage repo doubles CI, review burden, and contributor onboarding.
**Decision.** Single language: Python 3.12 for everything in v0.1.
**Consequences.** Lowest barrier for security-practitioner contributors; native OTel SDK, FastAPI, Streamlit, jsonschema. Go may be reconsidered for a future high-volume ingestion adapter, via a new ADR.
**Alternatives.** Go core + Python UI (rejected: two toolchains for no MVP benefit).

## ADR-0002 — Evidence record is the unit; OTel is the correlation transport

**Context.** OTel spans carry trace context well but have no notion of trust level, provenance channel, or gaps, and span attributes are loosely typed. FAQ states traces do not prove what an agent did.
**Decision.** The `EvidenceRecord` (schema-validated) is the unit of evidence. OTel provides `trace_id`/`span_id`/`parent_span_id` and optional OTLP export for interoperability. Spans are never treated as evidence on their own.
**Consequences.** Some duplication between span attributes and records. Clear separation between "what was emitted for observability" and "what we evaluate as evidence".
**Alternatives.** Spans-as-evidence with custom attributes (rejected: can't express trust or gaps cleanly; attribute limits; tempts overclaiming).

## ADR-0003 — JSON Schema is canonical; pydantic mirrors it

**Context.** The schema is a published artifact other projects may consume. Generating it from pydantic ties the contract to an implementation detail.
**Decision.** Hand-written JSON Schema (draft 2020-12) in `schemas/evidence/v<semver>/`. Pydantic v2 models mirror it; a parity test validates model output against the schema and fixtures against both.
**Consequences.** Two artifacts to keep in sync; the parity test catches drift.
**Alternatives.** Schema generated from pydantic (rejected for contract stability).

## ADR-0004 — Three trust levels on records; "unknown" is a Gap

**Context.** README requires distinguishing observed records, component assertions, independently verified evidence, and unknowns.
**Decision.** `trust ∈ {asserted, observed, verified}` on records, assigned by the recorder from the arrival channel (see ARCHITECTURE §4). Unknowns are `Gap` objects, not records with `trust: unknown`.
**Consequences.** Nothing can be "a record of nothing". Trust can't be self-declared by emitters.
**Alternatives.** Numeric trust score (rejected: false precision); four-level enum on records (rejected: conflates absence with weak presence).

## ADR-0005 — Gaps and claims are first-class; four claim statuses

**Context.** The project's value is stating what evidence does and doesn't support.
**Decision.** Analyzer outputs only `Gap` and `Claim`. Claim status ∈ {`supported`, `supported_by_assertion_only`, `contradicted`, `insufficient_evidence`}.
**Consequences.** No "detected/not detected" output anywhere. Tests assert statuses per variant.
**Alternatives.** Boolean findings (rejected: hides assertion-only support); confidence scores (rejected for v0.1, EV-3).

## ADR-0006 — Determinism via injected clock and derived IDs

**Context.** Repeatability is a project principle; golden bundles need byte-identical output.
**Decision.** `Clock` protocol injected everywhere (`FixedStepClock` in scenarios). IDs are `uuid5(NAMESPACE, f"{seed}:{counter}")` with a per-run counter. OTel configured with a deterministic `IdGenerator`. Lint rule bans `datetime.now`, `time.time`, `uuid4`, unseeded `random` in `src/`.
**Consequences.** Slightly awkward APIs (clock passed around); fully reproducible bundles.
**Alternatives.** Normalize timestamps/IDs at comparison time (rejected: hides nondeterminism bugs).

## ADR-0007 — Scripted stub agent; no live LLM

**Context.** FAQ: initial scenarios must not need a live model. LLM output is nondeterministic and adds cost/keys.
**Decision.** `sim/` executes scripted steps; "decisions" are fixture data.
**Consequences.** Scenarios demonstrate evidence properties, not model susceptibility — docs must say so.
**Alternatives.** Local model (e.g. Ollama) with fixed seed (deferred: still nondeterministic across hardware/versions).

## ADR-0008 — SQLite append-only store + deterministic zip bundles

**Decision.** SQLite with insert-only store API; bundle = deterministic zip of canonical JSON/JSONL (ARCHITECTURE §8).
**Consequences.** Zero-infra, inspectable. Not tamper-proof — documented.
**Alternatives.** JSON fixtures only (rejected: awkward queries for UI); Postgres (rejected: infra).

## ADR-0009 — Bundle integrity = SHA-256 manifest; no signing in v0.1

**Context.** RESOURCES notes a hash only helps if the reference is trusted. Signing needs key management decisions out of MVP scope.
**Decision.** `SHA256SUMS` + per-record digests. Manifest field `integrity: "sha256-manifest"`.
**Consequences.** Detects accidental corruption; does not resist a capable tamperer. Stated plainly in docs.
**Alternatives.** DSSE/Sigstore signing (deferred → OD-3).

## ADR-0010 — UI accesses data only through the read-only API

**Decision.** Streamlit UI calls FastAPI; no direct SQLite access. API binds 127.0.0.1.
**Consequences.** One security boundary to harden; API is reusable by other front ends.

## ADR-0011 — Minimization: digests and references, not raw content

**Decision.** Records store `*_digest` and `*_ref` for prompts, retrieved content, descriptors, tool args/outputs. Raw content only with `retain_content: true` on synthetic scenarios.
**Consequences.** Some investigation questions ("what did the doc say?") need the fixture, which is fine for synthetic data and models real-world privacy constraints.

## ADR-0012 — OTel GenAI semantic conventions inform naming, not the contract

**Context.** The GenAI/agent semantic conventions are still evolving; binding the schema to them risks churn.
**Decision.** Use them as naming guidance and provide a documented mapping table; the evidence schema stays independent and versioned.
**Consequences.** A mapping doc to maintain. Revisit when the conventions stabilize.

## ADR-0013 — Scenario variants vary evidence, not behaviour

**Decision.** Within a scenario the scripted execution is identical across variants; variants change which records are emitted and by which channel.
**Consequences.** Directly demonstrates "same events, different provable conclusions" — the project's core message.

## ADR-0014 — Tooling

**Decision.** `uv` (lockfile), `ruff`, `mypy --strict`, `pytest` (+ `hypothesis` for canonical serialization), `jsonschema`, Typer CLI (`ae`), GitHub Actions, Dependabot, CycloneDX SBOM on release.

---

## Open decisions

### OD-1 — Alignment with JFrog `agentic-process-evidence` (issue #1) — **BLOCKS schema v1.0**
Issue #1 (opened 2026-11-01) proposes integrating a parallel agentic process-evidence effort and offers provenance and session-log collection work. Options: (a) adopt their record format as the base; (b) keep this schema and publish a bidirectional mapping; (c) co-design v1.0 jointly. **Action:** maintainers review that repo and respond before schema leaves 0.x. v0.1 work can proceed because 0.x is explicitly unstable (EN-3).

### OD-2 — Streamlit vs. a static UI
Streamlit is fastest to build; a static HTML viewer over the bundle would let investigators open bundles with no server. Decide at M4.

### OD-3 — Signing and attestation
DSSE/in-toto envelopes, Sigstore keyless vs. local keys, per-record vs. per-bundle. Post-v0.1.

### OD-4 — Agent identity model
Current `delegation_chain` is a flat list of strings. Needs alignment with OAuth/OIDC token-exchange semantics and workload identity before v1.0.

### OD-5 — Real ingestion
Whether v0.2 adds an OTLP receiver or log adapters, and what trust such records get (default `asserted`).

### OD-6 — Repository governance
Who can mark ADRs Accepted; CODEOWNERS; whether ADRs move to `docs/adr/NNNN-*.md` once there are more than ~20.
