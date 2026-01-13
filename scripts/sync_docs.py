#!/usr/bin/env python3
"""Sync canonical files to docs_site/ for MkDocs build.

This eliminates manual duplication by automatically syncing canonical
files to the MkDocs source directory before builds.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
DOCS_SITE = WORKSPACE_ROOT / "docs_site"

# Folders to sync from root → docs_site
SYNC_FOLDERS = [
    "audits",
    "contracts",
    "datasets",
    "decisions",
    "docs",
    "evidence",
    "examples",
    "guidance",
    "knowledge",
    "references",
    "schemas",
    "scripts",
    "sources",
    "taxonomy",
    "templates",
]

# Individual files to sync
SYNC_FILES = [
    "index.md",
    "README.md",
]


def _configure_output_encoding() -> None:
    """Ensure stdout/stderr can safely emit unicode on Windows."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main() -> int:
    """Sync canonical files to docs_site/."""
    _configure_output_encoding()
    print(f"Syncing canonical files to {DOCS_SITE}...")

    # Clean docs_site (but preserve .gitignore if it exists)
    if DOCS_SITE.exists():
        for item in DOCS_SITE.iterdir():
            if item.name != ".gitignore":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    else:
        DOCS_SITE.mkdir()

    # Sync folders
    for folder_name in SYNC_FOLDERS:
        src = WORKSPACE_ROOT / folder_name
        dst = DOCS_SITE / folder_name
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"  ✓ {folder_name}/")
        else:
            print(f"  ⚠ {folder_name}/ not found (skipped)")

    # Sync individual files
    for file_name in SYNC_FILES:
        src = WORKSPACE_ROOT / file_name
        dst = DOCS_SITE / file_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {file_name}")
        else:
            print(f"  ⚠ {file_name} not found (skipped)")

    print(f"\nSync complete. {DOCS_SITE} is ready for MkDocs build.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
