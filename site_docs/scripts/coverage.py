"""Coverage analysis: verify all indicators have template coverage.

Reports:
- Indicators with zero template references
- Templates per indicator distribution
- Coverage percentage by frame

Usage:
  python scripts/coverage.py          # Report only (always exit 0)
  python scripts/coverage.py --strict # Fail if coverage < 100%

Scope: local QA and planning tool.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from ruamel.yaml import YAML

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = YAML(typ="safe")


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = YAML_LOADER.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"Expected mapping at root: {path}")
    return data


def main() -> int:
    strict_mode = "--strict" in sys.argv

    # Load indicators
    indicators_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "indicators.yaml")
    indicators = {i["id"]: i for i in indicators_doc.get("indicators", []) if isinstance(i, dict) and "id" in i}

    # Load templates
    templates_doc = load_yaml(WORKSPACE_ROOT / "templates" / "comment_templates.yaml")
    templates = templates_doc.get("templates", [])

    # Count references
    indicator_refs: dict[str, list[str]] = defaultdict(list)
    for tmpl in templates:
        if not isinstance(tmpl, dict):
            continue
        tid = tmpl.get("id", "<missing>")
        for ind_id in tmpl.get("indicators", []) or []:
            indicator_refs[ind_id].append(tid)

    # Analyze coverage
    uncovered: list[str] = []
    coverage_by_frame: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "covered": 0})

    print("=" * 60)
    print("INDICATOR COVERAGE REPORT")
    print("=" * 60)
    print()

    for ind_id, ind in sorted(indicators.items()):
        frame = ind.get("frame", "unknown")
        coverage_by_frame[frame]["total"] += 1

        ref_count = len(indicator_refs.get(ind_id, []))
        if ref_count == 0:
            uncovered.append(ind_id)
        else:
            coverage_by_frame[frame]["covered"] += 1

        status = "OK" if ref_count > 0 else "MISSING"
        print(f"  {status} {ind_id}: {ref_count} template(s)")

    print()
    print("-" * 60)
    print("COVERAGE BY FRAME")
    print("-" * 60)

    total_indicators = 0
    total_covered = 0

    for frame, counts in sorted(coverage_by_frame.items()):
        total = counts["total"]
        covered = counts["covered"]
        pct = (covered / total * 100) if total > 0 else 0
        total_indicators += total
        total_covered += covered
        print(f"  {frame}: {covered}/{total} ({pct:.0f}%)")

    overall_pct = (total_covered / total_indicators * 100) if total_indicators > 0 else 0
    print()
    print(f"  OVERALL: {total_covered}/{total_indicators} ({overall_pct:.0f}%)")

    print()
    print("-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print(f"  Total indicators: {len(indicators)}")
    print(f"  Total templates: {len(templates)}")
    print(f"  Uncovered indicators: {len(uncovered)}")
    print(f"  Mode: {'STRICT' if strict_mode else 'REPORT'}")

    if uncovered:
        print()
        print("UNCOVERED INDICATORS:")
        for ind_id in uncovered:
            print(f"  - {ind_id}")
        print()
        print("WARNING: Some indicators have no template coverage")
        if strict_mode:
            print("STRICT MODE: Failing due to incomplete coverage")
            return 1
        return 0

    print()
    print("All indicators have at least one template")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
