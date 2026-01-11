import shutil
from pathlib import Path

ROOT = Path(__file__).parents[1]
SITE_DOCS = ROOT / "site_docs"

DIRS_TO_COPY = [
    "docs",
    "taxonomy",
    "evidence",
    "templates",
    "guidance",
    "knowledge",
    "audits",
    "schemas",
    "scripts",
]
FILES_TO_COPY = [
    "index.md",
]


def main():
    if SITE_DOCS.exists():
        shutil.rmtree(SITE_DOCS)
    SITE_DOCS.mkdir()

    for dir_name in DIRS_TO_COPY:
        src = ROOT / dir_name
        dst = SITE_DOCS / dir_name
        if src.exists():
            shutil.copytree(src, dst)
            print(f"Copied {dir_name}")

    for file_name in FILES_TO_COPY:
        src = ROOT / file_name
        dst = SITE_DOCS / file_name
        if src.exists():
            shutil.copy(src, dst)
            print(f"Copied {file_name}")

    # Fix paths in mkdocs.yml?
    # No, because mkdocs.yml now points to site_docs, so "docs/framework.md" in mkdocs.yml
    # will look for "site_docs/docs/framework.md", which exists.
    # But "index.md" in mkdocs.yml will look for "site_docs/index.md", which exists.

    print("Documentation staged in site_docs/. Run 'mkdocs build' now.")


if __name__ == "__main__":
    main()
