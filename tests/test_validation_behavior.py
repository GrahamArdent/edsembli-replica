"""Tests for validate.py core functionality."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validate import (
    ValidationContext,
    build_validation_context,
    check_indicator_frame_integrity,
    check_template_slot_consistency,
    main,
)


def test_validation_passes_on_current_data(monkeypatch, capsys):
    """Full validation should pass on the current canonical data."""
    monkeypatch.chdir(PROJECT_ROOT)
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Validation OK" in captured.out


def test_build_validation_context():
    """build_validation_context should load all canonical IDs."""
    ctx = build_validation_context()
    assert len(ctx.frames) == 4  # 4 kindergarten frames
    assert len(ctx.indicators) == 13  # 13 indicators
    assert len(ctx.templates) == 36  # 36 comment templates
    assert len(ctx.refs) > 0  # Should have bibliography refs


def test_slot_consistency_catches_mismatch():
    """check_template_slot_consistency should catch mismatched slots."""
    ctx = ValidationContext(
        frames=set(),
        indicators=set(),
        templates=set(),
        evidence_patterns=set(),
        refs=set(),
        tags=set(),
        indicator_to_frame={},
        templates_raw=[
            {
                "id": "test.template",
                "slots": ["child", "evidence"],
                "text": "Hello {child}, you showed {missing_slot}.",
            }
        ],
        evidence_raw=[],
    )
    errors = check_template_slot_consistency(ctx)
    assert len(errors) == 2  # missing_slot used but not declared, evidence declared but not used


def test_indicator_frame_integrity_catches_bad_frame():
    """check_indicator_frame_integrity should catch unknown frames."""
    ctx = ValidationContext(
        frames={"frame.belonging"},
        indicators={"indicator.test"},
        templates=set(),
        evidence_patterns=set(),
        refs=set(),
        tags=set(),
        indicator_to_frame={"indicator.test": "frame.nonexistent"},
        templates_raw=[],
        evidence_raw=[],
    )
    errors = check_indicator_frame_integrity(ctx)
    assert len(errors) == 1
    assert "unknown frame" in errors[0]
