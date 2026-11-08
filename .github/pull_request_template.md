## What and why

<!-- Problem, change, and the HANDOFF.md milestone/task it belongs to. Link the issue. -->

Closes #

## How to verify

<!-- Exact commands a reviewer can run. -->

```
make check
```

## Checklist

- [ ] `make check` passes locally.
- [ ] `HANDOFF.md` is updated if this changes project state.
- [ ] Changes to the schema, trust model, determinism, storage format, or public CLI/API have an ADR (status Proposed) in `DECISIONS.md`.
- [ ] No wording (code, docs, UI, commit messages) claims an attack is "detected", "prevented", or "proven" unless a scenario test demonstrates exactly that.
- [ ] Synthetic data only: no secrets, real prompts, production traces, or real domains/addresses.
- [ ] New files carry `SPDX-License-Identifier: Apache-2.0` where the format allows comments.

## Limitations and follow-ups

<!-- What this does not do. -->
