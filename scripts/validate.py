"""Validate canonical YAML + Markdown front matter against JSON Schemas.

Scope: lightweight local validation to keep the design repo consistent.
No network calls.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

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
        WORKSPACE_ROOT / "framework.md",
        WORKSPACE_ROOT / "infrastructure.md",
        WORKSPACE_ROOT / "glossary.md",
        WORKSPACE_ROOT / "requirements.md",
        WORKSPACE_ROOT / "ROADMAP.md",
        WORKSPACE_ROOT / "CHANGELOG.md",
        WORKSPACE_ROOT / "CONTRIBUTING.md",
        WORKSPACE_ROOT / "PRIVACY.md",
        WORKSPACE_ROOT / "discussion.md",
        WORKSPACE_ROOT / "templates" / "README.md",
        WORKSPACE_ROOT / "schemas" / "README.md",
        WORKSPACE_ROOT / "scripts" / "README.md",
        WORKSPACE_ROOT / "guidance" / "comment-style.md",
        WORKSPACE_ROOT / "guidance" / "board-customization.md",
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

    for md_path in markdown_docs:
        fm = read_front_matter(md_path)
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

    if failures:
        print("VALIDATION FAILED\n")
        print("\n".join(failures))
        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
