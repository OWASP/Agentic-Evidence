# Resources

This page collects standards, specifications, and related work that can
inform Agentic Evidence. A resource is not automatically a dependency or
endorsement. Confirm the current version and relevance before using it
to define project requirements.

## Observability and telemetry

-   **OpenTelemetry:** https://opentelemetry.io/
    -   Traces, metrics, logs, context propagation, and semantic
        conventions.
    -   Useful for correlating execution events. OpenTelemetry
        instrumentation alone does not establish the integrity or
        completeness of evidence.
-   **OpenTelemetry specification:**
    https://opentelemetry.io/docs/specs/
    -   Protocol and SDK behavior relevant to telemetry collection and
        propagation.
-   **OTLP:** https://opentelemetry.io/docs/specs/otlp/
    -   Standard transport for telemetry data between instrumented
        components and collectors.

## AI and agent security

-   **OWASP GenAI Security Project:** https://genai.owasp.org/
    -   Security risks and guidance for generative AI applications.
-   **OWASP Top 10 for LLM Applications:**
    https://genai.owasp.org/llm-top-10/
    -   A source for relevant LLM application risk categories. Use the
        current official project page for the applicable edition.
-   **OWASP Agentic Security Initiative:** https://genai.owasp.org/
    -   Consult current OWASP publications and project pages for agentic
        AI risk taxonomies and guidance.
-   **OWASP Agentic AI Security Initiative materials:** Use the official
    OWASP project pages for current Agentic AI Top 10 and related
    publications. Avoid relying on unofficial copies when mapping
    categories.

Agentic Evidence should complement risk taxonomies and security-testing
projects by examining whether a specific execution can be reconstructed
and whether the evidence supports an investigation conclusion.

## Application security and secure development

-   **NIST Secure Software Development Framework (SSDF), SP 800-218:**
    https://csrc.nist.gov/pubs/sp/800/218/final
    -   Secure development practices relevant to project engineering,
        release processes, and supply-chain hygiene.
-   **SLSA:** https://slsa.dev/
    -   Framework for software supply-chain integrity and provenance.
        Its concepts may inform how project artifacts are built and
        released, but do not substitute for runtime evidence.
-   **CycloneDX:** https://cyclonedx.org/
    -   Software and related component bill of materials standards.
        Relevant to documenting project dependencies and build inputs.

## Identity, authorization, and policy

-   **NIST SP 800-207, Zero Trust Architecture:**
    https://csrc.nist.gov/pubs/sp/800/207/final
    -   Identity- and resource-focused access-control principles.
-   **OAuth 2.0 Security Best Current Practice, RFC 9700:**
    https://www.rfc-editor.org/rfc/rfc9700
    -   Relevant when integrations use OAuth 2.0.
-   **OpenID Connect:** https://openid.net/developers/
    -   Identity layer built on OAuth 2.0. Relevant only if a future
        implementation introduces OIDC-based identities.

These references provide context for identity and authorization. They do
not define a universal agent identity model, and the project should
document any assumptions it adopts.

## Evidence integrity and investigation design

When designing evidence bundles, consider these general requirements:

-   **Provenance:** record which component produced a claim and how it
    was collected.
-   **Correlation:** preserve stable run and trace identifiers across
    components.
-   **Integrity:** document whether records are merely logged, hashed,
    signed, or independently verified.
-   **Completeness:** identify expected event types that were not
    observed.
-   **Time:** distinguish event time from collection time and document
    clock assumptions.
-   **Minimization:** avoid storing raw prompts, secrets, personal data,
    or tool arguments when references or redacted forms suffice.
-   **Exportability:** preserve schema version and metadata so a bundle
    can be reviewed outside the UI.

A hash can help detect changes only when the comparison value is itself
trustworthy and protected. A hash alone does not prove who generated a
record or whether events were omitted.

## Related protocols and ecosystems

-   **Model Context Protocol (MCP):** https://modelcontextprotocol.io/
    -   Relevant when exploring tool discovery, tool descriptors, and
        MCP-based execution. Do not assume all agent frameworks use MCP.
-   **JSON Schema:** https://json-schema.org/
    -   Useful for defining and validating versioned evidence records.
-   **FastAPI:** https://fastapi.tiangolo.com/
    -   Proposed API framework for the MVP.
-   **pytest:** https://docs.pytest.org/
    -   Proposed testing framework.
-   **Docker Compose:** https://docs.docker.com/compose/
    -   Proposed local orchestration for a reproducible development
        environment.

## How to propose a resource

Open an issue or pull request with:

1.  The resource's official title and URL.
2.  The specific project question it helps answer.
3.  The evidence field, scenario, or engineering decision it informs.
4.  Any licensing, versioning, or maintenance concerns.

Prefer primary sources and stable specifications. Label community posts
and experimental research as secondary sources.
