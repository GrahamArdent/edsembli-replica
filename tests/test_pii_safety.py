"""Tests for validate.py PII detection and other safety checks."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.validate import _PII_PATTERNS, ValidationContext, check_pii_safety


def test_pii_detects_oen():
    """PII scanner should detect Ontario Education Numbers (9 digits)."""
    oen_pattern = _PII_PATTERNS[0][0]
    assert oen_pattern.search("Student OEN: 123456789")
    assert oen_pattern.search("OEN 123-456-789")
    assert not oen_pattern.search("12345")  # Too short


def test_pii_detects_phone():
    """PII scanner should detect phone numbers."""
    phone_pattern = _PII_PATTERNS[1][0]
    assert phone_pattern.search("Call me at (416) 555-1234")
    assert phone_pattern.search("Phone: 416-555-1234")
    assert not phone_pattern.search("123-456")  # Too short


def test_pii_detects_email():
    """PII scanner should detect email addresses."""
    email_pattern = _PII_PATTERNS[2][0]
    assert email_pattern.search("Contact: teacher@school.ca")
    assert email_pattern.search("Send to john.doe@example.com")
    assert not email_pattern.search("not an email")


def test_pii_check_clean_templates():
    """check_pii_safety should return empty list for clean data."""
    ctx = ValidationContext(
        frames=set(),
        indicators=set(),
        templates=set(),
        evidence_patterns=set(),
        refs=set(),
        tags=set(),
        indicator_to_frame={},
        templates_raw=[{"id": "test.template", "text": "This is clean text with {child} placeholder."}],
        evidence_raw=[],
    )
    errors = check_pii_safety(ctx)
    assert errors == []


def test_pii_check_catches_email_in_template():
    """check_pii_safety should catch email addresses in templates."""
    ctx = ValidationContext(
        frames=set(),
        indicators=set(),
        templates=set(),
        evidence_patterns=set(),
        refs=set(),
        tags=set(),
        indicator_to_frame={},
        templates_raw=[{"id": "test.template", "text": "Contact teacher@school.ca for more info."}],
        evidence_raw=[],
    )
    errors = check_pii_safety(ctx)
    assert len(errors) == 1
    assert "Email address detected" in errors[0]
