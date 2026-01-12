"""Add text_fr placeholders to all templates.

This script adds 'text_fr: "TODO"' to all templates that don't have it.
Part of Phase 3B Sprint 3B.1 (TASK-3B1-3).
"""

from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def add_french_placeholders() -> None:
    """Add text_fr: TODO to all templates."""
    templates_path = WORKSPACE_ROOT / "templates" / "comment_templates.yaml"

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = 4096  # Prevent line wrapping

    data = yaml.load(templates_path)
    templates = data.get("templates", [])

    modified = 0
    for tmpl in templates:
        if "text_fr" not in tmpl:
            tmpl["text_fr"] = "TODO"
            modified += 1

    if modified > 0:
        yaml.dump(data, templates_path)
        print(f"✓ Added text_fr: TODO to {modified} templates")
    else:
        print("✓ All templates already have text_fr field")


if __name__ == "__main__":
    add_french_placeholders()
