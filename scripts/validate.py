"""Validate canonical YAML + Markdown front matter against JSON Schemas.

Scope: lightweight local validation to keep the design repo consistent.
No network calls.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = WORKSPACE_ROOT / "schemas"

YAML_LOADER = YAML(typ="safe")


def normalize_yaml_scalars(value):
    if isinstance(value, (date, datetime)):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, dict):
        return {k: normalize_yaml_scalars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_yaml_scalars(v) for v in value]
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = YAML_LOADER.load(handle)
    if data is None:
        raise ValueError(f"Empty YAML file: {path}")
    if not isinstance(data, dict):
        raise TypeError(f"Expected YAML mapping at root: {path}")
    return normalize_yaml_scalars(data)


_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class ValidationContext:
    frames: set[str]
    indicators: set[str]
    templates: set[str]
    evidence_patterns: set[str]
    refs: set[str]


def read_front_matter(markdown_path: Path) -> dict:
    text = markdown_path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"Missing YAML front matter: {markdown_path}")
    yaml_text = match.group(1)
    data = YAML_LOADER.load(yaml_text)
    if not isinstance(data, dict):
        raise TypeError(f"Front matter must be a mapping: {markdown_path}")
    return normalize_yaml_scalars(data)


def validate(instance: dict, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    messages: list[str] = []
    for error in errors:
        loc = "/".join(str(p) for p in error.path)
        prefix = f"{loc}: " if loc else ""
        messages.append(prefix + error.message)
    return messages


_MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def iter_relative_markdown_links(markdown_text: str) -> list[str]:
    """Return a list of link targets from markdown for relative link checking.

    Excludes:
    - external URLs (http/https)
    - mailto links
    - pure anchors (#...)
    - empty targets
    """

    targets: list[str] = []
    for match in _MARKDOWN_LINK_RE.finditer(markdown_text):
        raw = match.group(1).strip()

        # Strip optional titles: (path "title")
        if " " in raw and not raw.startswith("<"):
            raw = raw.split(" ", 1)[0].strip()
        raw = raw.strip("<>")

        if not raw or raw.startswith("#"):
            continue

        lowered = raw.lower()
        if lowered.startswith(("http://", "https://", "mailto:")):
            continue

        targets.append(raw)

    return targets


def check_markdown_links(md_path: Path) -> list[str]:
    """Validate that relative markdown links resolve to existing files."""

    text = md_path.read_text(encoding="utf-8")
    targets = iter_relative_markdown_links(text)
    errors: list[str] = []

    for target in targets:
        # Drop anchor fragments and URL-decode paths (spaces, etc.)
        path_part = target.split("#", 1)[0]
        path_part = unquote(path_part)

        # Ignore empty after stripping anchors
        if not path_part:
            continue

        resolved = (md_path.parent / path_part).resolve()

        # Constrain to workspace (avoid weird absolute links)
        try:
            resolved.relative_to(WORKSPACE_ROOT)
        except ValueError:
            errors.append(f"Invalid link target outside workspace: ({target})")
            continue

        if not resolved.exists():
            rel_from_root = md_path.relative_to(WORKSPACE_ROOT)
            errors.append(f"Broken link in {rel_from_root}: ({target})")

    return errors


def build_validation_context() -> ValidationContext:
    """Load canonical ID sets used for cross-file consistency checks."""

    refs_doc = load_yaml(WORKSPACE_ROOT / "references" / "bibliography.yaml")
    ref_ids = {
        r.get("id")
        for r in refs_doc.get("references", [])
        if isinstance(r, dict) and isinstance(r.get("id"), str)
    }

    frames_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "frames.yaml")
    frame_ids = {
        f.get("id")
        for f in frames_doc.get("frames", [])
        if isinstance(f, dict) and isinstance(f.get("id"), str)
    }

    indicators_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "indicators.yaml")
    indicator_ids = {
        i.get("id")
        for i in indicators_doc.get("indicators", [])
        if isinstance(i, dict) and isinstance(i.get("id"), str)
    }

    templates_doc = load_yaml(WORKSPACE_ROOT / "templates" / "comment_templates.yaml")
    template_ids = {
        t.get("id")
        for t in templates_doc.get("templates", [])
        if isinstance(t, dict) and isinstance(t.get("id"), str)
    }

    evidence_ids: set[str] = set()
    evidence_dir = WORKSPACE_ROOT / "evidence"
    for md_path in sorted(evidence_dir.glob("evidence.pattern.*.md")):
        try:
            fm = read_front_matter(md_path)
        except Exception:
            continue
        ev_id = fm.get("id")
        if isinstance(ev_id, str):
            evidence_ids.add(ev_id)

    return ValidationContext(
        frames=set(filter(None, frame_ids)),
        indicators=set(filter(None, indicator_ids)),
        templates=set(filter(None, template_ids)),
        evidence_patterns=evidence_ids,
        refs=set(filter(None, ref_ids)),
    )


def check_duplicate_ids(markdown_front_matters: list[tuple[Path, dict]]) -> list[str]:
    """Ensure front matter IDs are unique across all canonical markdown."""

    seen: dict[str, Path] = {}
    errors: list[str] = []
    for path, fm in markdown_front_matters:
        doc_id = fm.get("id")
        if not isinstance(doc_id, str) or not doc_id.strip():
            continue
        if doc_id in seen:
            errors.append(
                "Duplicate front matter id: "
                f"{doc_id} in {path.relative_to(WORKSPACE_ROOT)} "
                f"and {seen[doc_id].relative_to(WORKSPACE_ROOT)}"
            )
        else:
            seen[doc_id] = path
    return errors


def check_traceability_matrix(ctx: ValidationContext) -> list[str]:
    """Validate the traceability matrix CSV if present.

    This intentionally validates only the CSV to avoid requiring parquet engines
    in contributor environments.
    """

    csv_path = WORKSPACE_ROOT / "datasets" / "traceability" / "matrix.csv"
    if not csv_path.exists():
        return []

    required_cols = {"frame_id", "indicator_id", "template_id", "section", "ref_ids"}
    allowed_sections = {"key_learning", "growth", "next_steps"}

    errors: list[str] = []

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return [f"Traceability matrix CSV has no header: {csv_path.relative_to(WORKSPACE_ROOT)}"]

        missing = sorted(required_cols - set(reader.fieldnames))
        if missing:
            return [
                "Traceability matrix CSV missing required columns "
                f"{missing}: {csv_path.relative_to(WORKSPACE_ROOT)}"
            ]

        for row_num, row in enumerate(reader, start=2):
            frame_id = (row.get("frame_id") or "").strip()
            indicator_id = (row.get("indicator_id") or "").strip()
            template_id = (row.get("template_id") or "").strip()
            section = (row.get("section") or "").strip()
            evidence_id = (row.get("evidence_pattern_id") or "").strip()

            if not frame_id or not indicator_id or not template_id or not section:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} missing required value(s)"
                )
                continue

            if frame_id not in ctx.frames:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown frame_id: {frame_id}"
                )
            if indicator_id not in ctx.indicators:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown indicator_id: {indicator_id}"
                )
            if template_id not in ctx.templates:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown template_id: {template_id}"
                )
            if section not in allowed_sections:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} invalid section: {section}"
                )
            if evidence_id and evidence_id not in ctx.evidence_patterns:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown evidence_pattern_id: {evidence_id}"
                )

            ref_ids_raw = row.get("ref_ids") or "[]"
            try:
                parsed = json.loads(ref_ids_raw)
            except json.JSONDecodeError:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} ref_ids is not valid JSON"
                )
                continue

            if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} ref_ids must be a JSON array of strings"
                )
                continue

            unknown_refs = [r for r in parsed if r and r not in ctx.refs]
            if unknown_refs:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown ref_ids: {unknown_refs}"
                )

    return errors


def main() -> int:
    failures: list[str] = []

    # YAML files
    yaml_targets = [
        (WORKSPACE_ROOT / "references" / "bibliography.yaml", SCHEMAS_DIR / "bibliography.schema.json"),
        (WORKSPACE_ROOT / "taxonomy" / "frames.yaml", SCHEMAS_DIR / "frames.schema.json"),
        (WORKSPACE_ROOT / "taxonomy" / "indicators.yaml", SCHEMAS_DIR / "indicators.schema.json"),
        (WORKSPACE_ROOT / "taxonomy" / "col-sections.yaml", SCHEMAS_DIR / "col_sections.schema.json"),
        (WORKSPACE_ROOT / "taxonomy" / "tags.yaml", SCHEMAS_DIR / "tags.schema.json"),
        (WORKSPACE_ROOT / "taxonomy" / "roles.yaml", SCHEMAS_DIR / "roles.schema.json"),
        (WORKSPACE_ROOT / "templates" / "comment_templates.yaml", SCHEMAS_DIR / "comment_templates.schema.json"),
    ]

    for yaml_path, schema_path in yaml_targets:
        instance = load_yaml(yaml_path)
        messages = validate(instance, schema_path)
        if messages:
            failures.append(f"{yaml_path.relative_to(WORKSPACE_ROOT)} failed schema {schema_path.name}:")
            failures.extend([f"  - {m}" for m in messages])

    # Markdown front matter
    doc_schema = SCHEMAS_DIR / "document.frontmatter.schema.json"
    entity_schema = SCHEMAS_DIR / "entity.frontmatter.schema.json"

    markdown_docs = [
        WORKSPACE_ROOT / "index.md",
        WORKSPACE_ROOT / "README.md",
        WORKSPACE_ROOT / "docs" / "framework.md",
        WORKSPACE_ROOT / "docs" / "infrastructure.md",
        WORKSPACE_ROOT / "docs" / "glossary.md",
        WORKSPACE_ROOT / "docs" / "requirements.md",
        WORKSPACE_ROOT / "docs" / "ROADMAP.md",
        WORKSPACE_ROOT / "docs" / "CHANGELOG.md",
        WORKSPACE_ROOT / "docs" / "CONTRIBUTING.md",
        WORKSPACE_ROOT / "docs" / "RELEASE.md",
        WORKSPACE_ROOT / "docs" / "SECURITY.md",
        WORKSPACE_ROOT / "docs" / "TESTING.md",
        WORKSPACE_ROOT / "docs" / "PRIVACY.md",
        WORKSPACE_ROOT / "docs" / "discussion.md",
        WORKSPACE_ROOT / "templates" / "README.md",
        WORKSPACE_ROOT / "schemas" / "README.md",
        WORKSPACE_ROOT / "scripts" / "README.md",
        WORKSPACE_ROOT / "guidance" / "comment-style.md",
        WORKSPACE_ROOT / "guidance" / "board-customization.md",
        WORKSPACE_ROOT / "guidance" / "override-policy.md",
        WORKSPACE_ROOT / "evidence" / "README.md",
        WORKSPACE_ROOT / "references" / "links.md",
        WORKSPACE_ROOT / "datasets" / "traceability" / "README.md",
    ]

    # Add all evidence patterns dynamically
    evidence_dir = WORKSPACE_ROOT / "evidence"
    for md_path in sorted(evidence_dir.glob("evidence.pattern.*.md")):
        markdown_docs.append(md_path)

    # Add all processes dynamically
    processes_dir = WORKSPACE_ROOT / "knowledge" / "processes"
    for md_path in sorted(processes_dir.glob("*.md")):
        markdown_docs.append(md_path)

    # Add audits dynamically
    audits_dir = WORKSPACE_ROOT / "audits"
    if audits_dir.exists():
        for md_path in sorted(audits_dir.glob("*.md")):
            markdown_docs.append(md_path)

    markdown_front_matters: list[tuple[Path, dict]] = []

    for md_path in markdown_docs:
        fm = read_front_matter(md_path)
        markdown_front_matters.append((md_path, fm))
        messages = validate(fm, doc_schema)
        if messages:
            failures.append(f"{md_path.relative_to(WORKSPACE_ROOT)} failed document front matter schema:")
            failures.extend([f"  - {m}" for m in messages])

    entities_dir = WORKSPACE_ROOT / "knowledge" / "entities"
    if entities_dir.exists():
        for md_path in sorted(entities_dir.glob("*.md")):
            fm = read_front_matter(md_path)
            messages = validate(fm, entity_schema)
            if messages:
                failures.append(f"{md_path.relative_to(WORKSPACE_ROOT)} failed entity front matter schema:")
                failures.extend([f"  - {m}" for m in messages])

    # Cross-file checks (only run if schema-level validation succeeded)
    if not failures:
        ctx = build_validation_context()

        dup_errors = check_duplicate_ids(markdown_front_matters)
        if dup_errors:
            failures.append("Duplicate IDs detected:")
            failures.extend([f"  - {m}" for m in dup_errors])

        # Validate relative links across canonical markdown docs
        link_errors: list[str] = []
        for md_path, _fm in markdown_front_matters:
            link_errors.extend(check_markdown_links(md_path))
        if link_errors:
            failures.append("Broken internal markdown links:")
            failures.extend([f"  - {m}" for m in link_errors])

        # Validate traceability matrix CSV if present
        matrix_errors = check_traceability_matrix(ctx)
        if matrix_errors:
            failures.append("Traceability matrix integrity checks failed:")
            failures.extend([f"  - {m}" for m in matrix_errors])

    if failures:
        print("VALIDATION FAILED\n")
        print("\n".join(failures))
        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
