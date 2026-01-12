"""Regression tests ensuring generated artifacts remain stable.

These tests treat certain generated outputs as "golden" artifacts:
- Traceability matrix CSV in datasets/traceability/matrix.csv
- Coverage + gaps reports in reports/

The tests re-run generators and assert the resulting files match what is
checked in, preventing accidental drift.
"""

from __future__ import annotations

from datetime import date as real_date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generate_reports_match_committed(monkeypatch) -> None:
    monkeypatch.chdir(PROJECT_ROOT)

    from scripts import generate_coverage_report, generate_gaps_report

    coverage_path = PROJECT_ROOT / "reports" / "coverage.md"
    gaps_path = PROJECT_ROOT / "reports" / "gaps.md"

    coverage_before = coverage_path.read_text(encoding="utf-8")
    gaps_before = gaps_path.read_text(encoding="utf-8")

    generate_coverage_report.generate_coverage_report()
    exit_code = generate_gaps_report.generate_gaps_report()

    assert exit_code == 0
    assert coverage_path.read_text(encoding="utf-8") == coverage_before
    assert gaps_path.read_text(encoding="utf-8") == gaps_before


def test_generate_matrix_matches_committed(monkeypatch) -> None:
    monkeypatch.chdir(PROJECT_ROOT)

    from scripts import generate_matrix

    parquet_path = PROJECT_ROOT / "datasets" / "traceability" / "matrix.parquet"

    csv_path = PROJECT_ROOT / "datasets" / "traceability" / "matrix.csv"
    before = csv_path.read_text(encoding="utf-8")

    class FixedDate(real_date):
        @classmethod
        def today(cls):  # type: ignore[override]
            return real_date(2026, 1, 11)

    monkeypatch.setattr(generate_matrix, "date", FixedDate)

    try:
        exit_code = generate_matrix.main()
        assert exit_code == 0

        after = csv_path.read_text(encoding="utf-8")
        assert after == before
    finally:
        if parquet_path.exists():
            parquet_path.unlink()
