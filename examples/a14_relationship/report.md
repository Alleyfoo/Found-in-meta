# Found in meta

*When the document exists. So why can't anyone find it?*

Case: `a14_relationship` · Snapshot: 2026-10-01T09:00:00Z

Synthetic investigation for an authorised investigator. The evidence export includes
documents the requester may not read. This report is not a requester-facing search result.

## Original complaint

The approved rental agreement for Apartment A14 is missing from my approved apartment view.

Requester: `property_manager`; apartment: `A14`; agreement cross-reference: `AGR-001`.

## Confirmed findings

- **apartment_filter_mismatch**: The document's A41 relationship excludes it from the requester's A14 apartment view. Evidence: evidence-004.
- **relationship_mismatch_requires_verification**: The agreement exists with a DMS apartment relationship different from the ERP record. The fictional policy nominates ERP as a verification reference; it does not authorise a correction. Evidence: evidence-004, evidence-009, evidence-001, evidence-005, evidence-007.

Documents matched by agreement ID: DOC-001.
Documents returned by the requester's apartment view: (none).
View blockers: apartment_filter_mismatch.

## Checks performed

### access-DOC-001: Requester has read access under deny-overrides rules — pass

Evidence: evidence-006.

```json
{
  "expected": true,
  "observed": true
}
```

### workflow-DOC-001: Current workflow state is approved — pass

Evidence: evidence-005.

```json
{
  "expected": "approved",
  "observed": "approved"
}
```

### apartment-view-DOC-001: Document relationship matches requested apartment — fail

Evidence: evidence-004.

```json
{
  "expected": "A14",
  "observed": "A41"
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

Evidence: evidence-009, evidence-001.

```json
{
  "expected": 1,
  "observed": 1
}
```

### relationship-comparison: DMS and ERP apartment relationships agree — fail

Evidence: evidence-004, evidence-009, evidence-001.

```json
{
  "expected": "equal apartment identifiers",
  "observed": {
    "dms_apartment_id": "A41",
    "erp_apartment_id": "A14"
  }
}
```

## Unknowns and competing explanations

- Snapshots do not establish current live system state.
- Who introduced the discrepancy, when it arose and why are not established.
- The signed agreement, source records and an authorised reviewer have not established the correct apartment for a correction.

- **unconfirmed explanation:** A mistaken apartment selection during DMS entry could explain the discrepancy. Evidence considered: evidence-004, evidence-009, evidence-001.
- **unconfirmed explanation:** A stale ERP record or an incompletely recorded reassignment could also explain the discrepancy. Evidence considered: evidence-004, evidence-009, evidence-001.
- **unconfirmed explanation:** An incorrect cross-system agreement identifier mapping could associate records that should not be compared. Evidence considered: evidence-004, evidence-009, evidence-001.

## Proposed next action

An authorised housing records owner should verify the agreement against ERP and source records, decide the correct apartment, and separately authorise any metadata correction.

## Required human decision

Required: yes. Role: housing_records_owner.

Does verification establish the correct apartment relationship, and should a separately controlled correction be authorised?

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

Source: `dms_export`; source record: `dms:DOC-001:v1`; locator: `environment.json#/documents/0`.

```json
{
  "agreement_id": "AGR-001",
  "class_id": "rental_agreement",
  "id": "DOC-001",
  "metadata": {
    "agreement_id": "AGR-001",
    "effective_date": "2026-09-01",
    "revision": 1,
    "signed": true,
    "title": "Rental agreement AGR-001"
  }
}
```

### evidence-004: relationships

Source: `dms_export`; source record: `dms:DOC-001:v1`; locator: `environment.json#/documents/0/relationships`.

```json
{
  "apartment_id": "A41",
  "property_id": "P1"
}
```

### evidence-005: workflow

Source: `dms_export`; source record: `dms:DOC-001:v1`; locator: `environment.json#/documents/0/workflow`.

```json
{
  "approval_event": {
    "actor_label": "Fictional tenancy approver",
    "at": "2026-09-01T12:00:00Z",
    "id": "APPROVAL-001",
    "meaning": "Approval of this document version; no authority to correct relationships."
  },
  "state": "approved"
}
```

### evidence-006: requester_access

Source: `dms_export`; source record: `dms:DOC-001:v1`; locator: `environment.json#/documents/0/acl`.

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

Source: `dms_export`; source record: `dms:DOC-001:v1`; locator: `documents/doc-001.txt`.

```json
{
  "bytes": 351,
  "document_id": "DOC-001",
  "exists_in_export": true,
  "sha256": "f0f68823391f1e4661bb35649bf386df7c02ef9401a06eef5c7fe0710766c6b2"
}
```

### evidence-008: related_document

Source: `dms_export`; source record: `dms:DOC-001-APPENDIX:v1`; locator: `environment.json#/documents/4`.

```json
{
  "acl": {
    "allow_read_roles": [
      "property_manager",
      "records_investigator"
    ],
    "deny_read_roles": []
  },
  "agreement_id": "AGR-001",
  "class_id": "inventory_appendix",
  "content_path": "documents/doc-001-appendix.txt",
  "id": "DOC-001-APPENDIX",
  "metadata": {
    "agreement_id": "AGR-001",
    "title": "Inventory appendix for AGR-001"
  },
  "relationships": {
    "agreement_document_id": "DOC-001"
  },
  "source_id": "dms_export",
  "source_record_id": "dms:DOC-001-APPENDIX:v1",
  "workflow": {
    "approval_event": {
      "actor_label": "Fictional tenancy approver",
      "at": "2026-09-01T12:05:00Z",
      "id": "APPROVAL-APPENDIX-001"
    },
    "state": "approved"
  }
}
```

### evidence-009: erp_record

Source: `erp_snapshot`; source record: `erp:rental:001`; locator: `environment.json#/erp_records/0`.

```json
{
  "agreement_id": "AGR-001",
  "apartment_id": "A14",
  "business_status": "active",
  "id": "ERP-001",
  "source_id": "erp_snapshot",
  "source_record_id": "erp:rental:001"
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
