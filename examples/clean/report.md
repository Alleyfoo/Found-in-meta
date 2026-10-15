# Found in meta

*When the document exists. So why can't anyone find it?*

Case: `clean` · Snapshot: 2026-10-01T09:00:00Z

Synthetic investigation for an authorised investigator. The evidence export includes
documents the requester may not read. This report is not a requester-facing search result.

## Original complaint

Please confirm the approved rental agreement for Apartment A44 is available in my approved apartment view.

Requester: `property_manager`; apartment: `A44`; agreement cross-reference: `AGR-004`.

## Confirmed findings

- **no_retrieval_failure**: The agreed apartment relationship, approved state and requester permissions return the expected document in the simulated view. Evidence: evidence-003, evidence-004, evidence-005, evidence-006, evidence-007, evidence-008.

Documents matched by agreement ID: DOC-004.
Documents returned by the requester's apartment view: DOC-004.
View blockers: (none).

## Checks performed

### access-DOC-004: Requester has read access under deny-overrides rules — pass

Evidence: evidence-006.

```json
{
  "expected": true,
  "observed": true
}
```

### workflow-DOC-004: Current workflow state is approved — pass

Evidence: evidence-005.

```json
{
  "expected": "approved",
  "observed": "approved"
}
```

### apartment-view-DOC-004: Document relationship matches requested apartment — pass

Evidence: evidence-004.

```json
{
  "expected": "A44",
  "observed": "A44"
}
```

### candidate-count: Exactly one exported rental agreement matches the agreement identifier — pass

Evidence: evidence-003, evidence-004, evidence-005, evidence-006, evidence-007, evidence-002.

```json
{
  "expected": 1,
  "observed": 1
}
```

### erp-count: Exactly one ERP record matches the agreement identifier — pass

Evidence: evidence-008, evidence-001.

```json
{
  "expected": 1,
  "observed": 1
}
```

### relationship-comparison: DMS and ERP apartment relationships agree — pass

Evidence: evidence-004, evidence-008, evidence-001.

```json
{
  "expected": "equal apartment identifiers",
  "observed": {
    "dms_apartment_id": "A44",
    "erp_apartment_id": "A44"
  }
}
```

## Unknowns and competing explanations

- Snapshots do not establish current live system state.


## Proposed next action

No corrective action is indicated by this snapshot; retain the successful retrieval evidence.

## Required human decision

Required: no. Role: none.

No human decision is required for this clean replay.

Changes applied: none. Recorded workflow approval does not authorise a metadata correction.

## Sources and provenance

```json
[
  {
    "captured_at": "2026-10-01T09:00:00Z",
    "id": "dms_export",
    "label": "Cedar Court synthetic document export",
    "provenance": "Deterministically authored fictional DMS export; no live product or proprietary API used.",
    "snapshot_id": "DMS-2026-10-01-001"
  },
  {
    "captured_at": "2026-10-01T09:00:00Z",
    "id": "erp_snapshot",
    "label": "Cedar Court synthetic ERP snapshot",
    "provenance": "Deterministically authored fictional housing business records; no ERP connection.",
    "snapshot_id": "ERP-2026-10-01-001"
  },
  {
    "captured_at": "2026-10-01T09:00:00Z",
    "id": "housing_policy",
    "label": "Fictional housing comparison policy",
    "provenance": "Fictional comparison policy for this demonstration; not a statement of product behavior.",
    "snapshot_id": "POLICY-2026-09-01-v1"
  }
]
```

## Observed evidence

These observations describe the frozen export, not independently verified live records.

### evidence-001: comparison_policy

Source: `housing_policy`; source record: `policy:relationship-verification:v1`; locator: `environment.json#/comparison_policy`.

```json
{
  "id": "relationship-verification-v1",
  "reference_source_by_agreement": {
    "AGR-001": "erp_snapshot",
    "AGR-002": "erp_snapshot",
    "AGR-003": null,
    "AGR-004": "erp_snapshot"
  },
  "requires_authorised_verification": true,
  "source_id": "housing_policy",
  "source_record_id": "policy:relationship-verification:v1",
  "statement": "ERP is nominated as a comparison reference only for the listed agreements with an explicit value. It is not correction authority. Where null, authority has not been established. All proposed relationship corrections require authorised verification of underlying records and a separate decision."
}
```

### evidence-002: investigator_scope

Source: `dms_export`; source record: `records_investigator`; locator: `environment.json#/investigator`.

```json
{
  "export_scope": "Previously authorised read-only evidence export of all five synthetic documents, metadata, workflow and ACL rules. This label is not authentication or an access grant.",
  "principal_id": "records_investigator",
  "source_id": "dms_export"
}
```

### evidence-003: document_metadata

Source: `dms_export`; source record: `dms:DOC-004:v1`; locator: `environment.json#/documents/3`.

```json
{
  "agreement_id": "AGR-004",
  "class_id": "rental_agreement",
  "id": "DOC-004",
  "metadata": {
    "agreement_id": "AGR-004",
    "effective_date": "2026-09-01",
    "revision": 1,
    "signed": true,
    "title": "Rental agreement AGR-004"
  }
}
```

### evidence-004: relationships

Source: `dms_export`; source record: `dms:DOC-004:v1`; locator: `environment.json#/documents/3/relationships`.

```json
{
  "apartment_id": "A44",
  "property_id": "P1"
}
```

### evidence-005: workflow

Source: `dms_export`; source record: `dms:DOC-004:v1`; locator: `environment.json#/documents/3/workflow`.

```json
{
  "approval_event": {
    "actor_label": "Fictional tenancy approver",
    "at": "2026-09-01T12:00:00Z",
    "id": "APPROVAL-004",
    "meaning": "Approval of this document version; no authority to correct relationships."
  },
  "state": "approved"
}
```

### evidence-006: requester_access

Source: `dms_export`; source record: `dms:DOC-004:v1`; locator: `environment.json#/documents/3/acl`.

```json
{
  "can_read": true,
  "deny_overrides": true,
  "matching_allow_roles": [
    "property_manager"
  ],
  "matching_deny_roles": [],
  "requester_id": "property_manager",
  "requester_roles": [
    "property_manager"
  ],
  "rules": {
    "allow_read_roles": [
      "property_manager",
      "records_investigator"
    ],
    "deny_read_roles": []
  }
}
```

### evidence-007: content_existence

Source: `dms_export`; source record: `dms:DOC-004:v1`; locator: `documents/doc-004.txt`.

```json
{
  "bytes": 351,
  "document_id": "DOC-004",
  "exists_in_export": true,
  "sha256": "afda18c3e37c864b72bdf25545921f650a7a7bf7056ecdd953348c98709d0eac"
}
```

### evidence-008: erp_record

Source: `erp_snapshot`; source record: `erp:rental:004`; locator: `environment.json#/erp_records/3`.

```json
{
  "agreement_id": "AGR-004",
  "apartment_id": "A44",
  "business_status": "active",
  "id": "ERP-004",
  "source_id": "erp_snapshot",
  "source_record_id": "erp:rental:004"
}
```

## Preserved source artifacts

- `documents/doc-001-appendix.txt` — SHA-256 `d71bb7bfc4e001b0324f1d340d3f0b165b66673312ec9f4ab9901d7dd70b533a`
- `documents/doc-001.txt` — SHA-256 `f0f68823391f1e4661bb35649bf386df7c02ef9401a06eef5c7fe0710766c6b2`
- `documents/doc-002.txt` — SHA-256 `339916caf6f9e476b98014753c4031d764f0d1965f45875644d64663a08c5a18`
- `documents/doc-003.txt` — SHA-256 `f76e573fada36bacd17127188a0217efa9d9c134ace8b80bba9fb3bdff9edb4f`
- `documents/doc-004.txt` — SHA-256 `afda18c3e37c864b72bdf25545921f650a7a7bf7056ecdd953348c98709d0eac`
- `environment.json` — SHA-256 `c9b093168804fe50fe78bc5534005e0b0cd59e5f74f6e049327f072a7c0bd62a`

Exact UTF-8 source contents are embedded in bundle.json. Hashes identify these synthetic
artifacts; they do not prove external authenticity or source authority.
