"""Tests for export functionality (template bank and comment exports)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from typer.testing import CliRunner

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.edsembli_cli import app

runner = CliRunner()


def test_export_csv_all_templates(tmp_path: Path) -> None:
    """Test CSV export of all templates."""
    output = tmp_path / "templates.csv"
    result = runner.invoke(app, ["export", "--format", "csv", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "Exported" in result.stdout

    # Check CSV structure
    content = output.read_text(encoding="utf-8-sig")
    lines = content.strip().split("\n")
    assert len(lines) > 1  # Header + data rows
    assert "id,frame,section,tone,text" in lines[0]


def test_export_json_all_templates(tmp_path: Path) -> None:
    """Test JSON export of all templates."""
    output = tmp_path / "templates.json"
    result = runner.invoke(app, ["export", "--format", "json", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "Exported" in result.stdout

    # Check JSON structure
    data = json.loads(output.read_text(encoding="utf-8"))
    assert "export_metadata" in data
    assert "templates" in data
    assert data["export_metadata"]["total_templates"] > 0
    assert len(data["templates"]) > 0

    # Check template structure
    template = data["templates"][0]
    assert "id" in template
    assert "frame" in template
    assert "section" in template
    assert "text" in template
    assert "metadata" in template


def test_export_filter_by_section(tmp_path: Path) -> None:
    """Test filtering export by section."""
    output = tmp_path / "growth_templates.json"
    result = runner.invoke(app, ["export", "--format", "json", "--section", "growth", "--output", str(output)])

    assert result.exit_code == 0

    data = json.loads(output.read_text(encoding="utf-8"))
    assert all(t["section"] == "growth" for t in data["templates"])


def test_export_filter_by_frame(tmp_path: Path) -> None:
    """Test filtering export by frame."""
    output = tmp_path / "belonging_templates.json"
    result = runner.invoke(app, ["export", "--format", "json", "--frame", "frame.belonging", "--output", str(output)])

    assert result.exit_code == 0

    data = json.loads(output.read_text(encoding="utf-8"))
    assert all(t["frame"] == "frame.belonging" for t in data["templates"])


def test_export_no_matches(tmp_path: Path) -> None:
    """Test export with filters that match nothing."""
    output = tmp_path / "none.json"
    result = runner.invoke(app, ["export", "--format", "json", "--status", "nonexistent", "--output", str(output)])

    assert result.exit_code == 1
    assert "No templates match" in result.stdout


def test_export_unsupported_format(tmp_path: Path) -> None:
    """Test export with unsupported format."""
    output = tmp_path / "templates.xml"
    result = runner.invoke(app, ["export", "--format", "xml", "--output", str(output)])

    assert result.exit_code == 1
    assert "Unsupported format" in result.stdout


def test_export_comment_txt(tmp_path: Path) -> None:
    """Test plain text comment export."""
    # Create child data file
    child_file = tmp_path / "child.json"
    child_data = {
        "student_id": "TEST-001",
        "child": "Alex",
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
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert "Exported comment" in result.stdout

    # Check content has student name
    content = output.read_text(encoding="utf-8")
    assert "Alex" in content


def test_export_comment_json(tmp_path: Path) -> None:
    """Test JSON comment export."""
    # Create child data file
    child_file = tmp_path / "child.json"
    child_data = {
        "student_id": "TEST-002",
        "child": "Sam",
        "pronoun_subject": "She",
        "pronoun_object": "her",
        "pronoun_possessive": "her",
        "evidence": "building towers",
        "strength": "spatial reasoning",
        "change": "more complex designs",
        "previous": "simple stacking",
        "goal": "create 3D structures",
        "home_support": "explore building toys",
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

    output = tmp_path / "comment.json"
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
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()

    # Check JSON structure
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["student_id"] == "TEST-002"
    assert data["student_name"] == "Sam"
    assert "full_comment" in data
    assert "metadata" in data
    assert "template_ids_used" in data
    assert len(data["template_ids_used"]) == 3


def test_export_comment_missing_child_file(tmp_path: Path) -> None:
    """Test comment export with missing child file."""
    result = runner.invoke(app, ["export-comment", "--child-file", str(tmp_path / "nonexistent.json")])

    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_export_comment_invalid_template_ids(tmp_path: Path) -> None:
    """Test comment export with invalid template IDs."""
    # Create child data file
    child_file = tmp_path / "child.json"
    child_data = {
        "student_id": "TEST-003",
        "child": "Jordan",
        "pronoun_subject": "He",
        "pronoun_object": "him",
        "pronoun_possessive": "his",
    }
    child_file.write_text(json.dumps(child_data), encoding="utf-8")

    # Create templates file with invalid IDs
    templates_file = tmp_path / "templates.yaml"
    templates_file.write_text(
        """template_ids:
  key_learning:
    - template.invalid.id.01
  growth:
    - template.another.invalid.02
  next_steps:
    - template.also.invalid.03
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
        ],
    )

    assert result.exit_code == 1
    assert "Assembly errors" in result.stdout


def test_export_translation_csv(tmp_path: Path) -> None:
    """Test translation-csv export format."""
    output = tmp_path / "translations.csv"
    result = runner.invoke(app, ["export", "--format", "translation-csv", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "Exported" in result.stdout

    # Check CSV structure
    content = output.read_text(encoding="utf-8-sig")
    lines = content.strip().split("\n")
    assert len(lines) > 1  # Header + data rows

    # Verify header has translator-friendly columns
    assert "id,frame,section,slots,text,text_fr" in lines[0]

    # Verify text_fr column is empty for translator to fill
    import csv

    with output.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) > 0
        # All text_fr should be empty
        for row in rows:
            assert row["text_fr"] == ""
            assert row["text"]  # English text should exist
            assert row["id"].startswith("template.")


def test_export_translation_csv_filtered(tmp_path: Path) -> None:
    """Test translation-csv export with filters."""
    output = tmp_path / "translations_belonging.csv"
    result = runner.invoke(
        app,
        [
            "export",
            "--format",
            "translation-csv",
            "--frame",
            "frame.belonging",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.exists()

    # All rows should be from belonging frame
    import csv

    with output.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        for row in rows:
            assert row["frame"] == "frame.belonging"


def test_import_translations_dry_run(tmp_path: Path) -> None:
    """Test import translations in dry-run mode."""
    # Create a CSV with translations
    translations_csv = tmp_path / "translations.csv"
    with translations_csv.open("w", encoding="utf-8-sig", newline="") as f:
        import csv

        writer = csv.DictWriter(f, fieldnames=["id", "text_fr"])
        writer.writeheader()
        writer.writerow(
            {
                "id": "template.comment.belonging.key_learning.01",
                "text_fr": (
                    "{child} développe un fort sentiment d'appartenance dans notre classe. "
                    "{pronoun_subject} le montre par {evidence}."
                ),
            }
        )

    result = runner.invoke(app, ["import-translations", str(translations_csv), "--dry-run"])

    assert result.exit_code == 0
    assert "validated successfully" in result.stdout
    assert "Preview of changes" in result.stdout
    assert "Run without --dry-run" in result.stdout


def test_import_translations_missing_slots(tmp_path: Path) -> None:
    """Test import translations with missing slots (validation error)."""
    translations_csv = tmp_path / "translations.csv"
    with translations_csv.open("w", encoding="utf-8-sig", newline="") as f:
        import csv

        writer = csv.DictWriter(f, fieldnames=["id", "text_fr"])
        writer.writeheader()
        # Missing {evidence} slot
        writer.writerow(
            {
                "id": "template.comment.belonging.key_learning.01",
                "text_fr": "{child} développe un fort sentiment d'appartenance.",
            }
        )

    result = runner.invoke(app, ["import-translations", str(translations_csv), "--dry-run"])

    assert result.exit_code == 1
    assert "Validation Errors" in result.stdout
    assert "missing slots" in result.stdout


def test_import_translations_extra_slots(tmp_path: Path) -> None:
    """Test import translations with extra slots (validation error)."""
    translations_csv = tmp_path / "translations.csv"
    with translations_csv.open("w", encoding="utf-8-sig", newline="") as f:
        import csv

        writer = csv.DictWriter(f, fieldnames=["id", "text_fr"])
        writer.writeheader()
        # Extra {extra_slot} not in English
        writer.writerow(
            {
                "id": "template.comment.belonging.key_learning.01",
                "text_fr": "{child} développe {extra_slot} par {evidence}. {pronoun_subject} le montre.",
            }
        )

    result = runner.invoke(app, ["import-translations", str(translations_csv), "--dry-run"])

    assert result.exit_code == 1
    assert "Validation Errors" in result.stdout
    assert "extra slots" in result.stdout


def test_import_translations_invalid_template_id(tmp_path: Path) -> None:
    """Test import translations with non-existent template ID."""
    translations_csv = tmp_path / "translations.csv"
    with translations_csv.open("w", encoding="utf-8-sig", newline="") as f:
        import csv

        writer = csv.DictWriter(f, fieldnames=["id", "text_fr"])
        writer.writeheader()
        writer.writerow({"id": "template.comment.invalid.template", "text_fr": "Translation text"})

    result = runner.invoke(app, ["import-translations", str(translations_csv), "--dry-run"])

    assert result.exit_code == 1
    assert "Validation Errors" in result.stdout
    assert "Template not found" in result.stdout


def test_import_translations_empty_csv(tmp_path: Path) -> None:
    """Test import translations with empty CSV."""
    translations_csv = tmp_path / "translations.csv"
    with translations_csv.open("w", encoding="utf-8-sig", newline="") as f:
        import csv

        writer = csv.DictWriter(f, fieldnames=["id", "text_fr"])
        writer.writeheader()

    result = runner.invoke(app, ["import-translations", str(translations_csv)])

    assert result.exit_code == 1
    assert "No translations found" in result.stdout
