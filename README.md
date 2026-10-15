# Found in meta

**When the document exists. So why can't anyone find it?**

A small synthetic document-integrity investigation. An approved rental agreement exists, but the property manager cannot find it under Apartment A14: the document's relationship points to A41. A frozen ERP record instead says A14. The evidence supports a discrepancy and an authorised verification request; it does not establish who made an error or authorise a correction.

This is a case study with a replay command, four deterministic fixtures and evidence a person can inspect. It has no live M-Files or ERP integration, AI dependency, metadata write-back, ticket store, approval service, authentication system or frontend.

## Run the demonstration

Python 3.11 or later. The replay uses only the standard library and runs from a fresh checkout without installing the package:

```sh
python -m found_in_meta --out output/demo
python -m found_in_meta --all --out output/demo
```

Open `output/demo/a14_relationship/report.md` for the first investigation. Its sibling `bundle.json` contains the complete machine-readable evidence, including exact source contents and SHA-256 hashes. Repeating the same command produces identical artifact bytes. The output directory must be outside the fixtures.

The command's successful exit means the investigation ran; findings such as a permission failure remain findings, not execution errors. Invalid fixtures or an unknown case exit with code 2. Use `--case permission_blocked`, `--case authority_unresolved` or `--case clean` to replay one control. `--fixtures PATH` selects an alternative local snapshot directory for experiments; no source is modified.

Committed [example artifacts](examples/) show all four results without running Python.

## What the first case establishes

1. The complaint is preserved verbatim with its requester, apartment and agreement reference.
2. Matching the agreement ID in the investigator's export finds the document and its synthetic content independently of the apartment relationship.
3. Its recorded workflow state is approved, with an approval-event observation.
4. The requester passes the simulated read-permission check.
5. The apartment view excludes it because its relationship is A41, while the query is A14.
6. The corresponding ERP snapshot says A14. Fictional policy nominates ERP for comparison, subject to authorised verification.

The report separates those observations from unconfirmed explanations: an incorrect selection, a stale ERP value or a mapping problem cannot be distinguished from these snapshots alone. A human must check the agreement, identity mapping and source ownership before deciding whether any relationship should change. Document approval alone does not validate its metadata or permit a correction. Every bundle records `changes_applied: []`.

## Control cases

| Case ID | Observations | Principal finding |
| --- | --- | --- |
| `a14_relationship` | Approved document points to A41; ERP points to requested A14; requester has read permission | `relationship_mismatch_requires_verification` |
| `permission_blocked` | Apartment relationship agrees with ERP; requester lacks read permission | `permission_blocked` |
| `authority_unresolved` | Document and ERP disagree; source authority is not established | `authority_unresolved` |
| `clean` | Correct relationship, approved workflow, requester can read | `no_retrieval_failure` |

Workflow exclusion is checked separately; a document outside the approved view cannot be described as approved. Ambiguous document or ERP matches stop that comparison rather than picking one silently. The clean control establishes success only for the simulated query and fixed snapshot.

## Architecture and boundary

```text
frozen JSON + synthetic document text
                |
  validate types, identities and relationships
                |
  agreement lookup + apartment-view replay
  workflow + permissions + ERP comparison
                |
      evidence bundle + Markdown report
                |
  authorised human verifies and decides
```

- `found_in_meta/fixtures/`: fictional housing organisation, properties/apartments, agreements, related documents, typed metadata/classes, workflow observations, permission rules, ERP records, comparison policy and source identifiers.
- `found_in_meta/engine.py`: deterministic checks against those snapshots; no network or write-back.
- `found_in_meta/report.py` and `cli.py`: readable report and local output command.
- `tests/`: controls, evidence integrity, repeatability, source immutability and fault injection.

The report is for a simulated **authorised investigator** who already has an exported evidence set. It can include documents hidden from the requester; the CLI is not an access-controlled end-user search tool. Principal labels and role lists are fixture data, not authentication.

[Datum context inspection](docs/context.md) records the reviewed revisions, including `build/round-six`, and the project boundary. Datum already provides tickets, journals, findings, proposals and human decision custody. This project emits its own [bundle format](docs/bundle.md); a future adapter must map it to a verified Datum interface. No Datum contract is invented and no existing repository is modified.

## Tests

```sh
python -m venv .venv
# Activate the virtual environment for your shell, then:
python -m pip install -e ".[test]"
python -m pytest -q
```

Only test/development installation needs third-party packages. The demonstration itself is offline. The package can also be installed to expose the `found-in-meta` command.

## Assumptions and limits

All people, documents, business records, dates, roles and incidents are invented and fixed. Hashes identify preserved bytes; they are not signatures or proof that a real system was truthful. Stable agreement IDs and cross-system apartment IDs are declared mappings in this small fictional environment. A real investigation must verify those mappings.

[System assumptions](docs/system-assumptions.md) separates the simulation from limited product concepts confirmed in M-Files' documentation. This is not the M-Files schema or a proprietary API implementation. It omits production indexing, synchronisation, version history, complex effective permissions, identity assurance and real agreement content analysis.

The first working demonstration ends here. See [.handoff.md](.handoff.md) for test results, limitations and possible next tasks. No licence has been selected; all rights reserved.
