"""Check that canonical files are linked in index.md.

Run: python scripts/check_index.py
Exit 0 = all good, Exit 1 = missing links found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _configure_output_encoding() -> None:
    """Ensure stdout/stderr can safely emit unicode on Windows."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]

# Folders containing canonical files that SHOULD be in index.md
CANONICAL_FOLDERS = [
    "docs",
    "taxonomy",
    "schemas",
    "evidence",
    "templates",
    "guidance",
    "decisions",
    "knowledge/processes",
]

# Files to ignore (generated, internal, or already covered by folder READMEs)
IGNORE_PATTERNS = [
    r"__pycache__",
    r"\.pyc$",
    r"docs_site/",
    r"\.schema\.json$",  # Schemas covered by schemas/README.md
    r"evidence\\evidence\.pattern\.",  # Covered by evidence/README.md
    r"taxonomy\\README\.md$",  # Internal README
    r"templates\\library\.md$",  # Covered by templates/README.md
    r"knowledge\\processes\\index\.md$",  # Internal index
]


def get_index_links(index_path: Path) -> set[str]:
    """Extract all markdown links from index.md."""
    content = index_path.read_text(encoding="utf-8")
    # Match [text](path) style links
    links = re.findall(r"\]\(([^)]+)\)", content)
    # Normalize paths
    return {link.replace("%20", " ").replace("/", "\\").lower() for link in links}


def get_canonical_files() -> list[Path]:
    """Find all markdown/yaml files in canonical folders."""
    files = []
    for folder in CANONICAL_FOLDERS:
        folder_path = WORKSPACE_ROOT / folder
        if folder_path.exists():
            files.extend(folder_path.rglob("*.md"))
            files.extend(folder_path.rglob("*.yaml"))
    return files


def should_ignore(file_path: Path) -> bool:
    """Check if file should be ignored."""
    path_str = str(file_path)
    return any(re.search(pattern, path_str) for pattern in IGNORE_PATTERNS)


def main() -> int:
    _configure_output_encoding()
    index_path = WORKSPACE_ROOT / "index.md"
    if not index_path.exists():
        print("ERROR: index.md not found!")
        return 1

    linked = get_index_links(index_path)
    canonical = get_canonical_files()

    missing = []
    for file_path in canonical:
        if should_ignore(file_path):
            continue
        rel_path = file_path.relative_to(WORKSPACE_ROOT)
        rel_str = str(rel_path).lower()
        # Check if file or its parent README is linked
        if rel_str not in linked and not any(rel_str in link for link in linked):
            missing.append(rel_path)

    if missing:
        print("WARNING: These canonical files may not be linked in index.md:")
        for f in sorted(missing):
            print(f"  - {f}")
        print("\nAdd them to index.md or update IGNORE_PATTERNS in this script.")
        return 1

    print("✓ All canonical files appear to be linked in index.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
