# CONSTRAINTS.md

Constraints are requirements that bound the design. **MUST** items are non-negotiable for the MVP; changing one needs an ADR in `DECISIONS.md` approved by a maintainer. **SHOULD** items can be relaxed with a written reason in the PR.

Source: derived from `README.md`, `FAQ.md`, and `RESOURCES.md` as published in the repository, plus decisions in `DECISIONS.md`.

---

## 1. Scope constraints

| ID | Constraint | Level |
|----|-----------|-------|
| SC-1 | The MVP is a **local reference application**. No production deployment, HA, multi-tenant access control, or retention management. | MUST |
| SC-2 | No enforcement, blocking, or automated response. The project observes and evaluates; it never acts on an agent. | MUST |
| SC-3 | Not an agent runtime or model provider. The agent in scenarios is a scripted stub. | MUST |
| SC-4 | Complements OWASP taxonomies and testing projects; does not redefine risk categories. Scenarios may reference taxonomy IDs via `taxonomy_refs`. | MUST |
| SC-5 | Exactly three scenarios in v0.1: benign baseline, retrieval poisoning, tool-descriptor modification. New scenarios go to v0.2+. | SHOULD |

## 2. Runtime and environment constraints

| ID | Constraint | Level |
|----|-----------|-------|
| RT-1 | Runs with Docker Compose **or** a plain Python venv. No Kubernetes, cloud account, or managed service. | MUST |
| RT-2 | No live LLM and no model API key anywhere in the default code path or CI. | MUST |
| RT-3 | No outbound network access at runtime. The OTLP collector, if used, is local to the compose network. | MUST |
| RT-4 | Runs offline after `make setup`. | SHOULD |
| RT-5 | Full test suite completes in under 2 minutes on a laptop-class machine. | SHOULD |

## 3. Determinism constraints

| ID | Constraint | Level |
|----|-----------|-------|
| DT-1 | Same scenario, variant, and seed ⇒ byte-identical evidence bundle. Enforced by golden tests. | MUST |
| DT-2 | All timestamps come from the injected `Clock`; all IDs from `ids.py` (seeded/derived). `datetime.now()`, `time.time()`, `uuid4()`, and unseeded `random` are banned in `src/` (lint rule). | MUST |
| DT-3 | Serialization is canonical: sorted keys, UTF-8, `\n` line endings, fixed float formatting; zip entries sorted with fixed mtimes. | MUST |
| DT-4 | Dict/set iteration order must never affect output. | MUST |

## 4. Evidence and claims constraints

| ID | Constraint | Level |
|----|-----------|-------|
| EV-1 | Every record carries a `trust` level: `observed`, `asserted`, or `verified`. Missing required evidence is represented as a `Gap`, never as a record. | MUST |
| EV-2 | A component's statement about its own behaviour is `asserted`. Only the mechanisms in `ARCHITECTURE.md §4` may produce `verified`. | MUST |
| EV-3 | Claim statuses are limited to: `supported`, `supported_by_assertion_only`, `contradicted`, `insufficient_evidence`. No numeric "confidence score" in v0.1. | MUST |
| EV-4 | The project must not state an attack is detectable unless a scenario test demonstrates it for that variant. | MUST |
| EV-5 | Hash = change detection against a trusted reference only. A digest alone never establishes authorship, use, or completeness, and the UI/docs must not imply it does. | MUST |
| EV-6 | Event time (component-reported) and collection time (recorder) are stored separately. Ordering conclusions state which clock they used. | MUST |
| EV-7 | Bundle integrity in v0.1 is a SHA-256 manifest (tamper-evident against accidental change only). Docs must not describe bundles as "signed" or "tamper-proof". | MUST |

## 5. Data constraints

| ID | Constraint | Level |
|----|-----------|-------|
| DA-1 | Synthetic data only in fixtures, tests, docs, and issues. No production traces, secrets, customer data, or personal data. | MUST |
| DA-2 | Fixtures use reserved names: `example.com`/`.test`/`.invalid` domains, RFC 5737 IPs, obviously fake identities. | MUST |
| DA-3 | Minimization by default: records store digests and references for prompts, retrieved content, and tool arguments. Raw content is stored only when a scenario explicitly sets `retain_content: true`, and only for synthetic data. | MUST |
| DA-4 | A pre-commit/CI secret scan runs on every PR. | MUST |

## 6. Security constraints (the tool itself)

| ID | Constraint | Level |
|----|-----------|-------|
| SE-1 | All ingested records are untrusted input: schema-validated, size-limited (default 64 KiB/record, 10k records/run), rejected on failure with a counted error. | MUST |
| SE-2 | Record content is rendered as escaped text in the UI. No Markdown/HTML rendering of payload fields. | MUST |
| SE-3 | Record content is never passed to an interpreter, template engine, shell, or LLM. | MUST |
| SE-4 | API is read-only (except `POST /runs` in dev mode) and binds to `127.0.0.1` by default. | MUST |
| SE-5 | Bundle import rejects path traversal, absolute paths, symlinks, and archives exceeding size/entry limits. | MUST |
| SE-6 | Dependencies pinned with a lockfile; CI produces a CycloneDX SBOM for releases. | SHOULD |
| SE-7 | `SECURITY.md` with a private reporting channel exists before the first tagged release. | MUST |

## 7. Engineering constraints

| ID | Constraint | Level |
|----|-----------|-------|
| EN-1 | Python 3.12; `mypy --strict` on `src/`; `ruff` lint + format. | MUST |
| EN-2 | JSON Schema in `schemas/` is the canonical contract; pydantic models must stay in parity (tested). | MUST |
| EN-3 | Schema versions follow semver. Pre-1.0 (`0.x`) may break; post-1.0 breaking changes need a major bump and migration note. | MUST |
| EN-4 | Apache-2.0. New files carry an SPDX header (`SPDX-License-Identifier: Apache-2.0`). | MUST |
| EN-5 | `analyze/` and `correlate/` are pure (no I/O). | SHOULD |
| EN-6 | No new runtime dependency without justification in the PR. | SHOULD |

## 8. Explicit non-goals for v0.1

- Signing/attestation of records or bundles (planned post-MVP, see OD-3).
- Live agent framework integrations (LangGraph, MCP servers, etc.).
- Streaming ingestion or OTLP ingestion from external systems.
- Detection scoring, anomaly detection, or ML-based analysis.
- Multi-user UI, authentication, RBAC.
- Mapping every OWASP Agentic risk; only the three scenarios.
