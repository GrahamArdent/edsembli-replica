"""Tests for coverage.py functionality."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.coverage import main


def test_coverage_report_runs(monkeypatch, capsys):
    """Coverage report should run successfully."""
    monkeypatch.chdir(PROJECT_ROOT)
    exit_code = main()
    captured = capsys.readouterr()
    # In report mode (default), should exit 0
    assert exit_code == 0
    assert "INDICATOR COVERAGE REPORT" in captured.out


def test_coverage_shows_100_percent(monkeypatch, capsys):
    """Coverage should show 100% with current data."""
    monkeypatch.chdir(PROJECT_ROOT)
    main()
    captured = capsys.readouterr()
    assert "100%" in captured.out
    assert "Uncovered indicators: 0" in captured.out
