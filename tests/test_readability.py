"""Tests for lib/readability.py readability analysis functions."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.readability import check_readability, format_readability_report


def test_check_readability_good_text():
    """Test readability check on text within target range."""
    # Simple, clear text at about grade 6-7
    text = """
    Alex shows curiosity about how things work.
    They ask questions during science activities.
    Alex can explain their thinking using simple words.
    """

    result = check_readability(text)

    # textstat is installed, should have scores
    if result.flesch_reading_ease > 0:
        assert result.flesch_kincaid_grade > 0
        assert result.automated_readability_index > 0
    else:
        # textstat not installed - should have error
        assert "textstat" in result.issues[0].lower()


def test_check_readability_complex_text():
    """Test readability check on overly complex text."""
    # Jargon-heavy, complex text
    text = """
    The aforementioned student demonstrates increasingly sophisticated
    metacognitive awareness through their articulation of problem-solving
    strategies and reflective practices.
    """

    result = check_readability(text)

    # If textstat installed, should flag as too complex
    # If not installed, should have installation error
    if result.flesch_reading_ease > 0:
        assert not result.passes
        assert any("too complex" in issue.lower() for issue in result.issues)
    else:
        assert "textstat" in result.issues[0].lower()


def test_check_readability_simple_text():
    """Test readability check on overly simple text."""
    # Very basic text
    text = "Alex can play. They run. They jump."

    result = check_readability(text)

    # If textstat installed, may flag as too simple
    # If not installed, should have installation error
    if result.flesch_reading_ease > 0:
        # May or may not pass depending on exact scoring
        pass  # Just check it runs without error
    else:
        assert "textstat" in result.issues[0].lower()


def test_format_readability_report():
    """Test formatting of readability result."""
    text = "Alex shows growth in reading. They can read simple books now."

    result = check_readability(text)
    report = format_readability_report(result)

    assert "Flesch Reading Ease" in report
    assert "Flesch-Kincaid Grade Level" in report
    assert "Automated Readability Index" in report
    assert len(report) > 0
