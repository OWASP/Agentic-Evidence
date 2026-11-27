<!-- SPDX-License-Identifier: Apache-2.0 -->

# Authorization-to-outcome scenarios through an external verifier

**Status:** Research write-up, input for the schema change request on [#2](https://github.com/OWASP/Agentic-Evidence/issues/2) and the scenarios in [#21](https://github.com/OWASP/Agentic-Evidence/issues/21).
Nothing here is a decision or an implemented capability.
It is one external verifier's reading of the scenario text, offered as a cross-check, not a reference implementation.

**Informs:**
- [#2](https://github.com/OWASP/Agentic-Evidence/issues/2): scenarios A, B1, B2 and C; the "dispatched without effect observation" gap; the independent effect observation;
- [#21](https://github.com/OWASP/Agentic-Evidence/issues/21): scenarios D and E, and the `unordered-revocation` variant.

**Related:** [#6](https://github.com/OWASP/Agentic-Evidence/issues/6) (claim-status derivation), [#20](https://github.com/OWASP/Agentic-Evidence/issues/20) (approval binding).

**Disclosure:** I'm the author of AMEP (Agentic Mandate Evidence Protocol), the verifier used here: an IETF individual Internet-Draft with Apache-2.0 reference verifiers. Mapping these scenarios found two gaps in AMEP itself, both fixed; §4 lists them.

"AR §n" below means a section of [ARCHITECTURE.md](../../ARCHITECTURE.md).

## 1. Questions

- **Q1.** Does an external verifier, given only the records each evidence variant leaves, reach the conclusions the scenarios expect? In particular:
  - that a component's own claim never stands in for an effect observation (#2, key rule);
  - that B1 and B2 without the oracle can't be told apart.
- **Q2.** Where it doesn't, is the difference in the scenarios or in the verifier?

Out of scope:
- **Signing:** signed evidence is deferred (OD-3), so the trust levels of AR §4 are read below as distinct keys and operators, nothing more.
- **Enforcement:** for example holding later uses until an outcome is known.
- **The new record kinds and gap IDs themselves:** those are #2's schema change request.

## 2. Method and sources

1. **Scenario text** as written in #2 (the 14 November restructure, with the 22 November B1/B2 split) and #21 (the issue body as of 26 November, with the comments on C-D-03, C-D-04 and the declared window).
2. **Mapping** each evidence variant to an AMEP evidence packet ([`interop/owasp-agentic-evidence/run.mjs`](https://github.com/stafordtituss/amep/blob/87b29f999a3c77d8a5250fb27a1888afcb5d8ea0/interop/owasp-agentic-evidence/run.mjs)), using #2's shared setup: a scripted PDP, an agent stub, and a mock tool with its own store, which the runner reads as the effect oracle.
3. **Evaluation** of each packet with AMEP's Python and JavaScript reference verifiers. The two share one author, so their agreement shows consistency, not independence. Each packet's digest is in [`results.json`](https://github.com/stafordtituss/amep/blob/87b29f999a3c77d8a5250fb27a1888afcb5d8ea0/interop/owasp-agentic-evidence/results.json).

The mapping from this project's records:

| AR §3.2 record | AMEP object | Signed as |
|---|---|---|
| grant from the authority source, with its declared window (#21) | mandate, `revocation.window` | the authority source |
| `authz.decision` allow / deny | decision, phase `pre_execution` | the host / PDP |
| `tool.invocation` | invocation, `files.write` declared `write_shared` | the host |
| `tool.result`, `trust: asserted` | the executing side's own receipt | a key under the host's operator |
| independent effect observation (#2, item 3) | effect receipt, or a "not executed" statement | a key under another operator |
| revocation | revocation | the authority source |

`write_shared` makes AMEP's observer-independence rule apply to the write. That rule is the counterpart of #2's key rule: no asserted record satisfies an effect requirement.

*This table maps records onto AMEP for this write-up only. It isn't a proposal for how trust is assigned here: this project assigns trust by channel (AR §4, EV-2), and signed evidence is deferred (OD-3).*

No code was added to this repository.

## 3. Findings

### 3.1 The results

"Expected" quotes the scenario text where it states an outcome; "—" where it doesn't state one in the terms used here.

| Scenario | Variant | Expected in #2 / #21 | AMEP verdict | AMEP gap |
|---|---|---|---|---|
| A1 | oracle present | execution claim `supported` | preserved | — |
| A2 | oracle removed | not `supported` | unresolved | `independent_observer` |
| A3 | claim absent | Gap | unresolved | `receipt` |
| B1 | oracle present | "executed" supported | preserved | — |
| B1 | oracle removed | neither claim; gap | unresolved | `receipt` |
| B2 | oracle present | "not executed" supported | preserved ("nothing executed") | — |
| B2 | oracle removed | same gap as B1 | unresolved | `receipt` |
| C | with the original invocation | no second effect; distinct from a denial | preserved | — |
| C | without the original | distinct from a denial | preserved ("nothing executed") | — |
| C | control: the replay took effect | — | violated, "executed twice" | — |
| D1 | grant declares no window | — | violated (authority withdrawn before the effect) | — |
| D1 | grant declares a 10 s window | — | preserved, the revocation named in the reason | — |
| D1 | `unordered-revocation` | C-D-02 `insufficient_evidence` | unresolved | `ordering` |
| D2 | second allow at dispatch | the second allow can't take C-D-02 to `supported` | violated (same as D1) | — |
| D3 | the resource's check rejects the write | C-D-03 `supported` | preserved ("nothing executed") | — |
| D3 | no resource-side record | — | unresolved | `receipt` |
| E1 | oracle present | "not executed" `contradicted` | preserved (the write is observed and within authority) | — |
| E1 | the tool signs "not executed" | — | violated (receipt contradicts the statement) | — |
| E2 | oracle present | — | preserved ("nothing executed") | — |
| E1 / E2 | oracle removed | the failure result alone leaves the write unresolved | unresolved | `receipt` |

**B1 and B2 without the oracle are the same AMEP packet,** byte for byte, as #2 requires. So any verdict on them is the same verdict.

### 3.2 Where they line up

- **The key rule holds independently.** The verifier reaches `unresolved` in A2, and wherever only the executing side or the PDP speaks. It never reads a component's claim as an effect.
- **"Dispatched without effect observation" is the verifier's most common gap.** It is the `receipt` gap in A3, B1 and B2 without the oracle, D3 without the resource record, and E without the oracle: the same conclusion #2's proposed gap rule blocks.
- **A deny alone doesn't show that nothing ran**, as noted on #2. The verifier needs an executing-side or resource-side record to conclude "nothing executed" (B2, D3, E2). The PDP's or host's own deny isn't enough.
- **The second allow in D2 changes nothing.** The verifier evaluates authority at the effect's own time, so a re-check at dispatch neither helps nor hurts, which matches #21.

### 3.3 Where they differ, and why

1. **Verdict versus claim status.**
   - AMEP answers one question per call: did what ran stay within authority? This project assigns a status per claim.
   - So E1 with the oracle present is `preserved`: the write happened and was authorized. The project's "not executed" claim is `contradicted` for the same records. Both are right; they answer different questions.
   - The contradiction becomes a verdict only when the tool signs its own "not executed" (E1, second row): violated.
   - This comparison depends on #2. Here distinct keys and operators stand in for trust levels, but main assigns trust by channel (AR §4, EV-2), and `verified` (b) covers two independent sources agreeing on a decision, not on an effect. The independent effect observation has no trust mechanism in main yet. The readings that rest on it assume #2 adds one.
2. **C needs a record of the original to say "replay".** With the original invocation, the verifier knows the operation already took effect, and a second effect would be "executed twice" (control row). Without it, the refused call reads as a call that didn't run. That supports keeping `replay_rejected` distinct from `deny` (#2, item 1). The distinction rests on state that only the original's record carries. Raised on [#2](https://github.com/OWASP/Agentic-Evidence/issues/2#issuecomment-7225315285).
3. **Windows.**
   - The verifier reads the declared window as part of the grant, as #21's fixtures now do, so an effect inside it is `preserved`.
   - For this project, the window's source determines its trust. The verifier assumes it was signed with the grant, before the outcome was known.
   - A window stated only in the revocation record would need a different reading, which is the case #21 lists under what the scenario does not show.
4. **Ordering needs a declared bound per source.**
   - Under main's default (AR §5), a run is ordered by `collected_at`, the recorder's clock. So every pair of records is orderable, but by arrival, not occurrence.
   - Main already covers part of the question:
     - EV-6 requires each ordering conclusion to say which clock it used;
     - G-AUTHZ-002 compares a decision's `collected_at` with the invocation;
     - G-TIME-001 flags a record whose `event_time` and `collected_at` differ by more than one global tolerance (default 5 s).
   - None of these says when two `event_time`s from different sources can't be ordered at all, which is the case `unordered-revocation` describes. The verifier reaches `unresolved` (`ordering`) there only because each source's clock skew is declared. With no declared bound, it compares the two times as given.
   - **Proposed change:** a skew bound declared for each emitting source, beside G-TIME-001's tolerance. Two `event_time`s from different sources are then unorderable when they differ by no more than the sum of the two bounds, and the proposed gap ("a revocation that cannot be ordered against the effect") fires on exactly those pairs. This would also answer HANDOFF Q4: the 5 s default becomes the fallback for a source that declares no bound. Raised on [#21](https://github.com/OWASP/Agentic-Evidence/issues/21#issuecomment-7225314821).

## 4. Gaps found in the verifier

Mapping these scenarios found two places where AMEP itself was wrong. Both are fixed in the same change, with test vectors ([stafordtituss/amep#44](https://github.com/stafordtituss/amep/pull/44)):

1. **A1 came out `unresolved`.** The executing side's own receipt was judged alone and failed the independence rule, even with an independent observation of the same write present. Adding corroborating evidence weakened the verdict. It is now read as one effect, observed independently.
2. **`unordered-revocation` came out definite.** The verifier ordered the two times as if one clock produced both. It now honours a declared clock skew per key, and returns `unresolved` (`ordering`) within it ([stafordtituss/amep#43](https://github.com/stafordtituss/amep/issues/43)).

## 5. Limitations

- **This is one reading,** by the author of the verifier, of scenario text that is still changing; the scenario author has not reviewed it. Where the text is ambiguous, the mapping states its choice in `run.mjs`.
- **Fixtures:** the packets are built from the scenario text, not from this project's fixtures, which wait for M1. When the fixtures land, rerunning against them is the real cross-check.
- **Trust levels:** distinct keys and operators stand in for `asserted`, `observed` and `verified`. That carries signing assumptions this project has deferred (OD-3), so it is not a proposal for how trust is assigned here.
- **Effect class:** `files.write` is classed `write_shared` so that the independence rule applies. For a call classed `write_local`, the verifier accepts the executing side's own receipt, which this project's key rule would not.
- **No signal from a real system:** every run here is offline, with a mock tool and scripted times.
