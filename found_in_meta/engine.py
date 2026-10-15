"""Replay frozen evidence; this module has no correction or network operations."""

from datetime import date, datetime
import hashlib
import json
from pathlib import Path


def default_fixture_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _index(items, name):
    _require(isinstance(items, list), f"{name} must be a list")
    result = {}
    for item in items:
        _require(isinstance(item, dict), f"{name} entries must be objects")
        key = item.get("id")
        _require(isinstance(key, str) and key, f"{name} entry requires a string id")
        _require(key not in result, f"duplicate {name} id: {key}")
        result[key] = item
    return result


def _text(value, label):
    _require(isinstance(value, str) and bool(value), f"{label} must be a nonempty string")


def _timestamp(value, label):
    _text(value, label)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        _require(parsed.tzinfo is not None, f"{label} requires a timezone")
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO timestamp with timezone") from exc


def _read(root, relative):
    _text(relative, "source file path")
    path = root / relative
    _require(not Path(relative).is_absolute(), f"source path must be relative: {relative}")
    _require(path.resolve().is_relative_to(root.resolve()), f"source path escapes fixture: {relative}")
    try:
        raw = path.read_bytes()
        content = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read UTF-8 source file {relative}: {exc}") from exc
    return {"path": Path(relative).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "content": content}


def _typed_metadata(metadata, definition, label):
    _require(isinstance(metadata, dict), f"{label}.metadata must be an object")
    fields = definition.get("metadata_fields")
    _require(isinstance(fields, dict), "document class metadata_fields must be an object")
    _require(not (metadata.keys() - fields.keys()), f"{label} has undeclared metadata fields")
    for key, field in fields.items():
        _require(isinstance(field, dict), f"{label} metadata field declaration must be an object")
        kind = field.get("type")
        _require(kind in {"string", "date", "boolean", "integer"}, f"unsupported metadata type: {kind}")
        if key not in metadata:
            _require(not field.get("required", False), f"{label} missing required metadata: {key}")
            continue
        value = metadata[key]
        valid = ((kind == "string" and isinstance(value, str) and bool(value))
                 or (kind == "date" and isinstance(value, str))
                 or (kind == "boolean" and type(value) is bool)
                 or (kind == "integer" and type(value) is int))
        _require(valid, f"{label}.metadata.{key} must have type {kind}")
        if kind == "date":
            try:
                _require(date.fromisoformat(value).isoformat() == value, "date is not canonical")
            except ValueError as exc:
                raise ValueError(f"{label}.metadata.{key} must be an ISO date YYYY-MM-DD") from exc


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _load_validated(fixture_dir):
    root = Path(fixture_dir)
    environment_file = _read(root, "environment.json")
    try:
        env = json.loads(environment_file["content"], object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid environment.json: {exc}") from exc
    _require(isinstance(env, dict), "environment must be an object")
    _timestamp(env.get("snapshot_at"), "snapshot_at")
    indexes = {name: _index(env.get(name), name) for name in (
        "sources", "properties", "apartments", "document_classes", "workflow_states",
        "principals", "erp_records", "documents", "cases")}
    sources = indexes["sources"]
    for source in sources.values():
        _timestamp(source.get("captured_at"), f"source {source['id']}.captured_at")
        _text(source.get("snapshot_id"), "source snapshot_id")
        _text(source.get("provenance"), "source provenance")

    def sourced(item, label):
        _require(item.get("source_id") in sources, f"{label} references unknown source")
        _text(item.get("source_record_id"), f"{label}.source_record_id")

    for name in ("properties", "apartments", "document_classes", "workflow_states", "erp_records"):
        for item in indexes[name].values():
            sourced(item, f"{name} {item['id']}")
    for apartment in indexes["apartments"].values():
        _require(apartment.get("property_id") in indexes["properties"], "apartment references unknown property")
    for principal in indexes["principals"].values():
        roles = principal.get("roles")
        _require(isinstance(roles, list) and all(isinstance(r, str) and r for r in roles), "principal roles must be string list")
    investigator = env.get("investigator")
    _require(isinstance(investigator, dict), "investigator must be an object")
    _require(investigator.get("principal_id") in indexes["principals"], "unknown investigator principal")
    _text(investigator.get("export_scope"), "investigator export_scope")
    _require(investigator.get("source_id") in sources, "investigator references unknown source")
    policy = env.get("comparison_policy")
    _require(isinstance(policy, dict), "comparison_policy must be an object")
    sourced(policy, "comparison_policy")
    _require(policy.get("requires_authorised_verification") is True, "policy must require authorised verification")
    reference_map = policy.get("reference_source_by_agreement")
    _require(isinstance(reference_map, dict), "policy reference_source_by_agreement must be an object")
    _require(all(v is None or v in sources for v in reference_map.values()), "policy references unknown source")
    files = {"environment.json": environment_file}
    for doc in indexes["documents"].values():
        label = f"document {doc['id']}"
        sourced(doc, label)
        _text(doc.get("agreement_id"), f"{label}.agreement_id")
        _require(doc.get("class_id") in indexes["document_classes"], f"{label} unknown class")
        _typed_metadata(doc.get("metadata"), indexes["document_classes"][doc["class_id"]], label)
        _require(doc["metadata"].get("agreement_id") == doc["agreement_id"], f"{label} agreement metadata differs from agreement_id")
        relationships = doc.get("relationships")
        _require(isinstance(relationships, dict), f"{label}.relationships must be an object")
        for key, collection in (("apartment_id", "apartments"), ("property_id", "properties"), ("agreement_document_id", "documents")):
            if key in relationships:
                _require(relationships[key] in indexes[collection], f"{label} unknown {key}")
        if doc["class_id"] == "rental_agreement":
            _require("apartment_id" in relationships and "property_id" in relationships, f"{label} missing rental agreement relationships")
            apartment = indexes["apartments"][relationships["apartment_id"]]
            _require(apartment["property_id"] == relationships["property_id"], f"{label} property/apartment relationships inconsistent")
        workflow = doc.get("workflow")
        _require(isinstance(workflow, dict) and workflow.get("state") in indexes["workflow_states"], f"{label} unknown workflow state")
        event = workflow.get("approval_event")
        if workflow["state"] == "approved":
            _require(isinstance(event, dict), f"{label} approved state requires approval event")
        if event is not None:
            _require(isinstance(event, dict), f"{label} approval event must be an object")
            _text(event.get("id"), f"{label} approval event id")
            _text(event.get("actor_label"), f"{label} approval actor label")
            _timestamp(event.get("at"), f"{label} approval event timestamp")
        acl = doc.get("acl")
        _require(isinstance(acl, dict), f"{label}.acl must be an object")
        for rule in ("allow_read_roles", "deny_read_roles"):
            roles = acl.get(rule)
            _require(isinstance(roles, list) and all(isinstance(r, str) and r for r in roles), f"{label}.acl.{rule} must be string list")
        source_file = _read(root, doc.get("content_path"))
        files[source_file["path"]] = source_file
    for record in indexes["erp_records"].values():
        _text(record.get("agreement_id"), "ERP agreement_id")
        _require(record.get("apartment_id") in indexes["apartments"], "ERP record references unknown apartment")
    for case in indexes["cases"].values():
        complaint = case.get("complaint")
        _require(isinstance(complaint, dict), "case complaint must be an object")
        for field in ("text", "agreement_id"):
            _text(complaint.get(field), f"complaint {field}")
        _require(complaint.get("requester_id") in indexes["principals"], "complaint references unknown requester")
        _require(complaint.get("apartment_id") in indexes["apartments"], "complaint references unknown apartment")
    return env, indexes, [files[k] for k in sorted(files)]


def _load(fixture_dir):
    try:
        return _load_validated(fixture_dir)
    except (TypeError, KeyError, AttributeError) as exc:
        raise ValueError(f"invalid fixture structure: {exc}") from exc


def case_ids(fixture_dir: Path) -> list[str]:
    """Return case IDs after validating the complete frozen environment."""
    _, indexes, _ = _load(fixture_dir)
    return list(indexes["cases"])


def replay(fixture_dir: Path, case_id: str) -> dict:
    """Investigate one complaint using an authorised, pre-exported snapshot.

    Candidate joins use agreement identifiers, independently of the requester view.
    Missing or ambiguous candidates/ERP records are explicitly inconclusive.
    """
    env, indexes, files = _load(fixture_dir)
    _require(case_id in indexes["cases"], f"unknown case_id: {case_id}")
    complaint = indexes["cases"][case_id]["complaint"]
    agreement = complaint["agreement_id"]
    requester = indexes["principals"][complaint["requester_id"]]
    docs = [d for d in env["documents"] if d["agreement_id"] == agreement and d["class_id"] == "rental_agreement"]
    erp_records = [r for r in env["erp_records"] if r["agreement_id"] == agreement]
    evidence, checks, findings, inferences = [], [], [], []
    blockers, visible = [], []
    unknowns = ["Snapshots do not establish current live system state."]

    def observe(kind, source_id, record_id, locator, observed):
        identity = f"evidence-{len(evidence) + 1:03d}"
        evidence.append({"id": identity, "kind": kind, "source_id": source_id,
                         "source_record_id": record_id, "locator": locator, "observed": observed})
        return identity

    def check(identity, name, status, ids, observed, expected):
        checks.append({"id": identity, "name": name, "status": status,
                       "evidence_ids": ids, "observed": observed, "expected": expected})

    def finding(code, statement, ids):
        findings.append({"code": code, "statement": statement, "evidence_ids": ids})

    policy = env["comparison_policy"]
    policy_e = observe("comparison_policy", policy["source_id"], policy["source_record_id"],
                       "environment.json#/comparison_policy", policy)
    scope_e = observe("investigator_scope", env["investigator"]["source_id"],
                      env["investigator"]["principal_id"], "environment.json#/investigator", env["investigator"])
    doc_evidence = {}
    for doc in docs:
        pointer = f"environment.json#/documents/{env['documents'].index(doc)}"
        ids = []
        for kind, suffix, observed in (("document_metadata", "", {"id": doc["id"], "agreement_id": doc["agreement_id"], "class_id": doc["class_id"], "metadata": doc["metadata"]}),
                                       ("relationships", "/relationships", doc["relationships"]), ("workflow", "/workflow", doc["workflow"])):
            ids.append(observe(kind, doc["source_id"], doc["source_record_id"], pointer + suffix, observed))
        roles = set(requester["roles"])
        denied = sorted(roles.intersection(doc["acl"]["deny_read_roles"]))
        allowed = sorted(roles.intersection(doc["acl"]["allow_read_roles"]))
        readable = bool(allowed) and not denied
        access = {"requester_id": requester["id"], "requester_roles": requester["roles"], "rules": doc["acl"],
                  "matching_allow_roles": allowed, "matching_deny_roles": denied, "deny_overrides": True, "can_read": readable}
        access_e = observe("requester_access", doc["source_id"], doc["source_record_id"], pointer + "/acl", access)
        ids.append(access_e)
        content = next(f for f in files if f["path"] == Path(doc["content_path"]).as_posix())
        ids.append(observe("content_existence", doc["source_id"], doc["source_record_id"], content["path"],
                           {"document_id": doc["id"], "exists_in_export": True, "sha256": content["sha256"], "bytes": len(content["content"].encode("utf-8"))}))
        doc_evidence[doc["id"]] = ids
        state = doc["workflow"]["state"]
        relationship_match = doc["relationships"]["apartment_id"] == complaint["apartment_id"]
        check(f"access-{doc['id']}", "Requester has read access under deny-overrides rules", "pass" if readable else "fail", [access_e], readable, True)
        check(f"workflow-{doc['id']}", "Current workflow state is approved", "pass" if state == "approved" else "fail", [ids[2]], state, "approved")
        if readable and relationship_match and state == "approved":
            visible.append(doc["id"])
        if not readable:
            blockers.append("permission_blocked")
            finding("permission_blocked", "The agreement relationship is inspectable in the authorised export, but requester read access is denied by the fixture ACL.", [access_e, scope_e, ids[1]])
        if state != "approved":
            blockers.append("workflow_excluded")
            finding("workflow_excluded", "The current workflow state excludes the document from the requester's approved-document view.", [ids[2]])
        if not relationship_match:
            blockers.append("apartment_filter_mismatch")
            finding("apartment_filter_mismatch", f"The document's {doc['relationships']['apartment_id']} relationship excludes it from the requester's {complaint['apartment_id']} apartment view.", [ids[1]])
        check(f"apartment-view-{doc['id']}", "Document relationship matches requested apartment", "pass" if relationship_match else "fail", [ids[1]], doc["relationships"]["apartment_id"], complaint["apartment_id"])

    for attachment in env["documents"]:
        if attachment["agreement_id"] == agreement and attachment["class_id"] != "rental_agreement":
            observe("related_document", attachment["source_id"], attachment["source_record_id"],
                    f"environment.json#/documents/{env['documents'].index(attachment)}", attachment)
    erp_evidence = []
    for record in erp_records:
        erp_evidence.append(observe("erp_record", record["source_id"], record["source_record_id"],
                                    f"environment.json#/erp_records/{env['erp_records'].index(record)}", record))
    all_doc_evidence = [identity for ids in doc_evidence.values() for identity in ids]
    check("candidate-count", "Exactly one exported rental agreement matches the agreement identifier", "pass" if len(docs) == 1 else "unknown", all_doc_evidence + [scope_e], len(docs), 1)
    check("erp-count", "Exactly one ERP record matches the agreement identifier", "pass" if len(erp_records) == 1 else "unknown", erp_evidence + [policy_e], len(erp_records), 1)
    if len(docs) != 1:
        blockers.append("candidate_unresolved")
        finding("candidate_unresolved", "The export does not establish one unique candidate agreement; no document relationship is selected for correction.", all_doc_evidence + [scope_e])
        unknowns.append(f"Expected one candidate in the export; observed {len(docs)}. Absence from an export does not establish nonexistence.")
    if len(erp_records) != 1:
        blockers.append("erp_unresolved")
        finding("erp_unresolved", "A unique ERP comparison record is unavailable; the relationship comparison is inconclusive.", erp_evidence + [policy_e])
        unknowns.append(f"Expected one ERP record; observed {len(erp_records)}.")
    mismatch = False
    authority = policy["reference_source_by_agreement"].get(agreement)
    if len(docs) == len(erp_records) == 1:
        doc, record = docs[0], erp_records[0]
        ids = [doc_evidence[doc["id"]][1], *erp_evidence, policy_e]
        mismatch = doc["relationships"]["apartment_id"] != record["apartment_id"]
        check("relationship-comparison", "DMS and ERP apartment relationships agree", "fail" if mismatch else "pass", ids,
              {"dms_apartment_id": doc["relationships"]["apartment_id"], "erp_apartment_id": record["apartment_id"]}, "equal apartment identifiers")
        if mismatch:
            unknowns.extend(["Who introduced the discrepancy, when it arose and why are not established.",
                             "The signed agreement, source records and an authorised reviewer have not established the correct apartment for a correction."])
            if authority == record["source_id"]:
                finding("relationship_mismatch_requires_verification", "The agreement exists with a DMS apartment relationship different from the ERP record. The fictional policy nominates ERP as a verification reference; it does not authorise a correction.", ids + [doc_evidence[doc["id"]][2], doc_evidence[doc["id"]][4]])
            else:
                finding("authority_unresolved", "DMS and ERP disagree and the supplied policy does not establish an authoritative comparison source for this agreement.", ids)
                blockers.append("authority_unresolved")
                unknowns.append("The authoritative apartment value and responsible business owner remain unresolved.")
            inferences.extend([
                {"statement": "A mistaken apartment selection during DMS entry could explain the discrepancy.", "status": "unconfirmed", "evidence_ids": ids},
                {"statement": "A stale ERP record or an incompletely recorded reassignment could also explain the discrepancy.", "status": "unconfirmed", "evidence_ids": ids},
                {"statement": "An incorrect cross-system agreement identifier mapping could associate records that should not be compared.", "status": "unconfirmed", "evidence_ids": ids},
            ])
    clean = len(docs) == len(erp_records) == 1 and not mismatch and bool(visible) and not blockers
    if clean:
        finding("no_retrieval_failure", "The agreed apartment relationship, approved state and requester permissions return the expected document in the simulated view.", all_doc_evidence + erp_evidence)
    required = not clean
    if mismatch and authority is None:
        action = "Ask the housing records owner to establish authority between DMS and ERP, inspect the underlying agreement and record a decision before proposing any correction."
        question = "Which source and apartment value should govern, and what verified evidence supports a subsequent authorised change?"
    elif mismatch:
        action = "An authorised housing records owner should verify the agreement against ERP and source records, decide the correct apartment, and separately authorise any metadata correction."
        question = "Does verification establish the correct apartment relationship, and should a separately controlled correction be authorised?"
    elif "candidate_unresolved" in blockers or "erp_unresolved" in blockers:
        action = "Obtain a complete, uniquely identified source export before deciding whether any relationship correction is needed."
        question = "Which candidate and ERP record are the verified records for this agreement?"
    elif "permission_blocked" in blockers:
        action = "Ask the access owner to review whether the requester has a legitimate need for access; keep the verified apartment relationship unchanged."
        question = "Should the access owner grant access under the organisation's policy?"
    elif "workflow_excluded" in blockers:
        action = "Ask the workflow owner to verify whether this agreement should be approved through the existing business process."
        question = "Is the document's current workflow state correct?"
    elif "apartment_filter_mismatch" in blockers:
        action = "Ask the housing records owner to verify the complaint's apartment and agreement identifiers against the agreeing source records before proposing any change."
        question = "Are the complaint's apartment and agreement identifiers correct, and which retrieval context should apply?"
    else:
        action = "No corrective action is indicated by this snapshot; retain the successful retrieval evidence."
        question = "No human decision is required for this clean replay."
    return {"schema_version": "found-in-meta.investigation/v1", "case_id": case_id,
            "replay": {"snapshot_at": env["snapshot_at"], "synthetic": True, "audience": "authorised_investigator", "tool_version": "0.1.0"},
            "complaint": complaint, "sources": env["sources"], "evidence": evidence, "checks": checks,
            "findings": findings, "unknowns": unknowns, "inferences": inferences,
            "proposed_next_action": action,
            "required_human_decision": {"required": required, "question": question, "role": "housing_records_owner" if mismatch or any(b in blockers for b in ("candidate_unresolved", "erp_unresolved", "apartment_filter_mismatch")) else "access_or_workflow_owner" if required else "none"},
            "retrieval": {"matched_document_ids": [d["id"] for d in docs], "requester_visible_document_ids": visible, "blockers": sorted(set(blockers))},
            "changes_applied": [], "source_files": files}
