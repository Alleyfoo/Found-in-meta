# Investigation bundle, version 1

`schema_version: "found-in-meta.investigation/v1"` names **our artifact format**, not a Datum or M-Files contract. The JSON and Markdown are two renderings of one investigation. No external API or adapter is implemented.

| Field | Purpose |
| --- | --- |
| `case_id`, `replay` | Stable fixture identity, fixed snapshot time, synthetic flag, tool version and intended investigator audience. No execution clock. |
| `complaint` | Verbatim complaint, requester ID, requested apartment and agreement ID used for the declared cross-system match. |
| `sources` | Snapshot source identifiers, capture times and declared provenance. |
| `evidence` | Identified observations with source ID, original record ID, locator and observed value. Includes document metadata/relationships, content existence, workflow/approval, access, ERP and policy. |
| `checks` | Named checks with observed/expected values, pass/fail/unknown result and evidence references. A failed check is not proof of a particular causal explanation. |
| `findings` | Confirmed snapshot findings, stable codes and supporting evidence references. |
| `unknowns` | Limits of the available evidence and unresolved questions. |
| `inferences` | Competing causal explanations explicitly marked `unconfirmed`. These are not observed facts. |
| `retrieval` | Agreement-matched documents, documents returned by the requester view and independent view blockers. |
| `proposed_next_action` | Verification or review recommendation, never an executed operation. |
| `required_human_decision` | Whether a decision is needed, the question and the fictional role responsible. This records a requirement, not an approval. |
| `changes_applied` | Always an empty list. There is no correction code path. |
| `source_files` | Fixture-relative paths, SHA-256 hashes and exact UTF-8 source text, including the environment snapshot and document artifacts. |

Evidence references are local to a bundle; source IDs and original record IDs preserve source identity across bundles. Locators identify the relevant record/value in a preserved source. The raw environment also contains the small surrounding organisation and control records; it is intentionally synthetic and suitable for the declared investigator audience.

## Rechecking preserved bytes

For each `source_files` item, encode `content` as UTF-8 and compare its SHA-256 to `sha256`. To replay independently, materialise these contents under a new directory preserving the relative paths, then run:

```sh
python -m found_in_meta --fixtures PATH_TO_MATERIALISED_SOURCES --all --out output/recheck
```

The output must be outside the materialised source directory. With the same code version and bytes, the JSON and Markdown are identical. Fixture validation rejects invalid types, missing references and unsafe content paths rather than treating malformed data as business evidence. Multiple candidate matches remain unresolved; the engine does not select a convenient document.

## Possible future Datum adapter

An adapter could preserve the original bundle as evidence, associate the complaint with a real Datum ticket, attach findings and propose authorised verification. It would need to inspect a chosen Datum revision and settle identity, permission, deduplication, evidence storage and lifecycle rules. The adapter should preserve the distinction between observations, competing explanations, proposed action and the actual person's decision. This document deliberately specifies no Datum field mapping, method signature, endpoint or promise of import compatibility.
