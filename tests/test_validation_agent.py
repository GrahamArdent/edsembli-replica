"""Tests for template validation agent."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.agents.validation import ValidationAgent


def test_validation_agent_init():
    """Test validation agent initialization."""
    agent = ValidationAgent()
    assert agent.system_prompt is not None
    assert agent.model == "claude-sonnet-4"
    assert agent.temperature == 0.3
    assert agent.valid_indicator_ids is not None
    assert agent.approved_slots is not None


def test_validate_valid_template():
    """Test validation of a valid template."""
    agent = ValidationAgent()

    valid_template = {
        "id": "template.comment.belonging.key_learning.01",
        "type": "comment_template",
        "frame": "frame.belonging",
        "section": "key_learning",
        "tone": "parent_friendly",
        "slots": ["child", "pronoun_subject", "evidence"],
        "text": "{child} demonstrates belonging through {evidence}. {pronoun_subject} is engaged.",
        "indicators": ["indicator.belonging.identity"],
        "refs": ["ref.ontario.kindergarten.program.2016"],
        "status": "draft",
        "version": "0.1.0",
    }

    result = agent.validate(valid_template)
    assert result.overall_status in ["pass", "needs_revision"]  # May warn about textstat
    assert result.schema_valid is True
    assert result.privacy_safe is True
    assert result.slots_consistent is True
    assert result.indicators_valid is True


def test_validate_missing_fields():
    """Test validation catches missing required fields."""
    agent = ValidationAgent()

    incomplete_template = {
        "id": "template.comment.belonging.key_learning.001",
        "type": "comment_template",
        "text": "Some text",
        # Missing: frame, section, tone, slots, indicators, refs, status, version
    }

    result = agent.validate(incomplete_template)
    assert result.overall_status == "fail"
    assert result.schema_valid is False
    assert len(result.errors) > 0


def test_validate_pii_violation():
    """Test validation catches PII violations."""
    agent = ValidationAgent()

    pii_template = {
        "id": "template.comment.belonging.key_learning.001",
        "type": "comment_template",
        "frame": "frame.belonging",
        "section": "key_learning",
        "tone": "parent_friendly",
        "slots": ["child", "surname"],
        "text": "{child} {surname} demonstrates belonging.",
        "indicators": ["indicator.belonging.identity"],
        "refs": ["ref.ontario.kindergarten.program.2016"],
        "status": "draft",
        "version": "0.1.0",
    }

    result = agent.validate(pii_template)
    assert result.overall_status == "fail"
    assert result.privacy_safe is False


def test_validate_slot_mismatch():
    """Test validation catches slot inconsistencies."""
    agent = ValidationAgent()

    template = {
        "id": "template.comment.belonging.key_learning.001",
        "type": "comment_template",
        "frame": "frame.belonging",
        "section": "key_learning",
        "tone": "parent_friendly",
        "slots": ["child", "pronoun_subject"],  # Missing 'evidence'
        "text": "{child} demonstrates belonging through {evidence}.",
        "indicators": ["indicator.belonging.identity"],
        "refs": ["ref.ontario.kindergarten.program.2016"],
        "status": "draft",
        "version": "0.1.0",
    }

    result = agent.validate(template)
    assert result.overall_status == "fail"
    assert result.slots_consistent is False


def test_validate_invalid_indicator():
    """Test validation catches invalid indicators."""
    agent = ValidationAgent()

    template = {
        "id": "template.comment.belonging.key_learning.001",
        "type": "comment_template",
        "frame": "frame.belonging",
        "section": "key_learning",
        "tone": "parent_friendly",
        "slots": ["child"],
        "text": "{child} demonstrates belonging.",
        "indicators": ["indicator.fake.invalid"],
        "refs": ["ref.ontario.kindergarten.program.2016"],
        "status": "draft",
        "version": "0.1.0",
    }

    result = agent.validate(template)
    assert result.overall_status == "fail"
    assert result.indicators_valid is False


def test_validate_invalid_section():
    """Test validation catches invalid section types."""
    agent = ValidationAgent()

    template = {
        "id": "template.comment.belonging.invalid.001",
        "type": "comment_template",
        "frame": "frame.belonging",
        "section": "invalid_section",  # Invalid
        "tone": "parent_friendly",
        "slots": ["child"],
        "text": "{child} demonstrates belonging.",
        "indicators": ["indicator.belonging.identity"],
        "refs": ["ref.ontario.kindergarten.program.2016"],
        "status": "draft",
        "version": "0.1.0",
    }

    result = agent.validate(template)
    assert result.overall_status == "fail"
    assert result.schema_valid is False
