
# Contributing to OWASP Agentic Evidence

Thanks for helping.

This project answers one question honestly:

*Given the records we have, what can an investigator actually conclude about this agent run, and what can't they?*

Contributions are judged by whether they make that answer more accurate, never by whether they make the tool look more capable.

## Start Here

| Read | Why |
|---|---|
| [README.md](README.md) | Scope, goals, and the three initial scenarios |
| [FAQ.md](FAQ.md) | What the project does and doesn't claim |
| [docs/glossary.md](docs/glossary.md) | Trust levels, gaps, claims, and other shared terms |
| [HANDOFF.md](HANDOFF.md) | Current milestone, acceptance criteria, and open questions |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Data model, trust model, gap rules, and scenarios |
| [RESOURCES.md](RESOURCES.md) | Standards and related work |

You don't need Python, Docker, or any account other than GitHub to read the docs, propose a scenario, or contribute research.

Nothing runnable beyond the CI checks exists yet; HANDOFF.md says what is implemented.

## Community and Communication

We welcome security researchers, developers, architects, AI security practitioners, and community members interested in contributing to OWASP Agentic Evidence.

**Join the OWASP Slack project channel:**

[Join #project-agentic-evidence](https://owasp.slack.com/archives/C0CBV145CKB)

Use the Slack channel to:

- Introduce yourself and share your areas of interest.
- Discuss research questions and emerging security challenges.
- Propose new scenarios, evidence models, and gap rules.
- Collaborate with other contributors.
- Ask questions about project scope, architecture, and contribution opportunities.
- Share relevant standards, publications, tools, and technical resources.
- Coordinate research and implementation activities.

**GitHub remains the project's single source of truth.**

Use Slack for discussions and collaboration, GitHub Issues for tracking work, and Pull Requests for submitting changes. Important technical decisions and accepted proposals must be documented in the repository.

## Ground Rules

These apply to every contribution, including docs and issue text.

The full list is in [AGENTS.md](AGENTS.md) and [CONSTRAINTS.md](CONSTRAINTS.md).

1. **Don't overclaim.**

   Don't write that an attack is "detected", "prevented", or "proven" unless a scenario test demonstrates exactly that.

   Prefer "the evidence supports / does not support claim X".

2. **Gaps are results.**

   If a conclusion needs a record that isn't there, the correct output is a gap.

   Never infer, default, or backfill the missing value.

3. **Trust is assigned, not declared.**

   A component's log about itself is `asserted`.

   Only the mechanisms in [ARCHITECTURE.md §4](ARCHITECTURE.md#4-trust-model) produce `observed` or `verified`.

4. **Determinism.**

   No wall-clock time, random IDs, network, or live LLM in anything a scenario reaches.

5. **Synthetic data only.**

   Use `example.com` / `.test` / `.invalid` domains and RFC 5737 IPs.

   Never commit or paste secrets, real prompts, production traces, or personal data.

## How to Contribute

1. **Find or open an issue.**

   Use the issue form that matches your work (see the tracks below).

   For anything beyond a typo, wait for a maintainer to confirm scope before investing heavily.

2. **Check whether it needs an ADR.**

   A change to the schema, trust model, determinism, storage format, or a public CLI/API needs an ADR in [DECISIONS.md](DECISIONS.md) with status `Proposed` **before** code.

3. **Branch** from `main` with a descriptive name, for example `docs/glossary-influence`, `scenario/s2-authz-missing`, or `feat/recorder-limits`.

4. **Make a focused change**, with tests first for anything in `analyze/`.

5. **Run the checks** (see below).

6. **Update [HANDOFF.md](HANDOFF.md)** if your change moves project state.

   A PR that changes state without updating HANDOFF is incomplete.

7. **Open a PR** and fill in the template.

## Contribution Tracks

Each kind of work has a fixed shape and a clear definition of done.

You don't need to write Python to contribute.

Scenario specs and research are as valuable as code.

| Track | Issue form | What you deliver | Done when |
|---|---|---|---|
| Scenario | Scenario proposal | `scenarios/sN-name/` with `scenario.yaml`, fixtures, and `expected.yaml` | Fixtures validate, every expected gap and claim cites records by ID, and at least one variant has insufficient evidence |
| Gap rule | Gap rule proposal | A `G-AREA-NNN` rule plus an entry in ARCHITECTURE §6 | Tests cover fires / doesn't fire / present-but-only-asserted (if trust matters) |
| Schema | Schema change request | ADR, then a schema PR with fixtures | ADR is accepted and existing fixtures still validate or are migrated |
| Research | Research question | A write-up in `docs/research/` | It states question, method, sources, findings, and limitations, and links the schema or scenario issues it informs |
| Docs | Bug report or any form | Any page | It makes no claim about functionality that doesn't exist yet |
| Bug | Bug report | Fix plus a regression test | The test fails before the fix and passes after |

Some directories in this table (`scenarios/`, `schemas/`, `docs/research/`) don't exist yet.

They are created by the milestone that needs them, not ahead of it.

## Evidence Quality Expectations

Research findings and implementation claims must be reviewable by another contributor.

Where relevant, state:

- **Source:** where the evidence originated.
- **Collection context:** when and how it was collected, and by which component.
- **Correlation:** the run, trace, agent, action, or resource identifiers used to connect records.
- **Integrity:** any digest, signature, or validation applied, and what it does not establish.
- **Provenance:** whether a record is `observed`, `asserted`, or `verified`.
- **Completeness:** known missing events, unavailable fields, and collection boundaries.
- **Limitations:** what the evidence does not establish.

An OpenTelemetry span, application log, agent-generated explanation, or tool response is not independently verified proof by default.

## Local Setup and Checks

Prerequisites: Git and [uv](https://docs.astral.sh/uv/).

uv installs the pinned Python version (3.12) for you.

```bash
make setup    # uv sync --frozen
make lint     # ruff check, ruff format --check, mypy --strict
make test     # pytest
make check    # lint + test
```

Without `make` (for example on Windows), run the commands from the [Makefile](Makefile) directly, for example `uv run ruff check`.

CI runs the same checks on Ubuntu and macOS, plus a secret scan, on every pull request.

## Code Conventions

- Python 3.12, `src/` layout, type hints everywhere, `mypy --strict` on `src/`.
- `ruff` for lint and formatting.
- New files carry `SPDX-License-Identifier: Apache-2.0` where the format allows comments.
- No new runtime dependency without a justification in the PR.
  A structural dependency also needs an entry in DECISIONS.md.
- Record content is attacker-controlled.

  Never render it as HTML/Markdown, or pass it to an interpreter, template engine, shell, or LLM.

## Labels

| Label | Meaning |
|---|---|
| `needs-triage` | New; a maintainer hasn't looked yet |
| `good-first-issue` | Small, well-scoped, with pointers to the relevant files |
| `help-wanted` | Maintainers would welcome an external contributor |
| `research` | Literature, standards, or modelling question |
| `scenario` | Scenario or variant work |
| `gap-rule` | New or changed G-* rule |
| `schema` | Evidence schema change |
| `needs-adr` | Can't proceed until an ADR is proposed and reviewed |
| `bug` | Something is broken or wrong |
| `overclaim` | Docs, UI, or output that claims more than the evidence supports (high priority) |

## Data Handling

- Sanitize logs, fixtures, screenshots, and exported evidence bundles before sharing them anywhere.
- Never run scenarios or untrusted code against production systems.
- Document the security assumptions and trust boundaries your change relies on.

## Security Issues

Do not open public issues for vulnerabilities.

Follow [SECURITY.md](SECURITY.md).

## Code of Conduct

This project follows the [OWASP Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions are licensed under the [Apache License 2.0](LICENSE).
