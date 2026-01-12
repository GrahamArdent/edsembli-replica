"""Master validation script - run all checks in one command.

Usage:
    python scripts/check_all.py          # Run all checks
    python scripts/check_all.py --quick  # Skip slow checks (pytest, mkdocs)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], name: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n{'=' * 60}")
    print(f"Running: {name}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd, cwd=WORKSPACE_ROOT)
    if result.returncode == 0:
        print(f"✓ {name} passed")
        return True
    else:
        print(f"✗ {name} FAILED")
        return False


def main() -> int:
    quick = "--quick" in sys.argv
    results: list[tuple[str, bool]] = []

    # 1. Format check (fast)
    results.append(("Ruff format", run([sys.executable, "-m", "ruff", "format", "--check", "."], "Ruff format check")))

    # 2. Lint check (fast)
    results.append(("Ruff lint", run([sys.executable, "-m", "ruff", "check", "."], "Ruff lint")))

    # 3. Schema validation (fast)
    results.append(("Schema validation", run([sys.executable, "scripts/validate.py"], "Schema validation")))

    # 4. Reference lint (fast)
    results.append(("Reference lint", run([sys.executable, "scripts/lint.py"], "Reference & readability lint")))

    # 5. Index completeness (fast)
    results.append(("Index check", run([sys.executable, "scripts/check_index.py"], "Index completeness")))

    if not quick:
        # 6. Tests (slower)
        results.append(("Pytest", run([sys.executable, "-m", "pytest", "-v", "--tb=short"], "Pytest")))

        # 7. Type check (slower)
        results.append(("Pyright", run([sys.executable, "-m", "pyright"], "Type checking (pyright)")))

        # 8. Docs build (slower)
        results.append(("MkDocs", run([sys.executable, "scripts/sync_docs.py"], "Sync docs")))

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")
    print(f"\n{passed}/{total} checks passed")

    if quick:
        print("\n(Ran with --quick, skipping pytest/pyright/mkdocs)")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
