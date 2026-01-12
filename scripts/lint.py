"""Lightweight lint checks for internal consistency.

Checks:
- All referenced `ref.*` IDs exist in references/bibliography.yaml
- All referenced indicator IDs exist in taxonomy/indicators.yaml
- Templates use only `{slot}` placeholders (no bracket placeholders)
- Declared slots match placeholders used in text
- Readability scores within acceptable range (textstat)
- Deprecation consistency (deprecated_by ↔ replaces)
- Bilingual text presence for stable templates

Scope: local QA only.
"""

from __future__ import annotations

import re
from pathlib import Path

from ruamel.yaml import YAML

# Optional: readability analysis
try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = YAML(typ="safe")

# Readability thresholds
FLESCH_READING_EASE_MIN = 60
FLESCH_READING_EASE_MAX = 80
FLESCH_KINCAID_GRADE_MIN = 6
FLESCH_KINCAID_GRADE_MAX = 8


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = YAML_LOADER.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"Expected mapping at root: {path}")
    return data


def check_readability(text: str, tid: str) -> list[str]:
    """Check readability scores for a template text."""
    failures: list[str] = []
    if not HAS_TEXTSTAT or not text.strip():
        return failures

    # Strip slot placeholders for accurate scoring
    clean_text = re.sub(r"\{[a-z_]+\}", "child", text)

    fre = textstat.flesch_reading_ease(clean_text)
    fkg = textstat.flesch_kincaid_grade(clean_text)

    if fre < FLESCH_READING_EASE_MIN:
        failures.append(f"{tid}: Flesch Reading Ease {fre:.1f} < {FLESCH_READING_EASE_MIN} (too complex)")
    elif fre > FLESCH_READING_EASE_MAX:
        failures.append(f"{tid}: Flesch Reading Ease {fre:.1f} > {FLESCH_READING_EASE_MAX} (too simple)")

    if fkg < FLESCH_KINCAID_GRADE_MIN:
        failures.append(f"{tid}: Flesch-Kincaid Grade {fkg:.1f} < {FLESCH_KINCAID_GRADE_MIN}")
    elif fkg > FLESCH_KINCAID_GRADE_MAX:
        failures.append(f"{tid}: Flesch-Kincaid Grade {fkg:.1f} > {FLESCH_KINCAID_GRADE_MAX} (too complex)")

    return failures


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

        # Readability checks (warnings, not blockers)
        readability_issues = check_readability(text, tid)
        failures.extend(readability_issues)

        # Deprecation consistency checks
        status = tmpl.get("status", "draft")
        deprecated_by = tmpl.get("deprecated_by")
        replaces = tmpl.get("replaces")

        if status == "deprecated" and not deprecated_by:
            failures.append(f"{tid}: status is 'deprecated' but 'deprecated_by' is not set")

        if deprecated_by:
            # Check that the replacement template exists
            replacement_ids = {t.get("id") for t in templates if isinstance(t, dict)}
            if deprecated_by not in replacement_ids:
                failures.append(f"{tid}: deprecated_by references unknown template '{deprecated_by}'")

        # Bilingual check: stable templates should have text_fr
        if status == "stable":
            text_fr = tmpl.get("text_fr")
            if not text_fr:
                failures.append(f"{tid}: stable template missing 'text_fr' (French translation)")

    if failures:
        print("LINT FAILED\n")
        print("\n".join(f"- {f}" for f in failures))
        return 1

    print("Lint OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
