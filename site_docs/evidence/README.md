---
id: doc.evidence.readme
type: document
title: Evidence Patterns
version: 0.1.0
status: draft
tags: [evidence, patterns]
refs: []
updated: 2026-01-11
---

# Evidence Patterns

This folder contains **Evidence Patterns** (`evidence.pattern.*`).

## What is an Evidence Pattern?

An Evidence Pattern is a reusable, non-PII archetype of a learning scenario. It serves as a structure for documenting observations without storing actual student data.

## Current Patterns

| Pattern | Frame | Primary Indicators |
|---------|-------|-------------------|
| `block_play` | Belonging | relationships, community |
| `dramatic_play` | Belonging | relationships, identity |
| `snack_time` | Self-Regulation | health, attention |
| `circle_time` | Self-Regulation | attention, emotions |
| `outdoor_play` | Self-Regulation | health |
| `conflict_resolution` | Self-Regulation | emotions |
| `read_aloud` | Literacy/Math | reading, oral_language |
| `writing_centre` | Literacy/Math | writing, oral_language |
| `math_manipulatives` | Literacy/Math | numeracy |
| `art_creation` | Problem Solving | creativity, innovation |
| `inquiry_investigation` | Problem Solving | inquiry, innovation |
| `construction_building` | Problem Solving | innovation, creativity |
| `music_movement` | Belonging | community, identity |
| `sand_water` | Problem Solving | inquiry |
| `transition_time` | Self-Regulation | attention, emotions |

## Structure

Each evidence pattern file defines:
- **Context**: The classroom situation or area
- **Observable Behaviors**: Signals linked to specific Indicators
- **Teacher Moves**: Prompts and questions
- **Sample Observation Template**: A non-PII template for documentation

## Adding New Patterns

1. Copy an existing pattern file
2. Update the ID, title, and metadata
3. Ensure indicators exist in `taxonomy/indicators.yaml`
4. Run `python scripts/validate.py` to verify
