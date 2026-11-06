# AGENTS.md — OWASP Agentic Evidence

This file defines repository-wide instructions for AI coding agents working on OWASP Agentic Evidence. Read and follow any more specific `AGENTS.md` in the directory being changed. More specific instructions may add constraints but must not weaken the security, evidence-quality, or validation requirements here.

## 1. Project mission and status

OWASP Agentic Evidence is an open-source research and engineering project exploring how to collect, correlate, validate, and investigate security evidence from agentic AI execution.

The project focuses on:
- Reconstructing agent execution across identities, context, retrieval, tools, authorization decisions, and outcomes.
- Recording evidence provenance and collection context.
- Evaluating evidence integrity, completeness, correlation, and trust limitations.
- Making missing, conflicting, or unverifiable evidence visible.
- Providing deterministic, reproducible security scenarios and a local reference workflow.

**Status:** The project is in incubation. Treat the README, accepted issues, merged code, and maintainer decisions as sources of truth. Some components and technology choices described in project documentation are proposed or planned. Do not represent planned functionality as implemented. Do not invent setup commands, APIs, data models, or runtime behavior.

Before making a change, inspect the current repository and relevant history. Do not assume a proposed MVP component exists.

## 2. Core engineering principles

1. **Evidence before claims.** Every security finding must be traceable to explicit records, test results, or cited sources.
2. **Make uncertainty visible.** Missing or conflicting evidence is a result. Never fill gaps with invented events or inferred facts presented as observations.
3. **Separate observation from interpretation.** Preserve observations separately from derived findings and analyst conclusions.
4. **Provenance by design.** Record the source and collection context for evidence. Do not silently discard provenance during transformations.
5. **Integrity is not truth.** A hash or signature may help detect modification or identify a signer. It does not by itself prove that an event occurred, that the emitter was uncompromised, or that the record is complete.
6. **Correlation is not causation.** Related timestamps, trace IDs, or event IDs do not by themselves prove that one event caused another.
7. **Repeatability.** Prefer deterministic scenarios, synthetic fixtures, explicit expected outcomes, and reproducible tests.
8. **Least data.** Use synthetic data by default. Avoid storing secrets, personal data, customer content, or full prompts unless a reviewed use case requires them.
9. **Interoperability.** Prefer documented formats and established conventions, including OpenTelemetry where appropriate. Do not force a standard where it does not fit the evidence requirement.
10. **Small, reviewable changes.** Keep pull requests focused and explain security and compatibility implications.

## 3. Required workflow before editing

For every task:

1. Read this file and any more specific `AGENTS.md` files in the target directory.
2. Read the relevant README, contributor guidance, design decisions, and issue discussion.
3. Inspect the repository tree and current implementation. Use code and tests as the authority for current behavior.
4. Identify the smallest change that satisfies the request.
5. Check whether the change affects evidence semantics, schema compatibility, privacy, security boundaries, or exported formats.
6. If requirements are ambiguous or conflict with current behavior, document the ambiguity and ask for clarification rather than inventing a contract.
7. For significant architecture, schema, dependency, or interface changes, discuss the proposal in an issue before implementation unless maintainers have approved it.

Do not create speculative folders, services, APIs, database tables, MCP integrations, or abstractions merely because they appear in a roadmap.

## 4. Repository and technology discovery

The proposed MVP has discussed Python/FastAPI or Go, versioned JSON/JSON Schema, OpenTelemetry, local storage, a lightweight investigation interface, Docker Compose, automated tests, and GitHub Actions. These are not all mandatory or necessarily implemented.

Before running checks, discover the actual project tooling:

- Python: `pyproject.toml`, `requirements*.txt`, `tox.ini`, `pytest.ini`, `ruff.toml`, `.python-version`.
- JavaScript/TypeScript: `package.json`, lockfiles, `tsconfig*.json`, ESLint configuration.
- Go: `go.mod`, `go.work`, `Makefile`.
- Rust: `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`.
- Containers: `Dockerfile`, `compose.yaml`, `docker-compose.yml`.
- CI: `.github/workflows/`.
- Task runners: `Makefile`, `justfile`, `Taskfile.yml`, project scripts.

Prefer commands already documented by the repository, declared in package scripts, or used by CI. Do not add a toolchain just to satisfy this generic instruction. Do not run commands for a language or component that is not present.

## 5. Evidence model and schema rules

When working on evidence records, schemas, or event transformations:

- Use explicit schema versions. Do not silently change the meaning of an existing version.
- Define required, optional, nullable, and unknown fields distinctly.
- Use stable identifiers for runs, events, agents, tools, resources, and correlation references where applicable.
- Preserve source attribution, collection time, event time when available, collector identity, and relevant version information.
- Define timestamp format and timezone semantics. Do not assume clocks are perfectly synchronized.
- Represent unavailable or unobserved information as unavailable. Do not substitute fabricated values.
- Keep raw source references or immutable input fixtures where feasible and privacy-safe.
- Document normalization and transformation steps.
- Validate examples and fixtures against the authoritative schema.
- Add compatibility tests when changing a published schema.
- Avoid embedding secrets, full sensitive prompts, or unnecessary retrieved content in evidence records.

Do not label evidence as "verified" unless a defined verification procedure has been applied and its result recorded. Distinguish, where relevant:

- **Observed:** a collector received or recorded a value.
- **Asserted:** a component claims an event or decision occurred.
- **Corroborated:** separate records support a consistent account.
- **Verified:** a defined procedure validates a specific property.

These labels describe evidence properties. They are not a universal legal admissibility classification.

## 6. Security and privacy requirements

Treat evidence ingestion, processing, storage, display, and export as security-sensitive.

- Never commit credentials, API keys, access tokens, private keys, passwords, or production secrets.
- Never use real customer data or sensitive production traces in tests, examples, screenshots, or demos.
- Use synthetic fixtures and deterministic test inputs.
- Redact or minimize sensitive values before logging or exporting.
- Do not execute attack scenarios against systems without explicit authorization.
- Validate untrusted input at system boundaries.
- Apply least privilege to file access, network access, credentials, and tool execution.
- Avoid unsafe deserialization, shell injection, path traversal, SSRF, and uncontrolled file writes.
- Set reasonable limits for payload sizes, recursion, event counts, and export sizes.
- Handle malformed, incomplete, duplicate, out-of-order, and conflicting events safely.
- Do not silently swallow validation or integrity errors.
- Do not expose stack traces, secrets, internal paths, or sensitive evidence to unauthorized users.
- Ensure exported bundles do not accidentally include credentials, environment files, local databases, or unrelated files.

For suspected vulnerabilities, follow the project's published private reporting process. Do not put exploitable details in a public issue.

## 7. Feature development

For each feature:

1. State the problem and intended security or research outcome.
2. Identify evidence inputs, outputs, trust boundaries, and failure modes.
3. Define expected behavior for valid, invalid, missing, conflicting, and adversarial inputs.
4. Add or update tests before or alongside implementation.
5. Keep interfaces and dependencies as small as practical.
6. Update documentation and examples when behavior or configuration changes.
7. Consider backwards compatibility for schemas, APIs, fixtures, and exported bundles.
8. Record limitations. Do not claim detection, prevention, provenance, or verification beyond what tests demonstrate.

Do not add a live LLM, cloud dependency, external API, MCP server, or agent framework unless the task requires it and the dependency has been reviewed. Deterministic local tests should not require network access.

## 8. MCP and external integrations

MCP support and other integrations are not assumed to exist. Implement them only when an approved issue or design requires them.

For any MCP or external-tool integration:

- Treat tool descriptions, schemas, responses, and retrieved content as untrusted input.
- Record tool identity and descriptor/version or digest when available.
- Separate tool selection, authorization decision, invocation, and result events.
- Do not treat a tool's own response as independent proof of its behavior.
- Enforce explicit timeouts, payload limits, and error handling.
- Avoid forwarding credentials or sensitive context unless required and authorized.
- Test descriptor changes, malformed responses, timeouts, denied actions, and tool errors.
- Document transport, authentication, trust assumptions, and data handling.
- Never add a tool invocation path that bypasses the application's authorization boundary.

## 9. Testing and validation requirements

### 9.1 Validation policy

The repository's actual CI configuration and project manifests are authoritative. Inspect them and use the same commands locally.

The following are **conditional command mappings**, not claims that every tool is installed or every language is used. Run a command only when project files, configuration, or CI establish that it applies. If a required tool is missing, report that fact. Do not claim a skipped check passed.

| Detected tooling | Required validation |
|---|---|
| Python tests using pytest | `python -m pytest` |
| Ruff configured | `ruff check .` |
| Ruff formatter configured | `ruff format --check .` |
| mypy configured | `mypy .` |
| Pyright configured | `pyright` |
| JSON Schema/evidence fixtures | Run the repository's schema validator or schema tests. If none exists, add focused validation tests using the declared validator. |
| JavaScript/TypeScript package scripts | Run declared scripts, normally `npm run lint`, `npm run typecheck`, and `npm test` when those scripts exist. |
| ESLint configured without package scripts | `npx eslint .` only if ESLint and its configuration are present. |
| TypeScript with `tsconfig.json` | `npx tsc --noEmit` only if TypeScript is present. |
| Go module | `go test ./...` and `go vet ./...` |
| golangci-lint configured | `golangci-lint run` |
| Rust crate/workspace | `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings`, and `cargo test --all-targets` |
| Docker Compose file | `docker compose config` when Docker Compose is available. |
| Markdown lint configured | Run the repository's declared Markdown lint command, e.g. `npx markdownlint-cli2 "**/*.md"` only if that dependency and configuration exist. |

Do not run Python, Node, Go, or Rust commands just because they appear in this table. Do not introduce `cargo clippy`, ESLint, Ruff, mypy, or another tool into a project that does not use that ecosystem.

### 9.2 Minimum checks for every change

Before hand-off:

- Inspect `git diff --check`.
- Review `git diff` for unintended changes, generated files, secrets, and unrelated edits.
- Run all applicable tests for the changed component.
- Run applicable lint, formatting, and type checks configured by the repository.
- Validate changed JSON, YAML, and JSON Schema files with configured validators.
- Update or add tests for changed behavior.
- Check that documentation examples and commands match the current implementation.
- Report any checks that could not be run and why.

For documentation-only changes, run Markdown lint/link checks if configured, inspect rendered Markdown where practical, and verify local relative links and code examples. Do not run unrelated application test suites unless the documentation change affects them.

### 9.3 Evidence-specific test cases

Where relevant, tests should cover:

- Valid and invalid schema versions.
- Missing required fields and unknown optional fields.
- Duplicate events and identifiers.
- Out-of-order events and timestamp edge cases.
- Broken or mismatched correlation identifiers.
- Unknown identity, tool, or resource references.
- Missing provenance and incomplete collection.
- Conflicting records from separate sources.
- Modified records and failed integrity checks.
- Redaction and secret exclusion.
- Export/import round trips and bundle validation.
- Deterministic scenario outputs.

Tests must assert what the implementation can establish. Do not assert that correlation proves causation or that a valid signature proves an event was truthful.

## 10. Self-validation procedure

Use this sequence for every code hand-off:

1. **Discover:** Inspect manifests, scripts, Makefiles, and CI workflows.
2. **Select:** Identify the exact test, lint, formatter, and type-check commands used by this repository.
3. **Run targeted checks:** Run checks for the changed package or component.
4. **Run broader checks:** Run the full applicable suite and CI-equivalent checks when practical.
5. **Inspect results:** Review exit codes and relevant output. Investigate failures; do not hide or suppress them.
6. **Review diff:** Run `git diff --check`, inspect `git status`, and review the final diff.
7. **Report:** State exactly what ran, passed, failed, and was skipped.

If the repository has a documented CI command or `make check` equivalent, prefer it for the full validation pass. Do not assume such a target exists.

Never:
- Claim tests passed when they were not run.
- Replace a failing test with a weaker assertion merely to obtain a green result.
- Skip a failing check without disclosing it.
- Modify CI to suppress failures without an approved reason.
- Use network-dependent tests as a substitute for deterministic local tests.

## 11. Documentation expectations

Update relevant documentation when a change affects setup, architecture, evidence schema, API behavior, configuration, security assumptions, scenario execution, test commands, or project status.

- Keep `README.md` concise and user-facing.
- Use `GETTING_STARTED.md` for setup and first contribution guidance.
- Use `CONTRIBUTING.md` for the human contribution process.
- Use this `AGENTS.md` for AI-agent engineering instructions.
- Mark proposed capabilities as planned and implemented capabilities as implemented.
- Include exact setup and validation commands only after verifying them against the current repository.

Do not create `CLAUDE.md`, `SKILL.md`, `MEMORY.md`, `PLAN.md`, `DESIGN.md`, `DATABASE.md`, or `API.md` unless a concrete project need justifies the additional document. If a durable design decision is needed, propose a focused architecture decision record or narrowly scoped document rather than duplicating this file.

## 12. Git and pull request expectations

- Keep each change focused and use descriptive branch and commit messages.
- Do not rewrite shared history or force-push unless explicitly requested by maintainers.
- Do not commit build output, caches, virtual environments, local databases, credentials, or generated evidence bundles unless explicitly required.
- Include tests and reproducible steps in pull requests.
- Link the related issue or design discussion.
- Describe schema/API compatibility impact and security implications.
- Include limitations and follow-up work.
- Do not claim a scenario is detected or mitigated unless tests substantiate that claim.

## 13. Required hand-off report

At the end of a task, provide a concise report with:

1. **Changes:** Files and behavior changed.
2. **Validation:** Exact commands run and their results.
3. **Not run:** Applicable checks skipped, with reasons.
4. **Security considerations:** Relevant privacy, trust, and attack-surface implications.
5. **Limitations:** Known gaps, assumptions, and follow-up work.

A change is not ready for hand-off merely because the code compiles. It must also meet the evidence-quality, security, documentation, and validation requirements above.
