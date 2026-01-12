"""Validate canonical YAML + Markdown front matter against JSON Schemas.

Scope: lightweight local validation to keep the design repo consistent.
No network calls.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = WORKSPACE_ROOT / "schemas"

YAML_LOADER = YAML(typ="safe")


def normalize_yaml_scalars(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    if isinstance(value, dict):
        return {k: normalize_yaml_scalars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_yaml_scalars(v) for v in value]
    return value


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = YAML_LOADER.load(handle)
    if data is None:
        raise ValueError(f"Empty YAML file: {path}")
    if not isinstance(data, dict):
        raise TypeError(f"Expected YAML mapping at root: {path}")
    normalized = normalize_yaml_scalars(data)
    if not isinstance(normalized, dict):
        raise TypeError(f"Expected YAML mapping after normalization: {path}")
    return normalized


_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass(frozen=True)
class ValidationContext:
    frames: set[str]
    indicators: set[str]
    templates: set[str]
    evidence_patterns: set[str]
    refs: set[str]
    tags: set[str] = field(default_factory=set)
    indicator_to_frame: dict[str, str] = field(default_factory=dict)
    templates_raw: list[dict] = field(default_factory=list)
    evidence_raw: list[dict] = field(default_factory=list)


def read_front_matter(markdown_path: Path) -> dict[str, Any]:
    text = markdown_path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"Missing YAML front matter: {markdown_path}")
    yaml_text = match.group(1)
    data = YAML_LOADER.load(yaml_text)
    if not isinstance(data, dict):
        raise TypeError(f"Front matter must be a mapping: {markdown_path}")
    normalized = normalize_yaml_scalars(data)
    if not isinstance(normalized, dict):
        raise TypeError(f"Front matter must be a mapping: {markdown_path}")
    return normalized


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
        r.get("id") for r in refs_doc.get("references", []) if isinstance(r, dict) and isinstance(r.get("id"), str)
    }

    frames_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "frames.yaml")
    frame_ids = {
        f.get("id") for f in frames_doc.get("frames", []) if isinstance(f, dict) and isinstance(f.get("id"), str)
    }

    indicators_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "indicators.yaml")
    indicator_ids: set[str] = set()
    indicator_to_frame: dict[str, str] = {}
    for i in indicators_doc.get("indicators", []):
        if isinstance(i, dict) and isinstance(i.get("id"), str):
            ind_id = i["id"]
            indicator_ids.add(ind_id)
            if isinstance(i.get("frame"), str):
                indicator_to_frame[ind_id] = i["frame"]

    templates_doc = load_yaml(WORKSPACE_ROOT / "templates" / "comment_templates.yaml")
    templates_raw = templates_doc.get("templates", [])
    template_ids = {t.get("id") for t in templates_raw if isinstance(t, dict) and isinstance(t.get("id"), str)}

    evidence_ids: set[str] = set()
    evidence_raw: list[dict] = []
    evidence_dir = WORKSPACE_ROOT / "evidence"
    for md_path in sorted(evidence_dir.glob("evidence.pattern.*.md")):
        try:
            fm = read_front_matter(md_path)
        except Exception:
            continue
        ev_id = fm.get("id")
        if isinstance(ev_id, str):
            evidence_ids.add(ev_id)
        evidence_raw.append(fm)

    tags_doc = load_yaml(WORKSPACE_ROOT / "taxonomy" / "tags.yaml")
    tag_ids: set[str] = set()
    for t in tags_doc.get("tags", []):
        if isinstance(t, dict):
            tid = t.get("id")
            if isinstance(tid, str):
                tag_ids.add(tid)
    # Also allow short form (without tag. prefix) for convenience
    tag_names = {tid.replace("tag.", "") for tid in tag_ids if tid.startswith("tag.")}

    return ValidationContext(
        frames=set(filter(None, frame_ids)),
        indicators=set(filter(None, indicator_ids)),
        templates=set(filter(None, template_ids)),
        evidence_patterns=evidence_ids,
        refs=set(filter(None, ref_ids)),
        tags=set(filter(None, tag_ids)) | tag_names,
        indicator_to_frame=indicator_to_frame,
        templates_raw=templates_raw,
        evidence_raw=evidence_raw,
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
                f"Traceability matrix CSV missing required columns {missing}: {csv_path.relative_to(WORKSPACE_ROOT)}"
            ]

        for row_num, row in enumerate(reader, start=2):
            frame_id = (row.get("frame_id") or "").strip()
            indicator_id = (row.get("indicator_id") or "").strip()
            template_id = (row.get("template_id") or "").strip()
            section = (row.get("section") or "").strip()
            evidence_id = (row.get("evidence_pattern_id") or "").strip()

            if not frame_id or not indicator_id or not template_id or not section:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} missing required value(s)")
                continue

            if frame_id not in ctx.frames:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown frame_id: {frame_id}")
            if indicator_id not in ctx.indicators:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown indicator_id: {indicator_id}")
            if template_id not in ctx.templates:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown template_id: {template_id}")
            if section not in allowed_sections:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} invalid section: {section}")
            if evidence_id and evidence_id not in ctx.evidence_patterns:
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown evidence_pattern_id: {evidence_id}"
                )

            ref_ids_raw = row.get("ref_ids") or "[]"
            try:
                parsed = json.loads(ref_ids_raw)
            except json.JSONDecodeError:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} ref_ids is not valid JSON")
                continue

            if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
                errors.append(
                    f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} ref_ids must be a JSON array of strings"
                )
                continue

            unknown_refs = [r for r in parsed if r and r not in ctx.refs]
            if unknown_refs:
                errors.append(f"{csv_path.relative_to(WORKSPACE_ROOT)}:{row_num} unknown ref_ids: {unknown_refs}")

    return errors


_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$")


def check_version_format(markdown_front_matters: list[tuple[Path, dict]]) -> list[str]:
    """Ensure version fields follow semantic versioning format."""
    errors: list[str] = []
    for path, fm in markdown_front_matters:
        version = fm.get("version")
        if not isinstance(version, str):
            continue
        if not _SEMVER_RE.match(version):
            errors.append(f"{path.relative_to(WORKSPACE_ROOT)}: version '{version}' is not valid semver")
    return errors


def check_future_dates(markdown_front_matters: list[tuple[Path, dict]]) -> list[str]:
    """Warn if any updated date is in the future (likely a typo)."""
    errors: list[str] = []
    today = date.today()
    for path, fm in markdown_front_matters:
        updated = fm.get("updated")
        if not isinstance(updated, str):
            continue
        try:
            updated_date = date.fromisoformat(updated)
        except ValueError:
            errors.append(f"{path.relative_to(WORKSPACE_ROOT)}: updated '{updated}' is not a valid ISO date")
            continue
        if updated_date > today:
            errors.append(f"{path.relative_to(WORKSPACE_ROOT)}: updated '{updated}' is in the future")
    return errors


def check_tag_vocabulary(markdown_front_matters: list[tuple[Path, dict]], ctx: ValidationContext) -> list[str]:
    """Ensure tags in front matter are from controlled vocabulary.

    This check is informational for general documents but enforced for
    evidence patterns and templates where consistency matters most.
    """
    errors: list[str] = []

    # Extract base tag names (strip "tag." prefix if present)
    known_tags = set()
    for tag in ctx.tags:
        known_tags.add(tag)
        if tag.startswith("tag."):
            known_tags.add(tag[4:])  # Also accept without prefix

    for path, fm in markdown_front_matters:
        tags = fm.get("tags")
        if not isinstance(tags, list):
            continue

        # Only enforce for evidence patterns (where tag consistency is critical)
        rel_path = str(path.relative_to(WORKSPACE_ROOT))
        is_evidence = "evidence.pattern." in path.name

        for tag in tags:
            if not isinstance(tag, str):
                continue
            tag_lower = tag.lower().replace("-", "_")
            # Check both original and normalized
            if tag not in known_tags and tag_lower not in known_tags:
                if is_evidence:
                    errors.append(f"{rel_path}: unknown tag '{tag}' (evidence patterns require controlled vocabulary)")
    return errors


_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


def check_template_slot_consistency(ctx: ValidationContext) -> list[str]:
    """Ensure declared slots match actual {placeholders} in template text."""
    errors: list[str] = []
    for tmpl in ctx.templates_raw:
        if not isinstance(tmpl, dict):
            continue
        tid = tmpl.get("id", "<unknown>")
        declared_slots = set(tmpl.get("slots") or [])
        text = tmpl.get("text") or ""
        used_slots = set(_PLACEHOLDER_RE.findall(text))

        missing = used_slots - declared_slots
        extra = declared_slots - used_slots

        if missing:
            errors.append(f"Template {tid}: placeholders used but not declared in slots: {sorted(missing)}")
        if extra:
            errors.append(f"Template {tid}: slots declared but not used in text: {sorted(extra)}")
    return errors


def check_indicator_frame_integrity(ctx: ValidationContext) -> list[str]:
    """Ensure indicators reference valid frames."""
    errors: list[str] = []
    for ind_id, frame_id in ctx.indicator_to_frame.items():
        if frame_id not in ctx.frames:
            errors.append(f"Indicator {ind_id} references unknown frame: {frame_id}")
    return errors


def check_template_integrity(ctx: ValidationContext) -> list[str]:
    """Ensure templates reference valid frames, indicators, and refs."""
    errors: list[str] = []
    for tmpl in ctx.templates_raw:
        if not isinstance(tmpl, dict):
            continue
        tid = tmpl.get("id", "<unknown>")

        frame = tmpl.get("frame")
        if isinstance(frame, str) and frame not in ctx.frames:
            errors.append(f"Template {tid} references unknown frame: {frame}")

        indicators = tmpl.get("indicators") or []
        for ind in indicators:
            if isinstance(ind, str) and ind not in ctx.indicators:
                errors.append(f"Template {tid} references unknown indicator: {ind}")

        refs = tmpl.get("refs") or []
        for ref in refs:
            if isinstance(ref, str) and ref not in ctx.refs:
                errors.append(f"Template {tid} references unknown ref: {ref}")

        # Ensure templates have at least one indicator and one ref
        if not indicators:
            errors.append(f"Template {tid} has no indicators (traceability gap)")
        if not refs:
            errors.append(f"Template {tid} has no refs (citation gap)")
    return errors


def check_evidence_pattern_integrity(ctx: ValidationContext) -> list[str]:
    """Ensure evidence patterns reference valid frames, indicators, and refs."""
    errors: list[str] = []
    for ev in ctx.evidence_raw:
        if not isinstance(ev, dict):
            continue
        ev_id = ev.get("id", "<unknown>")

        frame = ev.get("frame")
        if isinstance(frame, str) and frame not in ctx.frames:
            errors.append(f"Evidence pattern {ev_id} references unknown frame: {frame}")

        indicators = ev.get("indicators") or []
        for ind in indicators:
            if isinstance(ind, str) and ind not in ctx.indicators:
                errors.append(f"Evidence pattern {ev_id} references unknown indicator: {ind}")

        refs = ev.get("refs") or []
        for ref in refs:
            if isinstance(ref, str) and ref not in ctx.refs:
                errors.append(f"Evidence pattern {ev_id} references unknown ref: {ref}")
    return errors


_HEADING_RE = re.compile(r"^#+\s+(.+)$", re.MULTILINE)


def slugify_heading(heading: str) -> str:
    """Convert a Markdown heading to its anchor slug (GitHub style)."""
    slug = heading.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def check_anchor_fragments(markdown_front_matters: list[tuple[Path, dict]]) -> list[str]:
    """Validate that #anchor links point to actual headings in target files."""
    errors: list[str] = []

    # Build heading cache for all markdown files
    heading_cache: dict[Path, set[str]] = {}

    def get_headings(path: Path) -> set[str]:
        if path not in heading_cache:
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                heading_cache[path] = set()
                return heading_cache[path]
            headings = set()
            for match in _HEADING_RE.finditer(text):
                headings.add(slugify_heading(match.group(1)))
            heading_cache[path] = headings
        return heading_cache[path]

    for md_path, _fm in markdown_front_matters:
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            continue

        for match in _MARKDOWN_LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if " " in raw and not raw.startswith("<"):
                raw = raw.split(" ", 1)[0].strip()
            raw = raw.strip("<>")

            if not raw:
                continue

            lowered = raw.lower()
            if lowered.startswith(("http://", "https://", "mailto:")):
                continue

            if "#" not in raw:
                continue

            path_part, anchor = raw.split("#", 1)
            if not anchor:
                continue

            # Determine target file
            if path_part:
                target_path = (md_path.parent / unquote(path_part)).resolve()
            else:
                # Same-file anchor
                target_path = md_path

            if not target_path.exists() or not target_path.suffix == ".md":
                continue

            headings = get_headings(target_path)
            anchor_lower = anchor.lower()

            if anchor_lower not in headings:
                rel_from_root = md_path.relative_to(WORKSPACE_ROOT)
                errors.append(f"{rel_from_root}: anchor #{anchor} not found in {target_path.name}")

    return errors


_GENERATED_MARKER = "AUTO-GENERATED"


def check_generated_file_markers(ctx: ValidationContext) -> list[str]:
    """Warn if generated files appear to have been hand-edited (missing marker)."""
    errors: list[str] = []

    generated_files = [
        WORKSPACE_ROOT / "references" / "links.md",
    ]

    for path in generated_files:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        if _GENERATED_MARKER not in text:
            errors.append(
                f"{path.relative_to(WORKSPACE_ROOT)} is missing '{_GENERATED_MARKER}' marker. "
                "Was it hand-edited? Regenerate with the appropriate script."
            )
    return errors


def check_orphan_indicators(ctx: ValidationContext) -> list[str]:
    """Warn about indicators not referenced by any template (coverage gap)."""
    errors: list[str] = []

    referenced: set[str] = set()
    for tmpl in ctx.templates_raw:
        if not isinstance(tmpl, dict):
            continue
        for ind in tmpl.get("indicators") or []:
            if isinstance(ind, str):
                referenced.add(ind)

    orphans = ctx.indicators - referenced
    for orphan in sorted(orphans):
        errors.append(f"Indicator {orphan} is not referenced by any template")

    return errors


_PII_PATTERNS = [
    # OEN: 9 digits, possibly hyphenated (Ontario Education Number)
    (re.compile(r"\b\d{3}[- ]?\d{3}[- ]?\d{3}\b"), "Possible OEN detected"),
    # Phone: (123) 456-7890 or 123-456-7890
    (re.compile(r"\b\(?\d{3}\)?[- .]\d{3}[- .]\d{4}\b"), "Possible phone number detected"),
    # Email: Simple check
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "Email address detected"),
]


def check_pii_safety(ctx: ValidationContext) -> list[str]:
    """Scan all loaded content for potential PII violations."""
    errors: list[str] = []

    # Check templates
    for tmpl in ctx.templates_raw:
        tid = tmpl.get("id", "<unknown>")
        text = tmpl.get("text", "")
        if not isinstance(text, str):
            continue

        for pattern, msg in _PII_PATTERNS:
            if pattern.search(text):
                errors.append(f"Template {tid}: {msg} (Strict No-PII Policy)")

    # Check evidence patterns
    for ev in ctx.evidence_raw:
        ev_id = ev.get("id", "<unknown>")
        # Evidence patterns might have 'observation' or 'analysis' fields in future
        # For now, check string values in the dict
        for key, val in ev.items():
            if isinstance(val, str):
                for pattern, msg in _PII_PATTERNS:
                    if pattern.search(val):
                        errors.append(f"Evidence {ev_id} ({key}): {msg} (Strict No-PII Policy)")

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

        # Version format validation
        version_errors = check_version_format(markdown_front_matters)
        if version_errors:
            failures.append("Invalid version format (expected semver):")
            failures.extend([f"  - {m}" for m in version_errors])

        # Future date detection
        date_errors = check_future_dates(markdown_front_matters)
        if date_errors:
            failures.append("Date validation errors:")
            failures.extend([f"  - {m}" for m in date_errors])

        # Tag vocabulary enforcement
        tag_errors = check_tag_vocabulary(markdown_front_matters, ctx)
        if tag_errors:
            failures.append("Unknown tags (not in taxonomy/tags.yaml):")
            failures.extend([f"  - {m}" for m in tag_errors])

        # Template slot consistency
        slot_errors = check_template_slot_consistency(ctx)
        if slot_errors:
            failures.append("Template slot/placeholder mismatches:")
            failures.extend([f"  - {m}" for m in slot_errors])

        # Indicator→frame integrity
        ind_frame_errors = check_indicator_frame_integrity(ctx)
        if ind_frame_errors:
            failures.append("Indicator→frame integrity issues:")
            failures.extend([f"  - {m}" for m in ind_frame_errors])

        # Template integrity (refs, frames, indicators)
        tmpl_errors = check_template_integrity(ctx)
        if tmpl_errors:
            failures.append("Template integrity issues:")
            failures.extend([f"  - {m}" for m in tmpl_errors])

        # Evidence pattern integrity
        ev_errors = check_evidence_pattern_integrity(ctx)
        if ev_errors:
            failures.append("Evidence pattern integrity issues:")
            failures.extend([f"  - {m}" for m in ev_errors])

        # Anchor fragment validation
        anchor_errors = check_anchor_fragments(markdown_front_matters)
        if anchor_errors:
            failures.append("Broken anchor links (heading not found):")
            failures.extend([f"  - {m}" for m in anchor_errors])

        # Generated file marker check
        gen_errors = check_generated_file_markers(ctx)
        if gen_errors:
            failures.append("Generated file issues:")
            failures.extend([f"  - {m}" for m in gen_errors])

        # Orphan indicator detection
        orphan_errors = check_orphan_indicators(ctx)
        if orphan_errors:
            failures.append("Orphan indicators (not referenced by any template):")
            failures.extend([f"  - {m}" for m in orphan_errors])

        # PII Safety Scan
        pii_errors = check_pii_safety(ctx)
        if pii_errors:
            failures.append("CRITICAL: PII Patterns Detected (Strict No-PII Policy):")
            failures.extend([f"  - {m}" for m in pii_errors])

    if failures:
        print("VALIDATION FAILED\n")
        print("\n".join(failures))
        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
