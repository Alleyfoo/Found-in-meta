"""Evidence integrity and retrieval outcomes for the synthetic investigation."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from found_in_meta.engine import case_ids, default_fixture_dir, replay


EXPECTED_FINDINGS = {
    "a14_relationship": "relationship_mismatch_requires_verification",
    "permission_blocked": "permission_blocked",
    "authority_unresolved": "authority_unresolved",
    "clean": "no_retrieval_failure",
}


def finding_codes(bundle: dict) -> set[str]:
    return {finding["code"] for finding in bundle["findings"]}


def snapshot_tree(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file()
    }


def document_for_case(environment: dict, case_id: str) -> dict:
    case = next(case for case in environment["cases"] if case["id"] == case_id)
    return next(
        document for document in environment["documents"]
        if document["agreement_id"] == case["complaint"]["agreement_id"]
        and document["class_id"] == "rental_agreement"
    )


def evidence_of_kind(bundle: dict, kind: str) -> dict:
    matches = [item for item in bundle["evidence"] if item["kind"] == kind]
    assert len(matches) == 1
    return matches[0]["observed"]


def resolve_pointer(value, pointer: str):
    if not pointer:
        return value
    assert pointer.startswith("/")
    for component in pointer[1:].split("/"):
        key = component.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


@pytest.fixture
def fixtures() -> Path:
    return default_fixture_dir()


@pytest.fixture
def editable_environment(tmp_path: Path, fixtures: Path):
    fixture_dir = tmp_path / "fixtures"
    shutil.copytree(fixtures, fixture_dir)
    environment = json.loads((fixture_dir / "environment.json").read_text(encoding="utf-8"))

    def save() -> Path:
        (fixture_dir / "environment.json").write_text(
            json.dumps(environment, indent=2) + "\n", encoding="utf-8"
        )
        return fixture_dir

    return environment, save


def test_four_cases_produce_distinct_findings(fixtures: Path):
    identifiers = case_ids(fixtures)
    assert len(identifiers) == len(EXPECTED_FINDINGS)
    assert set(identifiers) == set(EXPECTED_FINDINGS)
    for case_id, expected_code in EXPECTED_FINDINGS.items():
        bundle = replay(fixtures, case_id)
        assert expected_code in finding_codes(bundle)
        assert not (set(EXPECTED_FINDINGS.values()) - {expected_code}) & finding_codes(bundle)


@pytest.mark.parametrize("case_id", EXPECTED_FINDINGS)
def test_bundle_preserves_decision_and_evidence_contract(fixtures: Path, case_id: str):
    bundle = replay(fixtures, case_id)
    assert bundle["schema_version"] == "found-in-meta.investigation/v1"
    assert bundle["case_id"] == case_id
    assert bundle["replay"]["synthetic"] is True
    assert bundle["replay"]["audience"] == "authorised_investigator"
    assert bundle["replay"]["snapshot_at"]
    assert bundle["replay"]["tool_version"]
    environment = json.loads((fixtures / "environment.json").read_text(encoding="utf-8"))
    original_case = next(case for case in environment["cases"] if case["id"] == case_id)
    assert bundle["complaint"] == original_case["complaint"]
    assert set(bundle["complaint"]) >= {
        "text", "requester_id", "apartment_id", "agreement_id"
    }
    assert bundle["changes_applied"] == []
    assert bundle["proposed_next_action"]
    assert set(bundle["required_human_decision"]) >= {"required", "question", "role"}
    assert isinstance(bundle["required_human_decision"]["required"], bool)

    evidence_ids = [item["id"] for item in bundle["evidence"]]
    assert evidence_ids
    assert len(set(evidence_ids)) == len(evidence_ids)
    for item in bundle["evidence"]:
        assert set(item) >= {
            "id", "kind", "source_id", "source_record_id", "locator", "observed"
        }
    for collection in ("checks", "findings", "inferences"):
        for item in bundle[collection]:
            assert item["evidence_ids"]
            assert set(item["evidence_ids"]) <= set(evidence_ids)
    for check in bundle["checks"]:
        assert set(check) >= {"id", "name", "status", "observed", "expected"}
        assert check["status"] in {"pass", "fail", "unknown"}
    for inference in bundle["inferences"]:
        assert inference["status"] == "unconfirmed"
    assert all(isinstance(unknown, str) and unknown for unknown in bundle["unknowns"])


def test_first_case_demonstrates_approved_existing_document_hidden_by_wrong_relationship(fixtures: Path):
    bundle = replay(fixtures, "a14_relationship")
    metadata = evidence_of_kind(bundle, "document_metadata")
    assert metadata["id"] == "DOC-001"
    assert metadata["agreement_id"] == bundle["complaint"]["agreement_id"] == "AGR-001"
    assert metadata["metadata"]["signed"] is True
    assert evidence_of_kind(bundle, "relationships")["apartment_id"] == "A41"
    assert evidence_of_kind(bundle, "erp_record")["apartment_id"] == "A14"
    assert bundle["complaint"]["apartment_id"] == "A14"

    workflow = evidence_of_kind(bundle, "workflow")
    assert workflow["state"] == "approved"
    assert workflow["approval_event"]["id"] == "APPROVAL-001"
    assert evidence_of_kind(bundle, "content_existence")["exists_in_export"] is True
    assert evidence_of_kind(bundle, "requester_access")["can_read"] is True
    assert bundle["retrieval"]["matched_document_ids"] == ["DOC-001"]
    assert bundle["retrieval"]["requester_visible_document_ids"] == []
    assert bundle["retrieval"]["blockers"] == ["apartment_filter_mismatch"]
    assert "permission_blocked" not in finding_codes(bundle)
    assert "workflow_excluded" not in finding_codes(bundle)
    appendix = evidence_of_kind(bundle, "related_document")
    assert appendix["relationships"]["agreement_document_id"] == "DOC-001"


@pytest.mark.parametrize("case_id", EXPECTED_FINDINGS)
def test_raw_snapshots_are_portable_complete_and_authentic(fixtures: Path, case_id: str):
    bundle = replay(fixtures, case_id)
    source_files = bundle["source_files"]
    assert source_files
    paths = [source["path"] for source in source_files]
    assert len(set(paths)) == len(paths)
    assert "environment.json" in paths
    for source in source_files:
        relative = Path(source["path"])
        assert not relative.is_absolute()
        assert ".." not in relative.parts
        original = (fixtures / relative).read_bytes()
        assert source["content"].encode("utf-8") == original
        assert source["sha256"] == hashlib.sha256(original).hexdigest()


@pytest.mark.parametrize("case_id", EXPECTED_FINDINGS)
def test_evidence_locators_and_observations_resolve_to_preserved_sources(fixtures: Path, case_id: str):
    bundle = replay(fixtures, case_id)
    source_ids = {source["id"] for source in bundle["sources"]}
    source_files = {source["path"]: source for source in bundle["source_files"]}
    environment = json.loads(source_files["environment.json"]["content"])
    source_records = {
        record["source_record_id"]: record
        for collection in environment.values() if isinstance(collection, list)
        for record in collection
        if isinstance(record, dict) and "source_record_id" in record
    }
    policy = environment["comparison_policy"]
    source_records[policy["source_record_id"]] = policy
    for source in bundle["sources"]:
        assert source["snapshot_id"]
        assert source["captured_at"]
        assert source["provenance"]
    for evidence in bundle["evidence"]:
        assert evidence["source_id"] in source_ids
        if evidence["kind"] == "investigator_scope":
            assert evidence["source_record_id"] == environment["investigator"]["principal_id"]
        else:
            record = source_records[evidence["source_record_id"]]
            assert evidence["source_id"] == record["source_id"]
        file_path, fragment_separator, pointer = evidence["locator"].partition("#")
        assert file_path in source_files
        source = source_files[file_path]
        observed = evidence["observed"]
        if not fragment_separator:
            assert evidence["kind"] == "content_existence"
            assert observed["sha256"] == source["sha256"]
            assert observed["bytes"] == len(source["content"].encode("utf-8"))
            continue
        source_value = resolve_pointer(json.loads(source["content"]), pointer)
        kind = evidence["kind"]
        if kind == "document_metadata":
            assert observed == {key: source_value[key] for key in observed}
        elif kind in {"relationships", "workflow"}:
            # These are exact raw fields, even when a locator selects the parent document.
            assert observed == source_value.get(kind, source_value)
        elif kind == "requester_access":
            assert observed["rules"] == source_value
            roles = set(observed["requester_roles"])
            allowed = sorted(roles & set(source_value["allow_read_roles"]))
            denied = sorted(roles & set(source_value["deny_read_roles"]))
            assert observed["matching_allow_roles"] == allowed
            assert observed["matching_deny_roles"] == denied
            assert observed["can_read"] is (bool(allowed) and not denied)
        else:
            assert observed == source_value


def test_replay_is_deterministic_and_does_not_modify_inputs(fixtures: Path):
    before = snapshot_tree(fixtures)
    for case_id in case_ids(fixtures):
        first = json.dumps(replay(fixtures, case_id), sort_keys=True).encode("utf-8")
        second = json.dumps(replay(fixtures, case_id), sort_keys=True).encode("utf-8")
        assert first == second
    assert snapshot_tree(fixtures) == before


def test_first_case_keeps_uncertain_causes_separate_from_required_verification(fixtures: Path):
    bundle = replay(fixtures, "a14_relationship")
    assert bundle["unknowns"]
    assert bundle["inferences"]
    assert all(item["status"] == "unconfirmed" for item in bundle["inferences"])
    decision = bundle["required_human_decision"]
    assert decision["required"] is True
    assert decision["question"]
    assert decision["role"]
    assert bundle["changes_applied"] == []


def test_conflicting_sources_without_authority_require_a_human_decision(fixtures: Path):
    bundle = replay(fixtures, "authority_unresolved")
    assert "authority_unresolved" in finding_codes(bundle)
    assert "relationship_mismatch_requires_verification" not in finding_codes(bundle)
    assert bundle["required_human_decision"]["required"] is True
    assert bundle["unknowns"]
    assert bundle["changes_applied"] == []


def test_permission_control_has_correct_relationship_and_explicit_deny_overrides_allow(fixtures: Path):
    bundle = replay(fixtures, "permission_blocked")
    assert evidence_of_kind(bundle, "relationships")["apartment_id"] == "A22"
    assert evidence_of_kind(bundle, "erp_record")["apartment_id"] == "A22"
    access = evidence_of_kind(bundle, "requester_access")
    assert access["matching_allow_roles"] == ["property_manager"]
    assert access["matching_deny_roles"] == ["property_manager"]
    assert access["deny_overrides"] is True
    assert access["can_read"] is False
    assert bundle["retrieval"]["matched_document_ids"] == ["DOC-002"]
    assert bundle["retrieval"]["requester_visible_document_ids"] == []
    assert bundle["retrieval"]["blockers"] == ["permission_blocked"]
    assert bundle["required_human_decision"]["required"] is True


def test_clean_case_has_no_blockers_or_required_decision(fixtures: Path):
    bundle = replay(fixtures, "clean")
    assert bundle["retrieval"]["requester_visible_document_ids"]
    assert bundle["retrieval"]["blockers"] == []
    assert bundle["required_human_decision"]["required"] is False


def test_unknown_case_is_rejected(fixtures: Path):
    with pytest.raises(ValueError):
        replay(fixtures, "not-a-real-case")


@pytest.mark.parametrize("case_id", ["clean", "a14_relationship"])
def test_draft_state_is_a_separate_retrieval_failure(editable_environment, case_id: str):
    environment, save = editable_environment
    document = document_for_case(environment, case_id)
    document["workflow"] = {"state": "draft", "approval_event": None}
    bundle = replay(save(), case_id)
    assert "workflow_excluded" in finding_codes(bundle)
    assert "no_retrieval_failure" not in finding_codes(bundle)
    assert "workflow_excluded" in bundle["retrieval"]["blockers"]
    assert bundle["retrieval"]["requester_visible_document_ids"] == []
    assert evidence_of_kind(bundle, "workflow") == {"state": "draft", "approval_event": None}
    assert all("approved agreement exists" not in finding["statement"].lower()
               for finding in bundle["findings"])
    assert bundle["required_human_decision"]["required"] is True
    assert bundle["changes_applied"] == []


def test_duplicate_candidates_are_inconclusive_instead_of_silently_selected(editable_environment):
    environment, save = editable_environment
    original = document_for_case(environment, "a14_relationship")
    duplicate = deepcopy(original)
    duplicate["id"] = "DOC-DUPLICATE"
    duplicate["source_record_id"] = "dms:DOC-DUPLICATE:v1"
    environment["documents"].append(duplicate)
    bundle = replay(save(), "a14_relationship")
    assert "candidate_unresolved" in finding_codes(bundle)
    assert "relationship_mismatch_requires_verification" not in finding_codes(bundle)
    assert set(bundle["retrieval"]["matched_document_ids"]) == {original["id"], duplicate["id"]}
    candidate_check = next(check for check in bundle["checks"] if check["id"] == "candidate-count")
    assert candidate_check["status"] == "unknown"
    assert candidate_check["observed"] == 2
    assert bundle["required_human_decision"]["required"] is True
    assert bundle["changes_applied"] == []


def test_missing_erp_record_is_inconclusive_instead_of_manufacturing_a_comparison(editable_environment):
    environment, save = editable_environment
    agreement_id = document_for_case(environment, "a14_relationship")["agreement_id"]
    environment["erp_records"] = [
        record for record in environment["erp_records"] if record["agreement_id"] != agreement_id
    ]
    bundle = replay(save(), "a14_relationship")
    assert "erp_unresolved" in finding_codes(bundle)
    assert "relationship_mismatch_requires_verification" not in finding_codes(bundle)
    assert "authority_unresolved" not in finding_codes(bundle)
    assert bundle["required_human_decision"]["required"] is True
    assert bundle["changes_applied"] == []


def test_consistent_sources_disagreeing_with_complaint_still_require_verification(editable_environment):
    environment, save = editable_environment
    document = document_for_case(environment, "a14_relationship")
    record = next(record for record in environment["erp_records"]
                  if record["agreement_id"] == document["agreement_id"])
    record["apartment_id"] = document["relationships"]["apartment_id"]
    bundle = replay(save(), "a14_relationship")
    assert "apartment_filter_mismatch" in finding_codes(bundle)
    assert "relationship_mismatch_requires_verification" not in finding_codes(bundle)
    assert "no_retrieval_failure" not in finding_codes(bundle)
    assert bundle["retrieval"]["requester_visible_document_ids"] == []
    assert bundle["required_human_decision"]["required"] is True
    assert "no human decision" not in bundle["required_human_decision"]["question"].lower()
    action = bundle["proposed_next_action"].lower()
    assert any(term in action for term in ("verif", "query", "complaint"))
    assert bundle["changes_applied"] == []


@pytest.mark.parametrize("field,value", [
    ("signed", "yes"),
    ("revision", True),
    ("effective_date", "2026-02-30"),
])
def test_invalid_typed_metadata_is_rejected(editable_environment, field: str, value):
    environment, save = editable_environment
    document_for_case(environment, "a14_relationship")["metadata"][field] = value
    with pytest.raises(ValueError):
        replay(save(), "a14_relationship")


def test_broken_apartment_relationship_is_rejected(editable_environment):
    environment, save = editable_environment
    document_for_case(environment, "a14_relationship")["relationships"]["apartment_id"] = "A-NOT-IN-EXPORT"
    with pytest.raises(ValueError):
        replay(save(), "a14_relationship")


def test_duplicate_object_identifier_is_rejected(editable_environment):
    environment, save = editable_environment
    environment["documents"].append(deepcopy(document_for_case(environment, "a14_relationship")))
    with pytest.raises(ValueError):
        replay(save(), "a14_relationship")
