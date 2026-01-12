import shutil
from pathlib import Path

ROOT = Path(__file__).parents[1]
SITE_DOCS = ROOT / "site_docs"


# MkDocs treats a top-level docs_dir folder named "templates" specially.
# To avoid docs being silently excluded, we stage repo/templates -> site_docs/template_library.
DIR_MAP: list[tuple[str, str]] = [
    ("docs", "docs"),
    ("taxonomy", "taxonomy"),
    ("evidence", "evidence"),
    ("templates", "template_library"),
    ("guidance", "guidance"),
    ("knowledge", "knowledge"),
    ("audits", "audits"),
    ("schemas", "schemas"),
    ("scripts", "scripts"),
    ("references", "references"),
    ("examples", "examples"),
    ("decisions", "decisions"),
    ("sources", "sources"),
    ("datasets/traceability", "datasets/traceability"),
]


def rewrite_staged_markdown_links() -> None:
    """Rewrite internal links to match staged paths."""

    replacements = [
        # Markdown link targets
        ("(../templates/", "(../template_library/"),
        ("(templates/", "(template_library/"),
        ("(../templates%2F", "(../template_library%2F"),
        ("(templates%2F", "(template_library%2F"),
        # Reference-style links
        ("[../templates/", "[../template_library/"),
        ("[templates/", "[template_library/"),
    ]

    md_files = sorted(SITE_DOCS.rglob("*.md"))
    for md_path in md_files:
        text = md_path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements:
            updated = updated.replace(old, new)

        if updated != text:
            md_path.write_text(updated, encoding="utf-8")


def main() -> None:
    if SITE_DOCS.exists():
        shutil.rmtree(SITE_DOCS)
    SITE_DOCS.mkdir()

    for src_rel, dst_rel in DIR_MAP:
        src = ROOT / src_rel
        dst = SITE_DOCS / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            print(f"Copied {src_rel}")

    rewrite_staged_markdown_links()

    print("Documentation staged in site_docs/. Run 'mkdocs build' now.")


if __name__ == "__main__":
    main()
