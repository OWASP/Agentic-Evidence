# HANDOFF.md

The live state of the project. Whoever picks this up next — human or agent — starts here. **Update this file in every PR that changes project state.**

_Last updated: 2026-11-08_

---

## 1. Current state

- Project status: OWASP incubation; MVP is planned, not built. No schema, evidence code, or scenarios exist yet.
- Docs: `README.md`, `FAQ.md`, `RESOURCES.md`, `AGENTS.md`, plus the handoff set (`CONSTRAINTS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `HANDOFF.md`).
- `CLAUDE.md` (Claude Code agent instructions) is kept local only and is git-ignored; public docs must not link to it. Public agent guidance lives in `AGENTS.md`.
- M0 (in progress, branch `m0/repo-hygiene`) added:
  - Governance: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` (links the OWASP policy), `docs/glossary.md`, `.github/CODEOWNERS`.
  - Issue forms (bug, scenario proposal, gap-rule proposal, schema change, research) and a PR template under `.github/`.
  - Empty Python 3.12 package `src/agentic_evidence/` (version only), `pyproject.toml`, `uv.lock`, `Makefile` (`setup`, `lint`, `test`, `check`), `.gitattributes` (LF everywhere, for DT-3), `.gitignore`.
  - Directory layout from the target in CLAUDE.md: empty `src/agentic_evidence/` subpackages, `schemas/evidence/v0.1/`, `scenarios/`, `ui/`, `deploy/`, `docs/research/`, `tests/scenario/`, `tests/golden/`. Each placeholder names the milestone that fills it; none contains functionality.
  - Tests: package smoke test and `tests/unit/test_doc_links.py`, which fails if any relative Markdown link or heading anchor in the repo is broken.
  - CI: `.github/workflows/ci.yml` (ruff, ruff format, mypy --strict, pytest on ubuntu + macos), `secret-scan.yml` (TruffleHog), `dependabot.yml` (uv + GitHub Actions). Actions are pinned to commit SHAs.
- All ADRs are still **Proposed**.

### Known problems in the repo right now
| Problem | Fix |
|---------|-----|
| Issue #1 (JFrog agentic-process-evidence integration) has no maintainer response | Respond in M0; track as OD-1 |
| Labels used by the issue forms and CONTRIBUTING.md don't exist on GitHub yet; GitHub silently skips labels that don't exist | Maintainer creates them (list in CONTRIBUTING.md "Labels") |
| Private vulnerability reporting must be switched on in repo settings for the SECURITY.md link to work | Maintainer: Settings → Code security → Private vulnerability reporting |
| Secret-scan and CI workflows have not run on GitHub yet | First PR from `m0/repo-hygiene` |

Resolved in M0: `SECURITY.md` and `CONTRIBUTING.md` exist and README/FAQ link to them.
Removed as redundant: the old `GETTING_STARTED.md` (a contribution guide duplicated by `CONTRIBUTING.md`; its unique sections moved there) and a short-lived `ROADMAP.md` (duplicated this file's milestones). README/FAQ now link to the milestones below. `GETTING_STARTED.md` returns in M5 as a runnable walkthrough.

## 2. Milestones

Work strictly in order. Don't start a milestone until the previous one's acceptance criteria pass.

### M0 — Repo hygiene and governance
- [ ] Maintainer review of `DECISIONS.md`; mark accepted ADRs.
- [x] `SECURITY.md` (private vulnerability reporting via GitHub), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (OWASP), `CODEOWNERS`.
- [x] Issue templates: bug, scenario proposal, gap-rule proposal, schema change (plus research).
- [x] README/FAQ links resolve (old `GETTING_STARTED.md` folded into `CONTRIBUTING.md`; recreated in M5).
- [ ] Reply on issue #1; schedule a schema-alignment discussion (OD-1).
- [x] CI skeleton: GitHub Actions running ruff, mypy, pytest on an empty package; secret scanning; Dependabot. (Not yet run on GitHub.)
- [ ] Repo settings: create labels, enable private vulnerability reporting, enable GitHub secret scanning + push protection, require CI on `main`.
- [ ] Open the first labelled issues (draft list from the M0 planning session: schema versioning policy, provenance block fields, gap record structure, influence evidence ladder, S1 fixtures, S2/S3 specs, fixture validation in CI).

**Accept when:** CI is green on `main`, all README/FAQ links resolve, ADRs have a status set by a maintainer.

### M1 — Schema v0.1 and models
- [ ] `schemas/evidence/v0.1/`: `record`, `gap`, `claim`, `bundle-manifest` schemas (draft 2020-12).
- [ ] Pydantic models in `src/agentic_evidence/model/`.
- [ ] Canonical serializer (sorted keys, fixed float format) + `record_digest`.
- [ ] Parity test, fixture validation, hypothesis test for canonical round-trip.

**Accept when:** `make schema-check` validates hand-written example records for every kind in ARCHITECTURE §3.2; parity test passes; digests stable across runs and OSes in CI matrix (ubuntu, macos).

### M2 — Deterministic core + S1
- [ ] `clock.py`, `ids.py`, lint ban on nondeterministic calls.
- [ ] `sim/` stub agent, mock tools, retriever, PDP; scenario loader.
- [ ] `telemetry/` with deterministic OTel IdGenerator; in-memory exporter in tests.
- [ ] `recorder/` (validation, limits, trust assignment), `store/` (SQLite insert-only).
- [ ] `s1-benign` with variants `full`, `runtime-only`.
- [ ] `ae run`.

**Accept when:** running S1 twice with the same seed yields byte-identical `records.jsonl`; a record with an invalid schema is rejected and counted; `runtime-only` records are all `asserted`.

### M3 — Correlation, gap rules, claims, S2, S3
- [ ] `correlate/` graph from explicit fields only.
- [ ] All v0.1 gap rules (ARCHITECTURE §6) with positive/negative tests.
- [ ] Claim evaluators: authorization, influence, descriptor-identity, outcome.
- [ ] `s2-retrieval-poisoning` (3 variants), `s3-descriptor-modification` (3 variants), each with `expected.yaml`.
- [ ] `ae analyze`.

**Accept when:** every variant's gaps and claim statuses match `expected.yaml` exactly; no code path emits "detected".

### M4 — Bundle, API, UI
- [ ] Deterministic bundle export + `ae verify` (recompute, revalidate, re-analyze).
- [ ] Import hardening (SE-5) with zip-slip/zip-bomb tests.
- [ ] FastAPI read-only API on 127.0.0.1.
- [ ] Streamlit UI: run list, timeline (collected_at / event_time toggle), event detail (escaped), correlation graph, gaps, claims with supporting/contradicting records.
- [ ] Decide OD-2.

**Accept when:** golden bundles for all 8 variants committed and verified in CI; UI renders a payload containing `<script>` and Markdown as literal text (test).

### M5 — Packaging and v0.1.0 release
- [ ] `deploy/docker-compose.yaml` (app, UI, optional local OTel Collector).
- [ ] `GETTING_STARTED.md` with a 5-minute walkthrough of S2 `no-influence-link`.
- [ ] Mapping doc: evidence fields ↔ OTel GenAI semantic conventions (ADR-0012).
- [ ] CycloneDX SBOM attached to release; tag `v0.1.0`.

**Accept when:** a new contributor can go from clone to viewing S2 gaps in the UI in under 10 minutes using only `GETTING_STARTED.md`.

### After v0.1 (candidates, not committed)

Each needs its own issue or ADR:

- OTLP and log ingestion adapters, where lossy mappings become gaps and ingested records default to `asserted` (OD-5).
- Signing and attestation of records or bundles (OD-3).
- Scenarios that test the project's own claims: evidence tampering, dropped events, out-of-order events.
- Further scenarios: identity/delegation misuse, memory poisoning, MCP tool rug-pull, authorization bypass.
- A published findings report on which evidence was and wasn't sufficient, per scenario.

## 3. Next action (start here)

**M0, remaining:** open a PR from `m0/repo-hygiene` and get CI green on GitHub; a maintainer reviews `DECISIONS.md`, responds to issue #1, and applies the repo settings listed in the M0 checklist.
M1 schema work can start in parallel, because schema 0.x is explicitly unstable, but don't publish anything as "v1" until OD-1 is resolved.

## 4. Open questions

| # | Question | Owner | Blocking |
|---|----------|-------|----------|
| Q1 | Adopt, map, or co-design with JFrog agentic-process-evidence? (OD-1) | Maintainers | Schema v1.0 |
| Q2 | Who has authority to mark ADRs Accepted? (OD-6) | Maintainers | M0 |
| Q3 | Streamlit or static bundle viewer? (OD-2) | Contributors | M4 |
| Q4 | Default G-TIME-001 skew tolerance — 5s reasonable? | Contributors | M3 |
| Q5 | Should `side_effect` classification be in the descriptor, the invocation, or both? | Contributors | M3 |
| Q6 | Define an "influence evidence ladder": levels between "B followed A" and "A caused B" (temporal only, same trace, asserted `caused_by`, observed data flow, verified), so S2 can't be read as a causal claim. Fits inside the four claim statuses or needs an ADR? | Contributors | M1 schema for `caused_by`, M3 S2 |
| Q7 | Move ADRs to `docs/adr/NNNN-*.md` now (one file per ADR, easier review) or at ~20 ADRs as OD-6 suggests? | Maintainers | No |

## 5. Session log

Append one entry per working session. Newest first.

| Date | Who | What changed | Next |
|------|-----|-------------|------|
| 2026-11-14 | paolocostanzo | Research write-up `docs/research/mcp-approval-binding-and-digest-provenance.md` (#5 points 2 and 3) and index line in `docs/research/README.md`; no milestone state change | #6 ADR; S2/S3 specs issue; #4 for digest bytes |
| 2026-11-08 | Claude Code (with SyedDS) | M0 governance docs, issue forms, PR template, CODEOWNERS, empty package, CI + secret scan + Dependabot, doc-link test; target directory layout with milestone placeholders; CLAUDE.md made local-only (git-ignored); removed redundant GETTING_STARTED.md and ROADMAP.md | PR + maintainer settings, issue #1 reply |
| 2026-11-06 | - | Added CLAUDE.md, CONSTRAINTS.md, ARCHITECTURE.md, DECISIONS.md, HANDOFF.md; revised README.md | M0 review |
