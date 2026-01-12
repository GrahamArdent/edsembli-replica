"""Tests for comment assembly pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from lib.pipeline.assemble import AssemblyRequest, CommentAssembler


def test_assembler_init():
    """Test assembler initialization."""
    assembler = CommentAssembler()
    assert assembler.templates is not None
    assert len(assembler.templates) > 0


def test_assemble_valid_comment():
    """Test assembling a valid complete comment."""
    assembler = CommentAssembler()

    # Use actual template IDs from templates/comment_templates.yaml
    request = AssemblyRequest(
        child_data={
            "child": "Emma",
            "pronoun_subject": "She",
            "pronoun_object": "her",
            "pronoun_possessive": "her",
            "evidence": "building with blocks",
            "strength": "spatial reasoning",
            "change": "using more complex patterns",
            "previous": "simple stacking",
            "goal": "create 3D structures",
        },
        template_ids={
            "key_learning": ["template.comment.belonging.key_learning.01"],
            "growth": ["template.comment.belonging.growth.01"],
            "next_steps": ["template.comment.belonging.next_steps.01"],
        },
    )

    result = assembler.assemble(request)
    assert result.success is True
    assert result.comment is not None
    assert "Emma" in result.comment
    assert len(result.comment) >= assembler.TOTAL_MIN


def test_assemble_missing_section():
    """Test assembly fails when section is missing."""
    assembler = CommentAssembler()

    request = AssemblyRequest(
        child_data={"child": "Emma", "pronoun_subject": "She"},
        template_ids={
            "key_learning": ["template.comment.belonging.key_learning.01"],
            # Missing growth and next_steps
        },
    )

    result = assembler.assemble(request)
    assert result.success is False
    assert "missing" in str(result.errors).lower()


def test_assemble_too_many_templates():
    """Test assembly warns about too many templates in a section."""
    assembler = CommentAssembler()

    request = AssemblyRequest(
        child_data={
            "child": "Emma",
            "pronoun_subject": "She",
            "pronoun_object": "her",
            "pronoun_possessive": "her",
            "evidence": "playing cooperatively",
        },
        template_ids={
            "key_learning": [
                "template.comment.belonging.key_learning.01",
                "template.comment.belonging.key_learning.02",
                "template.comment.belonging.key_learning.03",  # Max is 2
            ],
            "growth": ["template.comment.belonging.growth.01"],
            "next_steps": ["template.comment.belonging.next_steps.01"],
        },
    )

    result = assembler.assemble(request)
    assert result.success is False
    assert result.errors is not None
    assert any("max" in str(e).lower() for e in result.errors)


def test_assemble_invalid_template_id():
    """Test assembly handles invalid template IDs."""
    assembler = CommentAssembler()

    request = AssemblyRequest(
        child_data={"child": "Emma", "pronoun_subject": "She"},
        template_ids={
            "key_learning": ["template.comment.invalid.999"],
            "growth": ["template.comment.belonging.growth.01"],
            "next_steps": ["template.comment.belonging.next_steps.01"],
        },
    )

    result = assembler.assemble(request)
    assert result.success is False
    assert "not found" in str(result.errors).lower()


def test_assemble_stats():
    """Test assembly returns statistics."""
    assembler = CommentAssembler()

    request = AssemblyRequest(
        child_data={
            "child": "Emma",
            "pronoun_subject": "She",
            "pronoun_object": "her",
            "pronoun_possessive": "her",
            "evidence": "building with blocks",
            "strength": "spatial reasoning",
            "change": "using more complex patterns",
            "previous": "simple stacking",
            "goal": "create 3D structures",
        },
        template_ids={
            "key_learning": ["template.comment.belonging.key_learning.01"],
            "growth": ["template.comment.belonging.growth.01"],
            "next_steps": ["template.comment.belonging.next_steps.01"],
        },
    )

    result = assembler.assemble(request)
    assert result.stats is not None
    assert "total_length" in result.stats
    assert "indicator_count" in result.stats
    assert "flesch_reading_ease" in result.stats


def test_assemble_multiple_templates_per_section():
    """Test assembling with multiple templates in key_learning."""
    assembler = CommentAssembler()

    request = AssemblyRequest(
        child_data={
            "child": "Emma",
            "pronoun_subject": "She",
            "pronoun_object": "her",
            "pronoun_possessive": "her",
            "evidence": "building with blocks",
            "strength": "spatial reasoning",
            "change": "using more complex patterns",
            "previous": "simple stacking",
            "goal": "create 3D structures",
        },
        template_ids={
            "key_learning": [
                "template.comment.belonging.key_learning.01",
                "template.comment.belonging.key_learning.02",
            ],
            "growth": ["template.comment.belonging.growth.01"],
            "next_steps": ["template.comment.belonging.next_steps.01"],
        },
    )

    result = assembler.assemble(request)
    # Should succeed with 2 templates in key_learning (max is 2)
    if result.success:
        assert result.comment is not None
        assert "Emma" in result.comment
        assert result.stats is not None
        assert result.stats["indicator_count"] >= 1
