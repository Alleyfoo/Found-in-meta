"""Render the investigation artifact without adding claims or decisions."""

import json


def _json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)


def render_report(bundle: dict) -> str:
    """Return a deterministic Markdown report for an authorised investigator."""
    complaint = bundle["complaint"]
    retrieval = bundle["retrieval"]
    lines = [
        "# Found in meta",
        "",
        "*When the document exists. So why can't anyone find it?*",
        "",
        f"Case: `{bundle['case_id']}` · Snapshot: {bundle['replay']['snapshot_at']}",
        "",
        "Synthetic investigation for an authorised investigator. The evidence export includes",
        "documents the requester may not read. This report is not a requester-facing search result.",
        "",
        "## Original complaint",
        "",
        complaint["text"],
        "",
        f"Requester: `{complaint['requester_id']}`; apartment: `{complaint['apartment_id']}`; "
        f"agreement cross-reference: `{complaint['agreement_id']}`.",
        "",
        "## Confirmed findings",
        "",
    ]
    for finding in bundle["findings"]:
        lines += [f"- **{finding['code']}**: {finding['statement']} "
                  f"Evidence: {', '.join(finding['evidence_ids'])}."]
    lines += [
        "",
        f"Documents matched by agreement ID: {', '.join(retrieval['matched_document_ids']) or '(none)' }.",
        f"Documents returned by the requester's apartment view: "
        f"{', '.join(retrieval['requester_visible_document_ids']) or '(none)' }.",
        f"View blockers: {', '.join(retrieval['blockers']) or '(none)' }.",
        "",
        "## Checks performed",
        "",
    ]
    for check in bundle["checks"]:
        lines += [
            f"### {check['id']}: {check['name']} — {check['status']}",
            "",
            f"Evidence: {', '.join(check['evidence_ids'])}.",
            "",
            "```json",
            _json({"expected": check["expected"], "observed": check["observed"]}),
            "```",
            "",
        ]
    lines += ["## Unknowns and competing explanations", ""]
    lines += [f"- {unknown}" for unknown in bundle["unknowns"]] or ["- None within the snapshot checks."]
    lines += [""]
    for inference in bundle["inferences"]:
        lines += [f"- **{inference['status']} explanation:** {inference['statement']} "
                  f"Evidence considered: {', '.join(inference['evidence_ids'])}."]
    decision = bundle["required_human_decision"]
    lines += [
        "",
        "## Proposed next action",
        "",
        bundle["proposed_next_action"],
        "",
        "## Required human decision",
        "",
        f"Required: {'yes' if decision['required'] else 'no'}. Role: {decision['role']}.",
        "",
        decision["question"],
        "",
        "Changes applied: none. Recorded workflow approval does not authorise a metadata correction.",
        "",
        "## Sources and provenance",
        "",
        "```json",
        _json(bundle["sources"]),
        "```",
        "",
        "## Observed evidence",
        "",
        "These observations describe the frozen export, not independently verified live records.",
        "",
    ]
    for evidence in bundle["evidence"]:
        lines += [
            f"### {evidence['id']}: {evidence['kind']}",
            "",
            f"Source: `{evidence['source_id']}`; source record: `{evidence['source_record_id']}`; "
            f"locator: `{evidence['locator']}`.",
            "",
            "```json",
            _json(evidence["observed"]),
            "```",
            "",
        ]
    lines += ["## Preserved source artifacts", ""]
    for source in bundle["source_files"]:
        lines += [f"- `{source['path']}` — SHA-256 `{source['sha256']}`"]
    lines += [
        "",
        "Exact UTF-8 source contents are embedded in bundle.json. Hashes identify these synthetic",
        "artifacts; they do not prove external authenticity or source authority.",
        "",
    ]
    return "\n".join(lines)
