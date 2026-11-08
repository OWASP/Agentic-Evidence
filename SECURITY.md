# Security Policy

## Reporting a vulnerability

Please report vulnerabilities **privately** using GitHub's private vulnerability reporting:

**[Report a vulnerability](https://github.com/OWASP/Agentic-Evidence/security/advisories/new)**

Do not open a public issue, pull request, or discussion for an unpatched vulnerability.

Include, where possible:

- The affected file, component, or commit SHA.
- Steps to reproduce, using synthetic data only.
- The impact you believe it has.
- Any suggested fix.

Never include real secrets, credentials, production traces, or personal data in a report.

## What to expect

This is a volunteer-run OWASP incubation project, so response times are best effort.
Maintainers aim to acknowledge a report within 7 days and to agree on a disclosure timeline with the reporter.
Credit is given in the advisory unless you ask otherwise.

## Scope

In scope is the code and configuration in this repository, in particular the components treated as security-sensitive in [ARCHITECTURE.md §9](ARCHITECTURE.md#9-threat-model-of-the-tool-itself-summary):

- Evidence ingestion and schema validation (malformed or oversized records).
- The local evidence store.
- Evidence bundle export, import, and verification (path traversal, archive bombs, symlinks).
- The local API and investigation UI (injection, unescaped rendering of record content).
- CI workflows and dependency supply chain.

Also in scope, and treated as security issues: documentation, UI text, or output that **overstates what the evidence supports**.
Examples are describing a bundle as "signed" or "tamper-proof", or a scenario as "detecting" an attack, when no test demonstrates it.

Out of scope:

- Vulnerabilities in third-party dependencies that are not exploitable through this project (report those upstream).
- The scripted scenarios themselves.
  They intentionally model attacks such as retrieval poisoning and tool-descriptor modification with synthetic data.

## Supported versions

No version has been released yet.
Until the first tagged release, only the `main` branch is supported.
