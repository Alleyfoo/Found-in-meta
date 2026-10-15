import json
from pathlib import Path
import shutil

from found_in_meta.cli import main
from found_in_meta.engine import case_ids, default_fixture_dir


def test_replay_all_writes_portable_json_and_complete_readable_reports(tmp_path, capsys):
    assert main(["--all", "--out", str(tmp_path)]) == 0
    for case_id in case_ids(default_fixture_dir()):
        directory = tmp_path / case_id
        bundle_bytes = (directory / "bundle.json").read_bytes()
        bundle = json.loads(bundle_bytes)
        report = (directory / "report.md").read_text(encoding="utf-8")
        assert bundle["complaint"]["text"] in report
        assert bundle["case_id"] in report
        for section in ("Confirmed findings", "Checks performed", "Unknowns and competing explanations",
                        "Proposed next action", "Required human decision", "Observed evidence"):
            assert section in report
        assert "Changes applied: none" in report
        assert "authorised investigator" in report
        for finding in bundle["findings"]:
            assert finding["code"] in report
        for evidence in bundle["evidence"]:
            assert evidence["id"] in report
            assert str(evidence["source_record_id"]) in report
        for source in bundle["source_files"]:
            assert source["sha256"] in report
    first_run = {file.relative_to(tmp_path): file.read_bytes() for file in tmp_path.rglob("*") if file.is_file()}
    assert main(["--all", "--out", str(tmp_path)]) == 0
    assert first_run == {file.relative_to(tmp_path): file.read_bytes() for file in tmp_path.rglob("*") if file.is_file()}
    assert "relationship_mismatch_requires_verification" in capsys.readouterr().out


def test_unknown_case_produces_actionable_error_without_output(tmp_path, capsys):
    import pytest

    with pytest.raises(SystemExit) as error:
        main(["--case", "unknown", "--out", str(tmp_path / "out")])
    assert error.value.code == 2
    assert "Investigation could not run" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_cli_refuses_to_write_into_source_fixtures(tmp_path):
    import pytest

    fixture_dir = tmp_path / "fixtures"
    shutil.copytree(default_fixture_dir(), fixture_dir)
    before = {file.relative_to(fixture_dir): file.read_bytes() for file in fixture_dir.rglob("*") if file.is_file()}
    with pytest.raises(SystemExit) as error:
        main(["--fixtures", str(fixture_dir), "--out", str(fixture_dir)])
    assert error.value.code == 2
    assert before == {file.relative_to(fixture_dir): file.read_bytes() for file in fixture_dir.rglob("*") if file.is_file()}


def test_embedded_sources_can_reproduce_artifacts_without_original_fixtures(tmp_path):
    initial_output = tmp_path / "initial"
    assert main(["--all", "--out", str(initial_output)]) == 0
    bundle = json.loads((initial_output / "a14_relationship" / "bundle.json").read_bytes())
    restored = tmp_path / "restored"
    for source in bundle["source_files"]:
        target = restored / source["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source["content"].encode("utf-8"))
    replay_output = tmp_path / "replayed"
    assert main(["--all", "--fixtures", str(restored), "--out", str(replay_output)]) == 0
    for artifact in initial_output.rglob("*"):
        if artifact.is_file():
            assert artifact.read_bytes() == (replay_output / artifact.relative_to(initial_output)).read_bytes()
