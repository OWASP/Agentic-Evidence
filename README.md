# Agentic Evidence

## Security Evidence and Observability for Agentic AI

**Agentic Evidence** is an OWASP open-source reference project exploring how to collect, correlate, and evaluate security evidence for agentic AI execution.

Agent observability can show that an event was logged. A security investigation needs to establish what happened, which identities and permissions were involved, what inputs influenced the action, which policy decisions were made, and what conclusions the available evidence actually supports.

Agentic Evidence focuses on **evidence sufficiency, execution reconstruction, and security investigation**. It complements agent security taxonomies and testing projects rather than duplicating them.

> **Project status:** Incubation. Nothing runnable exists yet beyond CI checks: there is no evidence schema, recorder, or scenario code. The architecture, record model, and commands described here are the intended MVP, documented as **Proposed** decisions that may change. See [Current status](#current-status) for what exists today.

## Goals

- Reconstruct agent executions from correlated execution and security events.
- Connect actions to identities, inputs, retrieved content, tool calls, authorization decisions, and outcomes.
- Make evidence provenance and evidence gaps visible to investigators.
- Demonstrate what can and cannot be concluded from collected evidence.
- Provide deterministic, repeatable scenarios that contributors can run locally.
- Publish an extensible evidence taxonomy and practical guidance for security practitioners.

## Current status

_Last reviewed: 2026-11-28._ [HANDOFF.md](HANDOFF.md) is the authoritative, per-PR record of project state.

| Milestone | Scope | Status |
|---|---|---|
| **M0** Repo hygiene and governance | Governance docs, issue forms, CI, secret scanning, Dependabot, doc-link test | Mostly done. Open: ADR acceptance, repo labels and settings, reply on issue #1 |
| **M1** Schema v0.1 and models | `record`, `gap`, `claim`, `bundle-manifest` schemas; pydantic models; canonical serializer | Started. Hand-written example records are in review; no schema yet |
| **M2** Deterministic core + S1 | Clock, IDs, stub agent, recorder, store, S1 | Not started |
| **M3** Correlation, gap rules, claims, S2/S3 | Gap rules, claim evaluators, S2 and S3 | Not started |
| **M4** Bundle, API, UI | Evidence bundle, `verify`, read-only API, investigation UI | Not started |
| **M5** v0.1.0 release | Docker Compose, getting-started walkthrough, SBOM | Not started |

All architecture decisions in [DECISIONS.md](DECISIONS.md) are currently **Proposed**; none is accepted yet.

**Research published so far** ([docs/research/](docs/research/README.md)):

- MCP tool approval binding and invocation digest provenance.
- Authorization-to-outcome scenarios checked through an external verifier.

Research write-ups inform schema and scenario decisions. They are not decisions or implemented capabilities.

## Initial Scenarios (v0.1)

1. **Benign execution:** Establish a baseline for a normal agent workflow.
2. **Retrieval poisoning:** Demonstrate how retrieved content can influence an agent action and whether the evidence captures that relationship.
3. **Tool descriptor modification:** Evaluate whether the evidence can establish which tool descriptor was observed or used and whether modifications are detectable.

Each scenario has **variants that change which evidence is emitted, not what the agent does**: the same execution, recorded differently, supports different conclusions. Scenarios are deterministic and use synthetic data. The project must not claim that an attack is detectable unless the implementation and tests support that claim.

**After v0.1 (candidates, not committed):** authorization-to-outcome (decision vs. dispatch vs. effect), authority changing before an effect, and MCP tool rug-pull. Each is tracked in its own issue and needs schema changes that are still under discussion.

## How the project reasons about evidence

These are the core concepts of the proposed model. See [ARCHITECTURE.md §4](ARCHITECTURE.md#4-trust-model) and the [Glossary](docs/glossary.md).

- **Trust is assigned by the recorder, from the channel a record arrived on, never by the emitter.**
  - `asserted`: a component's statement about itself (logs, self-reports).
  - `observed`: the recorder saw the bytes at an interception point it controls.
  - `verified`: checked against an independent reference.
- **Missing evidence is a Gap, not a record.** A gap names the conclusion it blocks.
- **Every claim gets exactly one status:** `supported`, `supported_by_assertion_only`, `contradicted`, or `insufficient_evidence`. There are no confidence scores.
- **Correlation comes only from explicit fields,** never from timing or proximity. Correlation is not causation.

## Intended MVP

The first release is planned as a local reference application featuring:

- A deterministic scenario runner with a scripted stub agent (no live LLM).
- A versioned JSON evidence schema.
- OpenTelemetry for execution telemetry and correlation.
- An evidence recorder and a local, append-only evidence store.
- A security investigation interface with execution timelines, event details, evidence gaps, and claims.
- Exportable evidence bundles with a SHA-256 manifest. These bundles are tamper-evident against accidental change only; they are not signed.
- Automated tests, Docker Compose configuration, and contributor documentation.

### Proposed Technology Stack

| Component | Proposed choice | Decision |
|---|---|---|
| Language | Python 3.12 | ADR-0001 |
| Evidence format | Versioned JSON; JSON Schema (draft 2020-12) is the canonical contract, pydantic mirrors it | ADR-0003 |
| Telemetry | OpenTelemetry as the correlation transport, not the evidence store | ADR-0002, ADR-0012 |
| Local storage | SQLite (append-only) plus deterministic zip bundles | ADR-0008 |
| API | FastAPI, read-only, bound to loopback | ADR-0010 |
| Investigation UI | Streamlit or a static bundle viewer | Open (OD-2) |
| Local deployment | Docker Compose | M5 |
| Testing | pytest, schema validation, golden-bundle tests | — |
| Continuous integration | GitHub Actions (ruff, mypy, pytest, secret scanning) | In place |

All ADRs are **Proposed**. A change to the schema, trust model, determinism, storage format, or a public CLI/API needs an ADR in [DECISIONS.md](DECISIONS.md) before code.

## What This Project Is Not

The initial release is not intended to be:

- A production SIEM or general-purpose observability platform.
- An agent runtime, model provider, or autonomous response engine.
- A guarantee that an agent is safe or that recorded evidence is truthful.
- A replacement for authorization enforcement, runtime security controls, or incident response.
- Dependent on a live LLM, Kubernetes, or cloud infrastructure.
- A signing or attestation system. Signed evidence is deferred (OD-3).

**Telemetry is not proof by itself.** Events may be missing, incorrectly correlated, or generated by a compromised component. The application must distinguish observed records, component assertions, independently verified evidence, and unknowns.

## Conceptual Workflow

1. Run a deterministic scenario.
2. Generate execution and security events.
3. Correlate events with an agent run and trace context.
4. Validate event structures, assign trust from the arrival channel, and record provenance.
5. Inspect execution timelines, authorization decisions, outcomes, evidence gaps, and claim statuses.
6. Export the evidence bundle and compare it with the expected scenario findings.

## Repository Documentation

- [Contributing](CONTRIBUTING.md): Contribution tracks, checks, and the definition of done.
- [Handoff](HANDOFF.md): Current state, milestones with acceptance criteria, and open questions.
- [Architecture](ARCHITECTURE.md): Components, record model, trust model, correlation, gap rules, and scenarios.
- [Constraints](CONSTRAINTS.md): The MUST/SHOULD rules for scope, determinism, evidence, and security.
- [Decisions](DECISIONS.md): Architecture decision records and their status.
- [Research](docs/research/README.md): Research write-ups and the issues they inform.
- [Glossary](docs/glossary.md): Trust levels, gaps, claims, and other shared terms.
- [Agentic Process Evidence integration](docs/integration/agentic-process-evidence.md): How to project APE session logs and process evidence into evidence records.
- [Security Policy](SECURITY.md): How to report a vulnerability privately.
- [Resources](RESOURCES.md): Standards, specifications, and related security projects.
- [FAQ](FAQ.md): Project scope, evidence trust, telemetry limitations, and contribution questions.

## Project Principles

- **Evidence before claims:** Findings must be supported by explicit evidence.
- **Make uncertainty visible:** Missing evidence is a result, not a reason to invent a conclusion.
- **Repeatability:** Scenarios must have deterministic inputs and testable expected outcomes.
- **Least data:** Use synthetic inputs by default and avoid collecting secrets or unnecessary personal data.
- **Interoperability:** Prefer documented schemas and established telemetry conventions where appropriate.
- **Security by design:** Treat evidence ingestion, storage, exports, and the investigation interface as security-sensitive components.

## Contributing

Contributions are welcome in the following areas:

- Evidence schema design and validation.
- Agent security scenarios and reproducible test cases.
- Telemetry collection and event correlation.
- Evidence provenance, integrity, and analysis.
- Research write-ups that map external standards, tools, or studies onto the evidence model.
- Investigation interface improvements.
- Automated testing and documentation.

Before starting substantial work:

1. Review the open issues and the [milestones](HANDOFF.md#2-milestones).
2. Open an issue using the matching form (bug, scenario proposal, gap-rule proposal, schema change, or research), or comment on an existing one.
3. Keep pull requests focused, include tests or reproducible evidence where applicable, and update HANDOFF.md if your change moves project state.
4. If you maintain or are affiliated with a tool, standard, or study your contribution relies on, say so in the issue or PR.
5. Never submit secrets, real customer data, or sensitive production traces.

Follow the [contribution guidelines](CONTRIBUTING.md) for current requirements.

## License

Licensed under the [Apache License 2.0](LICENSE).

## Acknowledgements

Agentic Evidence is an OWASP project. For anything not covered in the documentation, contact the Project Leader, Aamiruddin Syed (SyedDS).

Refer to the official OWASP project listing and repository metadata for current leadership, contact details, and project status. References to third-party tools and services do not imply OWASP endorsement.
