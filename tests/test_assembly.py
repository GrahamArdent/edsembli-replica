"""Tests for lib/assembly.py slot filling functions."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.assembly import fill_slots


def test_fill_slots_success():
    """Test successful slot filling."""
    template = {
        "text": "{child} shows {strength} by {evidence}.",
        "slots": ["child", "strength", "evidence"],
        "section": "key_learning",
    }
    child_data = {
        "child": "Alex",
        "pronoun_subject": "they",
        "strength": "persistence",
        "evidence": "continuing to try different block configurations",
    }

    result = fill_slots(template, child_data)

    assert result.success
    assert result.filled_text == "Alex shows persistence by continuing to try different block configurations."
    assert len(result.errors) == 0


def test_fill_slots_missing_required():
    """Test failure when required slot is missing."""
    template = {
        "text": "{child} demonstrates {skill}.",
        "slots": ["child", "skill"],
        "section": "key_learning",
    }
    child_data = {"skill": "counting"}  # Missing 'child'

    result = fill_slots(template, child_data)

    assert not result.success
    assert "Required slot 'child' missing" in result.errors[0]


def test_fill_slots_pii_detection():
    """Test PII safety check."""
    template = {
        "text": "{child} works with {other_child}.",
        "slots": ["child", "other_child"],
        "section": "key_learning",
    }
    child_data = {
        "child": "Alex",
        "pronoun_subject": "they",
        "other_child": "Emma",  # Not allowed - other child's name
        "email": "test@example.com",  # PII field
    }

    result = fill_slots(template, child_data)

    assert not result.success
    assert any("PII" in err for err in result.errors)


def test_fill_slots_length_warning():
    """Test length warning for text outside bounds."""
    template = {
        "text": "{child} can do it.",  # Very short
        "slots": ["child"],
        "section": "key_learning",
    }
    child_data = {"child": "Alex", "pronoun_subject": "they"}

    result = fill_slots(template, child_data)

    # Should succeed but have warning about length
    assert result.success
    assert len(result.warnings) > 0
    assert "too short" in result.warnings[0].lower()


def test_fill_slots_placeholder_alias_name_maps_to_child():
    template = {
        "text": "{Name} shows persistence.",
        "slots": ["child"],
        "section": "key_learning",
    }
    child_data = {"child": "Alex", "pronoun_subject": "they"}

    result = fill_slots(template, child_data)

    assert result.success
    assert result.filled_text == "Alex shows persistence."


def test_fill_slots_placeholder_alias_pronoun_maps_to_pronoun_subject():
    template = {
        "text": "{Name} is working hard. {He/She} is proud.",
        "slots": ["child", "pronoun_subject"],
        "section": "key_learning",
    }
    child_data = {"child": "Alex", "pronoun_subject": "they"}

    result = fill_slots(template, child_data)

    assert result.success
    assert result.filled_text == "Alex is working hard. they is proud."
