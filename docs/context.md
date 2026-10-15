# Context inspected before implementation

Inspected read-only on 2026-10-15:

- [Datum main, `5da65a6`](https://github.com/Alleyfoo/Datum/tree/5da65a6fa490abd38e6829974cb7628240ea0e21).
- [build/round-six, `fe37e39`](https://github.com/Alleyfoo/Datum/tree/fe37e39dc9de14df156e96e5bde877f8d1d86ebe).
- GitHub's comparison reports round-six 15 commits behind main, zero ahead. Its changes are already included in main. The branch uses `babel/`; main uses `datum/`. Neither source tree contains a handoff file.

## What Datum already provides

| Mechanism | Inspected implementation on main |
| --- | --- |
| Unified tasks, findings and decision documents; claims and leases; `about`/`blocks` links; attributed journal | `datum/record/store.py`, lines 1–54, 111–159, 500–528 |
| Proposals parked in `needs_input`, linked findings, named human approval/rejection, reasons and decision documents | `datum/record/queue.py`, lines 27–57, 82–154 |
| Facts, tools run, rules, checks, unknowns and separately recorded human answers in receipts | `datum/record/consultations.py`, lines 107–129, 147–169, 309–328 |
| Preserved original files, SHA-256 hashes and intake ledger | `datum/intake/inbox.py`, lines 1–9, 116–171 |
| Trial findings bound to source, ticket and schema, rechecked before human admission | `datum/intake/dispositions.py`, lines 48–60, 140–158 |

Reviewed the README, supporting plan and tests for approval refusal, effect rollback, source-bound findings and receipts. The store explicitly describes its actor names as coordination labels, not authentication (`store.py`, line 54); identity remains an open concern in `docs/plan.md`. This project must not infer an authentication product from Datum's approver labels.

## Boundary

Found-in-meta owns a small fictional housing environment, frozen document/ERP evidence, deterministic checks and a report explaining why a document could not be retrieved. It emits source-linked observations, confirmed findings, unconfirmed explanations and a request for a human decision. A DMS approval observation is never approval to change a relationship.

Datum retains ticket custody, journal and finding/decision storage, claims and the human proposal/approval lifecycle. This repository neither copies nor replaces them and does not depend on Datum at runtime. No Datum or Babel-Tower files were changed.

The JSON bundle is **this project's own versioned artifact**, not a Datum API contract. A future adapter would preserve original evidence and map findings and proposed verification into the actual Datum interface at a chosen revision. Identity, authorisation, deduplication and validation must be designed against that revision. No adapter or automatic correction is implemented here.
