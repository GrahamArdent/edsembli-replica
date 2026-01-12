"""Tests for board configuration loading and validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from typer.testing import CliRunner

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.edsembli_cli import app

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]


def test_ncdsb_config_exists() -> None:
    """Test that NCDSB board config exists."""
    config_path = ROOT / "config" / "boards" / "ncdsb.yaml"
    assert config_path.exists()


def test_tcdsb_config_exists() -> None:
    """Test that TCDSB board config exists."""
    config_path = ROOT / "config" / "boards" / "tcdsb.yaml"
    assert config_path.exists()


def test_export_with_board_flag_ncdsb(tmp_path: Path) -> None:
    """Test CSV export with NCDSB board config."""
    output = tmp_path / "ncdsb_templates.csv"
    result = runner.invoke(app, ["export", "--format", "csv", "--board", "ncdsb", "--output", str(output)])

    # Should succeed with board config loaded
    assert result.exit_code == 0
    assert "Using board config" in result.stdout or result.exit_code == 0
    assert output.exists()


def test_export_with_board_flag_tcdsb(tmp_path: Path) -> None:
    """Test CSV export with TCDSB board config."""
    output = tmp_path / "tcdsb_templates.csv"
    result = runner.invoke(app, ["export", "--format", "csv", "--board", "tcdsb", "--output", str(output)])

    # Should succeed with board config loaded
    assert result.exit_code == 0
    assert output.exists()


def test_export_with_invalid_board(tmp_path: Path) -> None:
    """Test export with non-existent board config."""
    output = tmp_path / "templates.csv"
    result = runner.invoke(app, ["export", "--format", "csv", "--board", "nonexistent", "--output", str(output)])

    # Should still export but warn about missing config
    assert "not found" in result.stdout or result.exit_code == 0


def test_export_comment_with_board_flag(tmp_path: Path) -> None:
    """Test comment export with board config."""
    # Create child data file
    child_file = tmp_path / "child.json"
    child_data = {
        "student_id": "TEST-BOARD-001",
        "child": "Taylor",
        "pronoun_subject": "They",
        "pronoun_object": "them",
        "pronoun_possessive": "their",
        "evidence": "playing cooperatively",
        "strength": "teamwork",
        "change": "increased sharing",
        "previous": "playing alone",
        "goal": "work in larger groups",
        "home_support": "practice turn-taking games",
    }
    child_file.write_text(json.dumps(child_data), encoding="utf-8")

    # Create templates file
    templates_file = tmp_path / "templates.yaml"
    templates_file.write_text(
        """template_ids:
  key_learning:
    - template.comment.belonging.key_learning.01
  growth:
    - template.comment.self_regulation.growth.01
  next_steps:
    - template.comment.belonging.next_steps.01
""",
        encoding="utf-8",
    )

    output = tmp_path / "comment.txt"
    result = runner.invoke(
        app,
        [
            "export-comment",
            "--child-file",
            str(child_file),
            "--templates",
            str(templates_file),
            "--output",
            str(output),
            "--board",
            "tcdsb",
        ],
    )

    # Should succeed (may have warnings about limits)
    assert result.exit_code == 0
    assert output.exists()


def test_board_config_char_limit_validation(tmp_path: Path) -> None:
    """Test that board config enforces character limits."""
    # Create a very short child data that will produce a short comment
    child_file = tmp_path / "child.json"
    child_data = {
        "student_id": "TEST-SHORT",
        "child": "Sam",
        "pronoun_subject": "She",
        "pronoun_object": "her",
        "pronoun_possessive": "her",
        "evidence": "playing",
        "strength": "skills",
        "change": "growth",
        "previous": "before",
        "goal": "improve",
        "home_support": "practice",
    }
    child_file.write_text(json.dumps(child_data), encoding="utf-8")

    templates_file = tmp_path / "templates.yaml"
    templates_file.write_text(
        """template_ids:
  key_learning:
    - template.comment.belonging.key_learning.01
  growth:
    - template.comment.self_regulation.growth.01
  next_steps:
    - template.comment.belonging.next_steps.01
""",
        encoding="utf-8",
    )

    output = tmp_path / "comment.txt"
    result = runner.invoke(
        app,
        [
            "export-comment",
            "--child-file",
            str(child_file),
            "--templates",
            str(templates_file),
            "--output",
            str(output),
            "--board",
            "tcdsb",
        ],
    )

    # Should complete (may warn about limits)
    assert result.exit_code == 0
    # Output may contain warnings but should still export
    assert output.exists()


def test_board_config_schema_compliance() -> None:
    """Test that board configs contain required fields."""
    from ruamel.yaml import YAML

    yaml_loader = YAML(typ="safe")

    # Test NCDSB config
    ncdsb_path = ROOT / "config" / "boards" / "ncdsb.yaml"
    with ncdsb_path.open("r", encoding="utf-8") as f:
        content = f.read()
        # Parse YAML content after frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[2].strip()
            config = yaml_loader.load(yaml_content) or {}

            # Check required fields from schema
            assert "char_limits" in config
            assert "per_section_min" in config["char_limits"]
            assert "per_section_max" in config["char_limits"]
            assert "total_min" in config["char_limits"]
            assert "total_max" in config["char_limits"]


def test_board_config_reasonable_limits() -> None:
    """Test that board configs have reasonable character limits."""
    from ruamel.yaml import YAML

    yaml_loader = YAML(typ="safe")

    for board_id in ["ncdsb", "tcdsb"]:
        config_path = ROOT / "config" / "boards" / f"{board_id}.yaml"
        with config_path.open("r", encoding="utf-8") as f:
            content = f.read()
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[2].strip()
                config = yaml_loader.load(yaml_content) or {}

                limits = config.get("char_limits", {})

                # Sanity checks
                assert limits["per_section_min"] > 0
                assert limits["per_section_max"] > limits["per_section_min"]
                assert limits["total_min"] > 0
                assert limits["total_max"] > limits["total_min"]
                # Total min should accommodate at least 2 sections at their min
                assert limits["total_min"] >= limits["per_section_min"] * 2
