# Getting Started

Welcome to **OWASP Agentic Evidence**.

This guide explains how to explore the project, prepare a local working copy, choose a contribution area, and submit research or engineering contributions.

> **Project status:** Agentic Evidence is in incubation. The initial reference implementation is being planned. The repository currently provides project documentation and research context; the MVP components and commands described in the README are planned capabilities, not necessarily runnable features. Check the repository and issue tracker before assuming a component or workflow is available.

## 1. Understand the project

Agentic Evidence investigates how to collect, correlate, validate, and assess security evidence generated during agentic AI execution.

The project asks questions such as:

- What did an agent do, and in what execution sequence?
- Which agent identity and permissions were associated with an action?
- Which inputs, retrieved content, memory, or context influenced the action?
- Which tools and external resources did the agent access?
- Which authorization and policy decisions were made?
- What evidence supports an investigation finding?
- What evidence is missing, inconsistent, or not independently verifiable?

Telemetry is useful, but a log or trace is not automatically proof. Evidence may be incomplete, incorrectly correlated, or produced by a compromised component. The project aims to make those limitations visible.

### Start with these documents

| Document | Why read it |
|---|---|
| [README](README.md) | Project scope, goals, initial scenarios, proposed MVP, and architecture direction |
| [FAQ](FAQ.md) | Clarifications about scope, evidence trust, and project terminology |
| [Resources](RESOURCES.md) | Relevant standards, specifications, and related security work |
| [Issues](https://github.com/OWASP/Agentic-Evidence/issues) | Current research questions, tasks, and implementation discussions |

## 2. Prepare your local working copy

You need:

- Git
- A GitHub account to participate in issues and pull requests
- A code editor
- A terminal or shell

No Python, Docker, database, cloud account, or live LLM is required just to read the project documentation or propose research. Runtime requirements will be documented when the MVP implementation is available.

Clone the repository:

```bash
git clone https://github.com/OWASP/Agentic-Evidence.git
cd Agentic-Evidence
```

Review the current files and project history:

```bash
git status
git log --oneline -5
ls -la
```

The repository layout may evolve as the project moves from research and planning into implementation. Consult the current README and issue tracker rather than relying on an assumed directory structure.

## 3. Choose how you want to contribute

Contributions are welcome from security researchers, AI engineers, application security practitioners, observability engineers, identity specialists, digital forensics practitioners, developers, and technical writers.

### Research and evidence modelling

Possible contributions:

- Identify the evidence needed to investigate a specific agentic AI threat.
- Propose evidence categories, required fields, and relationships.
- Define evidence provenance and source attribution requirements.
- Examine how to represent missing, conflicting, or unverifiable evidence.
- Map relevant standards and existing telemetry conventions.
- Document assumptions, limitations, and open research questions.

A useful research submission states the question, scope, methodology, supporting references, findings, limitations, and suggested next steps.

### Security scenarios and test cases

The initial scenarios are:

1. **Benign execution:** Establish a baseline for a normal agent workflow.
2. **Retrieval poisoning:** Examine whether retrieved content and its influence on a subsequent agent action can be reconstructed from available evidence.
3. **Tool descriptor modification:** Examine whether evidence can identify the tool descriptor observed or used during execution and whether a modification can be established.

Contributors can propose additional scenarios involving identity misuse, authorization failures, tool misuse, context manipulation, memory integrity, evidence tampering, or incomplete event capture.

A scenario proposal should include:

- Threat or security question
- Preconditions and assumptions
- Actors and system components
- Deterministic steps to reproduce
- Expected events and evidence
- Expected findings and known limitations
- Tests that distinguish observed facts from assumptions

Scenarios should use synthetic data and deterministic inputs wherever possible. Do not claim that a scenario is detectable until an implementation and repeatable test support that claim.

### Engineering and implementation

Potential engineering areas include:

- Versioned JSON evidence schemas and JSON Schema validation
- Agent execution instrumentation and OpenTelemetry correlation
- Evidence recording and local storage
- Identity, tool invocation, retrieval, and authorization event modelling
- Evidence provenance and integrity checks
- Investigation timelines and evidence-gap presentation
- Portable evidence export and validation
- Automated tests and continuous integration

The README describes a proposed technology direction, including Python/FastAPI or Go, JSON Schema, OpenTelemetry, SQLite or JSON fixtures, a lightweight investigation UI, Docker Compose, pytest, and GitHub Actions. These are proposals, not fixed prerequisites. Check current project decisions and open issues before selecting a technology or introducing a dependency.

### Documentation and community support

You can also contribute by:

- Improving setup and architecture documentation
- Reviewing research proposals for clarity and reproducibility
- Adding diagrams and examples
- Reviewing terminology and evidence definitions
- Reporting documentation gaps
- Helping new contributors understand an issue or research task

## 4. Find or propose a task

Before starting substantial work:

1. Search the [existing issues](https://github.com/OWASP/Agentic-Evidence/issues) for related work.
2. Read the relevant project documentation.
3. For a new idea, open an issue describing the problem, research question, or proposed change.
4. Explain the expected outcome and how it could be reviewed or tested.
5. Wait for project discussion on substantial architectural or scope changes before investing in a large implementation.

When selecting an issue, clarify its status and scope with the maintainers. Do not assume that an idea in the README is already an approved implementation task.

## 5. Create a branch and submit a contribution

For a focused documentation or code change, create a branch:

```bash
git checkout -b docs/short-description
```

For a research or implementation contribution, choose a branch name that reflects the work, for example:

```bash
git checkout -b research/evidence-provenance
git checkout -b feature/evidence-schema-validation
git checkout -b test/retrieval-poisoning-scenario
```

Make a focused change. Include supporting references, tests, fixtures, or reproduction steps where applicable.

Review your changes:

```bash
git diff --check
git diff
git status
```

Commit and push your branch:

```bash
git add <files>
git commit -m "docs: describe evidence provenance requirements"
git push -u origin HEAD
```

Open a pull request against the repository's default branch. In the pull request description:

- Explain the problem or research question.
- Summarize the change and its scope.
- Link the related issue or discussion.
- Describe how reviewers can validate the result.
- Include test results or reproduction steps where applicable.
- State limitations, assumptions, and follow-up work.

Follow any repository contribution instructions and review feedback. Keep pull requests small enough to review effectively.

## 6. Evidence quality expectations

Research findings and implementation claims should be reviewable by another contributor.

Where relevant, include:

- **Source:** Where the evidence originated.
- **Collection context:** When and how it was collected, and by which component.
- **Correlation:** The run, trace, agent, action, or resource identifiers used to connect records.
- **Integrity:** Any hash, signature, validation result, or other integrity mechanism applied.
- **Provenance:** Whether a record is directly observed, asserted by a component, or independently verified.
- **Completeness:** Known missing events, unavailable fields, and collection boundaries.
- **Limitations:** What the evidence does not establish.

Do not treat an OpenTelemetry span, application log, agent-generated explanation, or tool response as independently verified proof by default. State what the record demonstrates and what remains uncertain.

## 7. Security and data handling

This is a security research project. Contributions must not introduce avoidable risk.

- Use synthetic data for examples, tests, and demonstrations.
- Never commit credentials, API keys, access tokens, private keys, or secrets.
- Do not submit customer data, personal data, or sensitive production traces.
- Sanitize logs, fixtures, screenshots, and exported evidence bundles before sharing.
- Do not run untrusted scenarios or code against production systems.
- Document security assumptions and trust boundaries.
- Treat evidence ingestion, storage, export, and display as security-sensitive.
- Report suspected vulnerabilities privately through the repository's published security reporting process rather than disclosing exploitable details in a public issue.

## 8. What to expect from the MVP

The planned MVP is intended to provide a local reference workflow:

1. Run a deterministic agent security scenario.
2. Generate execution and security events.
3. Correlate events with an agent run and trace context.
4. Validate event structures and record provenance.
5. Inspect execution timelines, authorization decisions, outcomes, and evidence gaps.
6. Export an evidence bundle for review.

The planned components include a scenario runner, versioned evidence schema, OpenTelemetry instrumentation, evidence recorder and local store, investigation interface, export capability, and automated tests.

**These are target capabilities, not installation instructions.** Once the implementation is available, this guide should be updated with verified prerequisites, exact setup commands, supported versions, sample scenarios, expected outputs, and troubleshooting steps.

## 9. Stay involved

- [GitHub repository](https://github.com/OWASP/Agentic-Evidence)
- [Issues and research discussions](https://github.com/OWASP/Agentic-Evidence/issues)
- [Pull requests](https://github.com/OWASP/Agentic-Evidence/pulls)

Contributions should be technically grounded, reproducible where possible, and explicit about uncertainty. The objective is not simply to collect more telemetry. It is to help investigators determine what the available evidence supports, what it does not support, and where important gaps remain.

---

*OWASP Agentic Evidence is an open-source community project. Project scope, implementation choices, and contribution guidance may evolve. The repository's current documentation and maintainer decisions are authoritative.*
