"""Pre-commit helper: remind contributors to update docs/CHANGELOG.md.

This hook is intentionally warning-only: it never blocks a commit.
"""

from __future__ import annotations

import subprocess


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=False,
        capture_output=True,
        text=True,
    )

    staged = {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}
    if "docs/CHANGELOG.md" not in staged:
        print("NOTE: Consider updating docs/CHANGELOG.md")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
