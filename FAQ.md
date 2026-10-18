# Frequently Asked Questions

## What is Agentic Evidence?

Agentic Evidence is an OWASP open-source reference project for
collecting, correlating, and evaluating security evidence from agentic
AI execution. It focuses on reconstructing actions and determining what
the evidence supports an investigator concluding.

## What problem does it solve?

Agent logs and traces can show that events were recorded, but may not
establish which identity authorized an action, what input influenced it,
which tool descriptor was used, or whether relevant records are missing
or untrustworthy. The project explores these evidence gaps through
reproducible scenarios.

## How is this different from an observability dashboard?

A conventional observability dashboard primarily helps operators
understand system behavior and performance. Agentic Evidence adds a
security-investigation perspective: evidence provenance, authorization
context, cross-event correlation, expected-versus-observed evidence, and
explicit limits on what can be concluded.

It builds on established telemetry where appropriate. It does not claim
that telemetry alone proves an action was trustworthy.

## Is this a production-ready security product?

No. The initial deliverable is a local reference implementation for
learning, experimentation, and repeatable demonstrations. Production
deployment, high availability, access controls for multi-user
environments, retention controls, and integrations require separate
design and validation.

## Does it prevent agent attacks?

Not by itself. The initial focus is evidence collection and
investigation, not enforcement or automatic remediation. Authorization
controls and runtime defenses must be implemented by the system that
executes the agent.

## Does it use a live LLM?

The initial scenarios are intended to be deterministic and
fixture-driven. A live model should not be required to reproduce the
baseline, retrieval-poisoning, or tool-descriptor-modification
scenarios. Future integrations may be considered after the evidence
model and core tests are stable.

## What scenarios are planned first?

1.  Benign execution to establish a baseline.
2.  Retrieval poisoning to examine whether retrieved content and
    subsequent actions can be correlated.
3.  Tool-descriptor modification to examine descriptor identity,
    versioning, integrity, and provenance evidence.

These are controlled demonstrations, not claims of comprehensive attack
coverage.

## What does the project mean by evidence?

Evidence is a record or artifact used to support or challenge a claim
about an execution. Examples include a tool invocation event, a policy
decision, a trace span, a descriptor hash, or a provenance statement.

Evidence has different levels of trust. A component-generated log is an
assertion from that component unless there is a separate mechanism to
validate it.

## Does a trace prove what the agent actually did?

No. A trace reflects what instrumented components emitted and what the
collection pipeline retained. A compromised or faulty component may emit
false events, omit events, or use incorrect identifiers. The project
should expose those limitations instead of treating trace presence as
proof.

## Does a hash prove that a tool descriptor is trustworthy?

No. A hash can help identify whether bytes differ from a known value. It
does not prove who produced the descriptor, whether the reference hash
is trustworthy, whether the descriptor was actually used, or whether
relevant events were omitted. Stronger conclusions require trustworthy
reference values and appropriate provenance or verification mechanisms.

## What is an evidence gap?

An evidence gap is a missing or insufficient record needed to support a
security conclusion. Examples include a tool invocation without a
correlated authorization decision, a descriptor without a known version,
or an execution timeline with missing events. A gap should be reported
explicitly rather than silently filled with an assumption.

## Does the project replace OWASP agent-security taxonomies or testing projects?

No. The intended role is complementary. Taxonomies describe risks and
testing projects exercise security properties. Agentic Evidence focuses
on the evidence available to reconstruct execution and evaluate
investigation claims.

## What technology does it use?

The proposed baseline is Python/FastAPI, versioned JSON and JSON Schema,
OpenTelemetry, local SQLite or JSON fixtures, a lightweight
investigation UI, Docker Compose, pytest, and GitHub Actions. These
choices may change through documented architecture decisions as the
implementation develops.

## Does it require Kubernetes, cloud infrastructure, or credentials?

The initial local MVP is intended to run with Docker Compose and
synthetic data. It should not require Kubernetes, a cloud account, or a
live model API key.

## Can I use production logs or customer data?

Do not submit sensitive production traces, credentials, secrets,
customer data, or personal data to public issues or pull requests. Use
synthetic fixtures or properly sanitized data. Follow your
organization's data-handling requirements.

## How can I contribute?

Start by checking the roadmap and open issues. Useful contributions
include evidence-schema design, deterministic scenarios, telemetry
correlation, UI improvements, test cases, documentation, and independent
validation. Discuss substantial changes in an issue before opening a
pull request.

## How should I report a security vulnerability in the project?

Use the private reporting method documented in the repository's
`SECURITY.md`, once published. Do not disclose an unpatched
vulnerability in a public issue.

## What is the license?

The project is intended to use Apache License 2.0. The repository's
published `LICENSE` file is authoritative. Check it before
redistributing code.

## Where can I find the latest project status?

Use the official OWASP project listing and repository milestones,
issues, and release notes. This documentation describes the intended MVP
and should not be treated as proof that a planned feature has already
shipped.
