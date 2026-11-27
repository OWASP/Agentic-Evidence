# Verifier verdicts and the claim statuses proposed in #6

Informs [#6](https://github.com/OWASP/Agentic-Evidence/issues/6) and [#4](https://github.com/OWASP/Agentic-Evidence/issues/4). It does not decide either: the claim-status model comes out of #6.

## Question

The offline verifier in [agent-evidence-vectors](https://github.com/probityai/agent-evidence-vectors) judges signed run records and gives a decision per record. How do its outputs line up with the four statuses proposed in #6 (`supported`, `supported_by_assertion_only`, `contradicted`, `insufficient_evidence`), and where do they not?

## Method

Read the verifier's own documentation: the [decision and verdict codes](https://github.com/probityai/agent-evidence-vectors/blob/main/docs/guides/offline-verify.md) and the [verifier contract](https://github.com/probityai/agent-evidence-vectors/blob/main/docs/reference/verifier-contract.md#receipt-verdict-codes). Compare each output with the derivation rule proposed in #6 and the comparability rule in #4.

## Findings

1. The verifier's `decision` has two values, `supported` when the record verifies and `contradicted` when it does not. A valid record also carries a verdict code: none when every substrate row is attested under the consumer's keys, `NOT_PUBLICLY_VERIFIABLE` when a row is unattested, `NOT_RECONSTRUCTIBLE` when the rows rest on no sealed observation record. A valid report takes the code of its worst row tier.
2. The two limit codes line up with the assertion axis in #6. `NOT_RECONSTRUCTIBLE` (every row declared, none tied to a sealed observation) is the closest to `supported_by_assertion_only`. `NOT_PUBLICLY_VERIFIABLE` is the mixed case #6 Case A describes: some rows are attested and some are not. The verifier answers it with the worst-row rule, which is the weakest-link alternative in #6 and needs no list of carrying elements.
3. `contradicted` is wider than #6's. The verifier gives it for a failed hash or proof (`LEAF_HASH_MISMATCH`, `PROOF_BROKEN`), but also for an unreadable record (`MALFORMED`) and for a claim that cites no sealed record that can carry it (`CLAIM_NOT_BOUND`). Under #6 the last two are not conflicts between comparable elements, so they would read as `insufficient_evidence`. A mapping between the two projects should keep that difference visible.
4. Comparability is outside the verifier's decision today. Whether two digests were computed over the same bytes is the question in #4, and the verifier does not ask it. The [tool-descriptor-digest cases](https://github.com/probityai/agent-evidence-vectors/tree/7fd5f3d90be7fb1ebb1d4bdeb990f00579f580bf/corpora/vectors-tool-descriptor-digest) implement the #4 rule: a pin and an observation compare only when both carry a profile and the profiles are equal, and anything else is a gap and never a contradiction.

## Limitations

The verifier judges a signed record after the fact; this project derives statuses from records an investigator holds, with trust assigned by channel. The mapping above compares definitions, not behaviour on the same inputs, and no scenario here exercises either side.
