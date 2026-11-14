<!-- SPDX-License-Identifier: Apache-2.0 -->

# MCP tool approval binding and invocation digest provenance

**Status:** Research write-up, input for v0.2.
Nothing here is a decision or an implemented capability.
The field and scenario shapes are sketches for a later ADR and scenario proposal.

**Informs:** [#5](https://github.com/OWASP/Agentic-Evidence/issues/5) (points 2 and 3), [#6](https://github.com/OWASP/Agentic-Evidence/issues/6) (claim-status derivation), the planned S2/S3 specs issue, and the post-v0.1 "MCP tool rug-pull" candidate in [HANDOFF.md](../../HANDOFF.md#after-v01-candidates-not-committed).
**Related:** [#4](https://github.com/OWASP/Agentic-Evidence/issues/4) (which bytes `descriptor_digest` covers), [#2](https://github.com/OWASP/Agentic-Evidence/issues/2) (authorization, dispatch and outcome), [#1](https://github.com/OWASP/Agentic-Evidence/issues/1) (joint topic on descriptor modification; §3.1 and §3.3 are offered there as client-side input).

**Disclosure:** independent researcher; author of the preprint and harness cited in [§8](#8-prior-data-motivation-only); contributed to OWASP AISVS 10.4.7, 10.4.8 and 10.4.22.

"AR §n" below means a section of [ARCHITECTURE.md](../../ARCHITECTURE.md); a bare "§n" is a section of this write-up.

## 1. Questions

The case: an MCP server lists tool definition A, the user approves A, A is invoked, the server changes the tool to B, the client fetches the list again, and B is invoked.

- **Q1, approval binding.** What would a record need to carry to show which tool definition a user approved, who approved it, when, and for what scope?
  Which evidence channel can carry it, and at what trust level?
- **Q2, digest provenance.** When a `tool.invocation` record carries a `descriptor_digest`, where can that digest come from, and what trust can each source get under [AR §4](../../ARCHITECTURE.md#4-trust-model) and [AR §5](../../ARCHITECTURE.md#5-correlation)?

Out of scope: which bytes the digest covers (#4), and whether the call was authorized, dispatched or had an effect (#2).
Point 2(a) of #5 (pin sources) is answered only as far as §3.2: an approval cannot be a pin source. Other MCP pin sources are not surveyed.

## 2. Method and sources

1. **Protocol reading.** The tools pages of the MCP specification, revisions [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) and [2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), with the 2026-07-28 [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [subscriptions](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/subscriptions) and [caching](https://modelcontextprotocol.io/specification/2026-07-28/server/utilities/caching) pages.
   For each message: what it carries, and which party sees it.
2. **Record walk-through** against the v0.1 record kinds ([AR §3.2](../../ARCHITECTURE.md#32-record-kinds-v01)), trust, correlation and gap rules ([AR §6](../../ARCHITECTURE.md#6-gap-rules-v01)).
3. **Requirements cross-check.** OWASP AISVS 10.4.7, 10.4.8 and 10.4.22: an approval bound to the approved tool definition, a new approval after a change, and an approval bound to the server launch configuration ([OWASP/AISVS#1204](https://github.com/OWASP/AISVS/pull/1204), [OWASP/AISVS#1218](https://github.com/OWASP/AISVS/pull/1218)).

No code was written and no live MCP integration was used.

## 3. Findings

### 3.1 Who sees what

| Step | Protocol message | On the client–server wire | Only inside the host |
|---|---|---|---|
| 1. List A | `tools/list` result with definition A | yes | |
| 2. Approve A | none for host approval | no | prompt, answer, scope |
| 3. Invoke A | `tools/call` | yes | which definition the client held |
| 4. Change to B | `notifications/tools/list_changed`, if sent and deliverable | if sent | |
| 5. List B | `tools/list` result with definition B | yes | |
| 6. Invoke B | `tools/call` with the same `name` | yes | which definition the client held; whether it asked again |

Three protocol facts shape the rest:

- `tools/call` carries the name, the arguments and `_meta` (2025-11-25 adds an optional `task`; 2026-07-28 adds `inputResponses`/`requestState`, and on Streamable HTTP the `Mcp-Name` header and any `Mcp-Param-*` headers mirroring arguments). None of these refers to the definition, a version of it or a digest of it. A client digest placed in `_meta` would still be the client's assertion.
- Host approval is not a protocol message ("there SHOULD always be a human in the loop"; the interaction model is left to the application). Server elicitation (an `InputRequiredResult` in 2026-07-28) is visible on the wire, but it is asked by the party being checked and names no client-held definition.
- Step 4 may leave no trace. `list_changed` is a SHOULD and needs an open channel: in 2025-11-25, stdio or the optional Streamable HTTP GET stream; in 2026-07-28, a `subscriptions/listen` stream with `toolsListChanged: true` that the server acknowledged. A 2026-07-28 client may also learn of a change only when its cached list expires (`ttlMs`).

### 3.2 Q1: approval arrives as `asserted`

Unless the recorder has an interception point inside the host's approval path (v0.1 defines none, and assumes no recorder placement inside a real host), any record of step 2 is a component's statement about itself.
Under AR §4 it arrives on the `self-report` channel and the recorder assigns `asserted`.
Nothing in v0.1 raises it:

- A client–server tap never sees the host approval.
- In v0.1 `reference.pin` is emitted only by a scenario fixture (AR §3.2), and an approval arrives as a host self-report, from the component that also holds the definition being checked. It cannot serve as an independent reference.
- AR §4 path (b), two independent sources agreeing, needs a second producer that saw the approval. There is none.

Under AR §4 as written, a claim resting on the approval can still reach `supported` through a tap-observed descriptor (Case A of #6, from Mayur021's comment on #5).
Under a per-element rule like the one proposed in #6, it would stop at `supported_by_assertion_only`, provided the approval is one of the claim's carrying elements. A weakest-link rule over all required elements, the alternative Mayur021 argues for on #6, gives the same result here.

The adversary in this case is the MCP server, not the host. The host is assumed honest but possibly lax about asking again, so its `asserted` approval is a useful record of its own behaviour. A compromised or lying host is out of scope; nothing in v0.1 or in either option below would expose it.

### 3.3 Q2: on a client–server tap, the invocation digest cannot be `observed`

A `tool.invocation` record can get a `descriptor_digest` from three places.

| Source | Producer | Trust under AR §4 | Note |
|---|---|---|---|
| The last `tools/list` a tap saw | recorder tap | `observed` for the listing record itself; not a valid source for the invocation | Seen at step 5, not 6. Linking by name and order is an inference (AR §5), so a tap-emitted invocation carrying it would be mislabelled `observed`. |
| The definition the client held | host or agent runtime | `self-report`, `asserted` | It can differ from the latest listing. In 2026-07-28 caching is part of the protocol (`ttlMs`, `cacheScope`), so a stale list is legitimate, not only a client quirk. |
| The definition the server ran | server or tool | `self-report`, `asserted` | The server that changed the tool is the party being checked. |

2026-07-28 makes the first row weaker: there is no session, so a tap cannot group a listing and a call into one session, and a tool list "MAY vary by the authorization presented on the request".

So, on a client–server tap, the invocation digest is either `asserted` or absent.
If absent, G-DESC-001 fires, which is the honest result.
A gateway that fetches the list again right before each call narrows the window, but the call still does not reference the definition that was checked.

For MCP, this is in tension with AR §3.2 (`observed_via: invocation`) and AR §7 S3 `tapped-both` ("observes descriptor at list and at invocation").
On MCP, `tools/call` carries no descriptor bytes, so that observation can only come from a component that holds the definition (self-report) or from a tap placed inside the server boundary, a different placement that needs its own trust argument.
This belongs in the S2/S3 specs issue, together with the C-S3-01 "first or latest listing" ambiguity, and is only noted here.

### 3.4 What v0.1 cannot tell apart

Two runs, identical except for one host step:

- **R1:** approve A, invoke A, change to B, list B, invoke B without asking again.
- **R2:** the same, but the host asks again and the user approves B before the second call.

No v0.1 record kind, field, gap rule or claim evaluator represents a user approval or its scope.
A producer could leave an indirect trace: an `agent.decision` whose `caused_by` points to the B descriptor record, or an `authz.decision` carrying `correlation.descriptor_digest`.
No rule would read that trace as an approval. It would be `asserted`, it would have no scope, and it would look like the agent's decision rather than the user's.
So the analyzer output (gaps and claim statuses) does not differ between R1 and R2.
Pins do not separate them either: without a pin, G-DESC-003 fires in both runs; with a static pin of A, B mismatches the pin in both, including R2, where B was re-approved.

## 4. Options for approval evidence

Both keep approval apart from authorization and outcome, the boundary AngeYobo set out on #5.

### Option A: a new record kind, `tool.approval`

One record per approval, with an `approval_id`; each `tool.invocation` that relies on it references it.

- **Trust:** `asserted` (§3.2).
- **Fit:** a session or persistent approval is one record covering many invocations, joined by `approval_id`. #2 stays independent of MCP approval semantics.
- **Costs:** a new kind in AR §3.2, a new correlation field (`approval_id`) and its AR §5 edge (rule 4 extended to `tool.approval`), two proposed gap rules ("invocation without a prior approval" and "approval without a descriptor digest"), and a claim evaluator. Schema and correlation changes need an ADR.

### Option B: extend `authz.decision`

Add the approved definition's digest and the approval scope to `authz.decision`.

- **Trust:** the policy decision can be corroborated under AR §4 path (b), when a PDP and a gateway tap agree on `invocation_id` and decision. The approval fields cannot, because neither saw the host prompt. A reference-check record verifying that `authz.decision` would appear to vouch for its asserted approval fields, unless a new rule excludes them.
- **Costs:**
  - `authz.decision` is keyed by `invocation_id` (AR §5). A session approval covers invocations that did not exist when it was given. Either the PDP restates the approval on every invocation, as a decision it did not make at that moment, or the join changes, which changes G-AUTHZ-001 and G-AUTHZ-002.
  - A per-invocation record carrying an approval would also close G-AUTHZ-001 ("invocation was authorized") with a user approval.
  - AR §3.2 lists `pdp / gateway` as the emitters of `authz.decision`; a host-emitted approval needs a new emitter.
  - It mixes "a user approved this definition" with "policy allowed this call", which the #5/#2 boundary keeps apart. A missing approval becomes a missing field on an existing record, which needs a field-level gap rule.

### Status under AR §4 today and under #6

Claim "approved-definition match" (no ID yet): "the definition the client held at invocation is the one the user approved" (`descriptor_digest_basis` in §5 says which definition the invocation digest describes).
Elements: the approval, the invocation digest, and the `tool.descriptor.observed` joined to it by digest (AR §5 rule 4).

| Evidence | AR §4 as written | With #6 (approval and invocation digest carrying) |
|---|---|---|
| Approval `asserted`, descriptor tap-`observed`, digests match | `supported` | `supported_by_assertion_only` |
| Approval `asserted`, digests differ, same profile (#4) | `contradicted` | `contradicted` |
| No approval (record or fields) | `insufficient_evidence`, gap from a proposed rule; no AR §6 rule covers approval | same |

Under AR §4 both options hit Case A of #6 (first row).
Under #6 they differ: carrying elements are record kinds, so in Option B the carrying element is `authz.decision`, which can be corroborated via AR §4 (b) while its approval fields stay `asserted`. Option B would need a field-level carrying rule that #6 does not propose.

### Which component emits the approval

`agent-runtime` needs no enum change, but a host UI answer then reads as the agent's own decision. A new `host` value shows that the approval came from the host UI. Trust is `asserted` either way; the difference is attribution.

## 5. Field sketch for a later ADR

Illustrative only. `descriptor_digest` follows whatever #4 settles. The shape below is the profile object Mayur021 proposed in #4, as narrowed in the #4 triage (`profile`, `algorithm`, `value`).

```jsonc
// Option A: new record kind (sketch)
{
  "kind": "tool.approval",
  "source": { "component": "host", "channel": "self-report" },  // or agent-runtime: undecided (§4); trust asserted
  "correlation": {
    "approval_id": "appr_…",
    "descriptor_digest": { "profile": "…", "algorithm": "sha256", "value": "…" }
  },
  "payload": {
    "tool_name": "files.search",
    "server_ref": "sha256:…",        // launch-configuration digest or endpoint; serverInfo is self-declared
    "decision": "approved",          // approved | refused
    "scope": "session",              // once | session | workspace | persistent
    "scope_target": "tool"           // tool | server
  }
}

// On tool.invocation (either option)
{
  "correlation": {
    "approval_id": "appr_…",                   // absent: gap "invocation without a prior approval"
    "descriptor_digest": { "…": "…" },
    "descriptor_digest_basis": "client_held"   // client_held | server_reported
  }
}
```

- `descriptor_digest_basis` is self-declared by the emitter. It does not change trust (CONTRIBUTING ground rule 3), but it decides which claim the digest can support, so the ADR should state who may set it. It has no "unknown" value: a missing basis is a gap (ADR-0004). If §3.3 holds, a client–server tap can never be the basis, so there is no value for it.
- `server_ref`: `serverInfo` is self-declared by the server (in 2026-07-28, with no `initialize` handshake, it moves to each result's `_meta` as a SHOULD). AISVS 10.4.22 points to the launch configuration.
- `scope` values come from the blog post cited in §8: VS Code offers once, this workspace and always, each for one tool or for every tool of the server; Gemini CLI offers a session scope.

## 6. Synthetic scenario sketch

A candidate for the post-v0.1 "MCP tool rug-pull" scenario: synthetic tools and domains, a scripted host, no live MCP integration.
ADR-0013 (Proposed) treats approval and the second fetch as execution steps, so R1 and R2 (§3.4) must be separate scenarios, not variants of one scenario.
Within each, variants change only which records are emitted.

- **R1:** list A, approve A (session, tool), invoke A, change to B, `list_changed`, list B, invoke B with no new approval.
- **R2:** the same, plus a new approval of B before the second call.

"Approved-definition match" at the second call:

| Variant | Records | R1 | R2 |
|---|---|---|---|
| `full` | approvals `asserted`, descriptors tap-`observed`, invocation digest `client_held`, all under one profile | `contradicted` | `supported` under AR §4 today; `supported_by_assertion_only` if #6 is accepted |
| `approval-without-digest` | approvals name the tool only | `insufficient_evidence` (proposed gap: approval without a descriptor digest) | same |
| `no-approval-record` | v0.1 shape: no approval | `insufficient_evidence` (proposed gap: invocation without a prior approval) | same |
| `name-only` | invocation carries `tool_name` only | `insufficient_evidence` (G-DESC-001) | same |

If approval and invocation digests use different profiles, R1 `full` should be `insufficient_evidence`, not `contradicted`: a gap analogous to G-DESC-004 in #4 (defined there for a pin and an observation), under the comparability rule proposed in #6.
If #6 is accepted, the R2 `full` cell is a test case for it.

## 7. Acceptance criteria

From #5; the third criterion moved to #4.

1. **This write-up fails** if a v0.1 bundle can already tell "approved A, invoked B" apart from "approved B, invoked B" in v0.1 analyzer output (gaps and claim statuses). §3.4 argues it cannot; a counterexample would falsify it.
2. **A schema built on it fails** if a missing approval gives `contradicted` instead of a gap. §4 and §6 keep it at `insufficient_evidence` in both options.

## 8. Prior data (motivation only)

Aggregate counts from real clients, outside this project's trust model, as stated in #5. The client-log counts in #5 are left out because they bear on detectability.
Not evidence for a detectability claim (EV-4).
Preprint, not peer reviewed: [Outside the Prompt](https://doi.org/10.5281/zenodo.23867645), [harness](https://doi.org/10.5281/zenodo.23861225) (v0.5.0; the runs below used [v0.3.0](https://doi.org/10.5281/zenodo.23438372)), [blog post](https://paolocostanzo.github.io/approved-mcp-tools-can-change-after-you-say-yes) (it also covers two editors run by hand).

*Approved tool changes mid-session* (6 clients × 2 conditions × 5 repetitions):

- Without `list_changed`, every client kept the old list (30 of 30).
- With it, B reached 2 clients (10 of 60 runs, all in the 30 with the notification). One was Claude Code, which in its default auto mode doesn't ask even at first use. The other was Gemini CLI, which showed a notice and didn't ask again.
- After a restart, Gemini CLI asked again (10 of 10), because its session approval had expired, not because it noticed the change. The other 5 used B without asking.
- Labels come from a rule-based coder over the server log and the client screen. The author checked them as a whole, not packet by packet.
- The preregistered local-model coder agreed poorly (κ = 0.115). 45 of its 46 disagreements trace to one misleading line in the coding packets. A post-hoc coder from another model family agreed 60/60.

## 9. Limitations

- **Analytical, not empirical.** The findings come from reading the protocol and the v0.1 model; no analyzer exists yet to run records through.
- **Two revisions.** The protocol reading is pinned to 2025-11-25 and 2026-07-28. A later revision that adds a definition reference to `tools/call` would change §3.3.
- **Host internals.** Clients differ in how they store approvals and cached definitions; no specific client is modelled, nor any gateway that edits the listing it forwards (AR §4 (b) already names a gateway tap).
