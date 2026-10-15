"""Replay the fixed investigation and write local evidence artifacts."""

import argparse
import json
from pathlib import Path
import re

from .engine import case_ids, default_fixture_dir, replay
from .report import render_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--case", default="a14_relationship", help="case ID (default: a14_relationship)")
    selection.add_argument("--all", action="store_true", help="replay the first case and all three controls")
    parser.add_argument("--fixtures", type=Path, default=default_fixture_dir(), help="frozen fixture directory")
    parser.add_argument("--out", type=Path, default=Path("output/demo"), help="artifact output directory")
    args = parser.parse_args(argv)
    try:
        fixture_dir, output_dir = args.fixtures.resolve(), args.out.resolve()
        if output_dir == fixture_dir or fixture_dir in output_dir.parents:
            raise ValueError("output directory must be outside the source fixtures")
        selected = case_ids(fixture_dir) if args.all else [args.case]
        if any(re.fullmatch(r"[a-z0-9_]+", item) is None for item in selected):
            raise ValueError("case IDs must contain only lowercase letters, digits and underscores")
        bundles = [replay(fixture_dir, item) for item in selected]
        for bundle in bundles:
            destination = output_dir / bundle["case_id"]
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "bundle.json").write_text(
                json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8", newline="\n",
            )
            (destination / "report.md").write_text(render_report(bundle), encoding="utf-8", newline="\n")
            findings = ", ".join(item["code"] for item in bundle["findings"])
            print(f"{bundle['case_id']}: {findings}\n  {destination / 'report.md'}")
    except (ValueError, OSError) as error:
        parser.exit(2, f"Investigation could not run: {error}\n")
    return 0
