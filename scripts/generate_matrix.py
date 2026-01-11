"""Generate datasets/traceability/matrix.{csv,parquet}.

Usage: python scripts/generate_matrix.py

Builds a traceability matrix linking:
Frames → Indicators → Evidence Patterns → Comment Templates → References.

Notes:
- No network calls.
- Evidence pattern selection is heuristic:
  1) Prefer evidence patterns with matching frame AND matching indicator.
  2) Otherwise, any evidence pattern with matching indicator.
  3) Otherwise, leave blank.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pandas as pd
from ruamel.yaml import YAML


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = YAML(typ="safe")

_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = YAML_LOADER.load(handle)
    if data is None:
        raise ValueError(f"Empty YAML file: {path}")
    if not isinstance(data, dict):
        raise TypeError(f"Expected YAML mapping at root: {path}")
    return data


def read_front_matter(markdown_path: Path) -> dict:
    text = markdown_path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"Missing YAML front matter: {markdown_path}")
    data = YAML_LOADER.load(match.group(1))
    if not isinstance(data, dict):
        raise TypeError(f"Front matter must be a mapping: {markdown_path}")
    return data


def ensure_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def main() -> int:
    today = date.today().isoformat()

    indicators_path = WORKSPACE_ROOT / "taxonomy" / "indicators.yaml"
    frames_path = WORKSPACE_ROOT / "taxonomy" / "frames.yaml"
    templates_path = WORKSPACE_ROOT / "templates" / "comment_templates.yaml"
    bibliography_path = WORKSPACE_ROOT / "references" / "bibliography.yaml"

    indicators = load_yaml(indicators_path).get("indicators", [])
    frames = load_yaml(frames_path).get("frames", [])
    templates = load_yaml(templates_path).get("templates", [])
    bibliography = load_yaml(bibliography_path).get("references", [])

    indicator_by_id = {i["id"]: i for i in indicators if isinstance(i, dict) and "id" in i}
    frame_by_id = {f["id"]: f for f in frames if isinstance(f, dict) and "id" in f}
    ref_ids = {r["id"] for r in bibliography if isinstance(r, dict) and "id" in r}

    evidence_dir = WORKSPACE_ROOT / "evidence"
    evidence_patterns: list[dict] = []
    for path in sorted(evidence_dir.glob("evidence.pattern.*.md")):
        fm = read_front_matter(path)
        evidence_patterns.append(
            {
                "id": fm.get("id"),
                "title": fm.get("title"),
                "frame": fm.get("frame"),
                "indicators": ensure_list(fm.get("indicators")),
                "refs": ensure_list(fm.get("refs")),
            }
        )

    def select_evidence_pattern(template_frame: str, indicator_id: str) -> dict | None:
        best = [p for p in evidence_patterns if p.get("frame") == template_frame and indicator_id in p.get("indicators", [])]
        if best:
            return best[0]
        any_match = [p for p in evidence_patterns if indicator_id in p.get("indicators", [])]
        if any_match:
            return any_match[0]
        return None

    rows: list[dict] = []
    for t in templates:
        if not isinstance(t, dict):
            continue
        template_id = t.get("id")
        frame_id = t.get("frame")
        section = t.get("section")
        template_refs = ensure_list(t.get("refs"))
        template_indicators = ensure_list(t.get("indicators"))

        for indicator_id in template_indicators:
            evidence = select_evidence_pattern(frame_id, indicator_id)

            merged_refs = []
            merged_refs.extend(template_refs)
            if evidence:
                merged_refs.extend(ensure_list(evidence.get("refs")))

            # Deduplicate while preserving order
            seen = set()
            merged_refs = [r for r in merged_refs if not (r in seen or seen.add(r))]

            rows.append(
                {
                    "frame_id": frame_id,
                    "frame_name": frame_by_id.get(frame_id, {}).get("name"),
                    "indicator_id": indicator_id,
                    "indicator_name": indicator_by_id.get(indicator_id, {}).get("name"),
                    "evidence_pattern_id": evidence.get("id") if evidence else "",
                    "evidence_pattern_title": evidence.get("title") if evidence else "",
                    "template_id": template_id,
                    "section": section,
                    "ref_ids": merged_refs,
                    "generated": today,
                }
            )

    df = pd.DataFrame(rows)

    # Basic sanity checks (fail fast with clear errors)
    missing_indicators = sorted({r["indicator_id"] for r in rows if r["indicator_id"] not in indicator_by_id})
    if missing_indicators:
        raise SystemExit(f"Unknown indicator IDs in templates: {missing_indicators}")

    missing_frames = sorted({r["frame_id"] for r in rows if r["frame_id"] not in frame_by_id})
    if missing_frames:
        raise SystemExit(f"Unknown frame IDs in templates: {missing_frames}")

    used_refs = sorted({ref for r in rows for ref in r["ref_ids"] if ref})
    unknown_refs = [ref for ref in used_refs if ref not in ref_ids]
    if unknown_refs:
        raise SystemExit(f"Unknown ref IDs in matrix: {unknown_refs}")

    out_dir = WORKSPACE_ROOT / "datasets" / "traceability"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "matrix.csv"
    parquet_path = out_dir / "matrix.parquet"

    # CSV: store ref_ids as JSON for lossless round-trip
    df_csv = df.copy()
    df_csv["ref_ids"] = df_csv["ref_ids"].apply(json.dumps)
    df_csv.to_csv(csv_path, index=False, encoding="utf-8")

    # Parquet: keep ref_ids as a list column when possible
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception as exc:  # pragma: no cover
        print(f"WARN: Parquet write failed ({exc}); CSV still generated.")

    print(f"Generated {csv_path.relative_to(WORKSPACE_ROOT)}")
    if parquet_path.exists():
        print(f"Generated {parquet_path.relative_to(WORKSPACE_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
