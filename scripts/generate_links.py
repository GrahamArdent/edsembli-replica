"""Generate references/links.md from references/bibliography.yaml.

Usage: python scripts/generate_links.py

Produces a human-readable quick links file from the canonical bibliography.
"""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = YAML(typ="safe")


def main() -> int:
    bib_path = WORKSPACE_ROOT / "references" / "bibliography.yaml"
    output_path = WORKSPACE_ROOT / "references" / "links.md"

    with bib_path.open("r", encoding="utf-8") as f:
        bib = YAML_LOADER.load(f)

    references = bib.get("references", [])

    # Group by type
    groups: dict[str, list[dict]] = {}
    for ref in references:
        ref_type = ref.get("type", "other")
        if ref_type not in groups:
            groups[ref_type] = []
        groups[ref_type].append(ref)

    # Generate markdown
    lines = [
        "---",
        "id: doc.references.links",
        "type: document",
        "title: Quick Links",
        "version: 0.1.0",
        "status: draft",
        "tags: [references, links]",
        "refs: []",
        f"updated: 2026-01-11",
        "---",
        "",
        "# Quick Links",
        "",
        "*Auto-generated from `references/bibliography.yaml`.*",
        "",
    ]

    type_labels = {
        "government_document": "Government Documents",
        "legislation": "Legislation",
        "vendor_documentation": "Vendor Resources",
        "corporate": "Corporate",
        "curriculum_resource": "Curriculum Resources",
        "academic": "Academic",
        "other": "Other",
    }

    for ref_type, refs in sorted(groups.items()):
        label = type_labels.get(ref_type, ref_type.replace("_", " ").title())
        lines.append(f"## {label}")
        lines.append("")

        for ref in refs:
            title = ref.get("title", "Untitled")
            url = ref.get("url", "")
            year = ref.get("year", "")
            
            if url:
                lines.append(f"- **{title}** ({year})  ")
                lines.append(f"  [{url}]({url})")
            else:
                lines.append(f"- **{title}** ({year})  ")
                lines.append(f"  *(No URL available)*")
            lines.append("")

    lines.append("---")
    lines.append("*Note: Edit `references/bibliography.yaml` to update sources. Re-run `python scripts/generate_links.py` to regenerate this file.*")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_path.relative_to(WORKSPACE_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
