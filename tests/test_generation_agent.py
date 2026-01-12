"""Tests for template generation agent."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.agents.generation import GenerationAgent, GenerationRequest


def test_generation_agent_init():
    """Test generation agent initialization."""
    agent = GenerationAgent()
    assert agent.system_prompt is not None
    assert agent.model == "claude-sonnet-4"
    assert agent.temperature == 0.7
    assert agent.templates is not None


def test_generation_request():
    """Test generation request creation."""
    request = GenerationRequest(
        frame="frame.belonging",
        section="key_learning",
        indicator="indicator.belonging.identity",
        evidence_pattern="Shows sense of self through play",
    )
    assert request.frame == "frame.belonging"
    assert request.section == "key_learning"


def test_get_similar_examples():
    """Test finding similar template examples."""
    agent = GenerationAgent()
    request = GenerationRequest(
        frame="frame.belonging",
        section="key_learning",
        indicator="indicator.belonging.identity",
    )

    examples = agent._get_similar_examples(request, limit=3)
    assert len(examples) <= 3
    # All examples should match frame and section
    for ex in examples:
        assert ex["frame"] == "frame.belonging"
        assert ex["section"] == "key_learning"


def test_build_user_prompt():
    """Test user prompt construction."""
    agent = GenerationAgent()
    request = GenerationRequest(
        frame="frame.belonging",
        section="key_learning",
        indicator="indicator.belonging.identity",
    )

    prompt = agent._build_user_prompt(request)
    assert "frame.belonging" in prompt
    assert "key_learning" in prompt
    assert "indicator.belonging.identity" in prompt
    assert "Example" in prompt  # Should include examples


def test_mock_generate():
    """Test mock template generation."""
    agent = GenerationAgent()
    request = GenerationRequest(
        frame="frame.belonging",
        section="key_learning",
        indicator="indicator.belonging.identity",
    )

    result = agent.generate(request)
    assert result.success is True
    assert result.template is not None
    assert result.template["frame"] == "frame.belonging"
    assert result.template["section"] == "key_learning"
    assert "indicator.belonging.identity" in result.template["indicators"]


def test_mock_generate_all_sections():
    """Test mock generation for all section types."""
    agent = GenerationAgent()
    sections = ["key_learning", "growth", "next_steps"]

    for section in sections:
        request = GenerationRequest(
            frame="frame.selfregulation",
            section=section,
            indicator="indicator.selfregulation.emotions",
        )
        result = agent.generate(request)
        assert result.success is True
        assert result.template is not None
        assert result.template["section"] == section
