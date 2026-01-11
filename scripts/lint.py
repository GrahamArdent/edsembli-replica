"""Lightweight lint checks for internal consistency.

Checks:
- All referenced `ref.*` IDs exist in references/bibliography.yaml
- All referenced indicator IDs exist in taxonomy/indicators.yaml
- Templates use only `{slot}` placeholders (no bracket placeholders)
- Declared slots match placeholders used in text

Scope: local QA only.
"""

from __future__ import annotations

import re
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
    failures: list[str] = []

    bib = load_yaml(WORKSPACE_ROOT / "references" / "bibliography.yaml")
    ref_ids = {r["id"] for r in bib.get("references", []) if isinstance(r, dict) and "id" in r}

    indicators_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "indicators.yaml")
    indicator_ids = {i["id"] for i in indicators_doc.get("indicators", []) if isinstance(i, dict) and "id" in i}

    templates_doc = load_yaml(WORKSPACE_ROOT / "templates" / "comment_templates.yaml")
    templates = templates_doc.get("templates", [])

    bracket_placeholder_re = re.compile(r"\[[^\]]+\]")
    slot_placeholder_re = re.compile(r"\{([a-z_]+)\}")

    for tmpl in templates:
        if not isinstance(tmpl, dict):
            continue
        tid = tmpl.get("id", "<missing id>")

        # Check ref IDs exist
        for ref in tmpl.get("refs", []) or []:
            if ref not in ref_ids:
                failures.append(f"{tid}: unknown ref id {ref}")

        # Check indicator IDs exist
        for indicator in tmpl.get("indicators", []) or []:
            if indicator not in indicator_ids:
                failures.append(f"{tid}: unknown indicator id {indicator}")

        text = tmpl.get("text", "") or ""

        # Check for bracket-style placeholders
        if bracket_placeholder_re.search(text):
            failures.append(f"{tid}: bracket-style placeholder found in text")

        # Check slot consistency: declared vs used
        declared_slots = set(tmpl.get("slots", []) or [])
        used_slots = set(slot_placeholder_re.findall(text))

        # Slots declared but not used
        unused_slots = declared_slots - used_slots
        for slot in unused_slots:
            failures.append(f"{tid}: slot '{slot}' declared but not used in text")

        # Slots used but not declared
        undeclared_slots = used_slots - declared_slots
        for slot in undeclared_slots:
            failures.append(f"{tid}: slot '{{{slot}}}' used in text but not declared in slots")

    if failures:
        print("LINT FAILED\n")
        print("\n".join(f"- {f}" for f in failures))
        return 1

    print("Lint OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
