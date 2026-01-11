"""Tests for lint.py functionality."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lint import load_yaml, main


def test_lint_passes_on_valid_data(monkeypatch, capsys):
    """Lint should pass with exit code 0 on the current valid data."""
    monkeypatch.chdir(PROJECT_ROOT)
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Lint OK" in captured.out


def test_load_yaml_returns_dict():
    """load_yaml should return a dictionary for valid YAML files."""
    yaml_path = PROJECT_ROOT / "taxonomy" / "frames.yaml"
    data = load_yaml(yaml_path)
    assert isinstance(data, dict)
    assert "frames" in data
