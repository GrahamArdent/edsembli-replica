---
id: doc.changelog
type: document
title: Changelog
version: 0.1.1
status: draft
tags: [changelog]
refs: []
updated: 2026-01-12
---

# Changelog

All notable changes to this repository’s *canonical* artifacts are documented here.

The format is loosely based on Keep a Changelog, and this project aims to follow Semantic Versioning where it makes sense for schemas/artifacts.

## [Unreleased]

### Added (2026-01-12)

- VGReport Kindergarten “golden outputs” specification (clipboard-per-box and 12-box CSV)
- VGReport Kindergarten completeness / export-ready semantics (per-box, approval-gated)
- Clarified applicability of canonical assembly constraints to VGReport 12-box workflow
- Master execution prompt for phase-gated implementation (`gameplan_prompt.md`)

### Added (Phase 4 Sprint 4.2 - 2026-01-11)

- Template generation agent (`lib/agents/generation.py`) for AI-assisted template creation
- Validation agent (`lib/agents/validation.py`) for quality assurance and feedback
- Comment assembly pipeline (`lib/pipeline/assemble.py`) for building complete CoL comments
- `edsembli review` CLI command for validating draft templates with detailed feedback
- Integration tests for agents and pipeline (18 new tests, 42 total)
- Mock LLM mode for testing without API credentials

### Added (Phase 4 Sprint 4.1 - 2026-01-11)

- Prompt templates library in `prompts/` for AI agent integration
- System prompts for generation, validation, and simplification tasks
- Assembly library (`lib/assembly.py`) for slot filling with PII safety checks
- Readability library (`lib/readability.py`) using textstat for Flesch scores
- Tests for assembly and readability functions (8 new tests, 24 total)

### Added (Phase 3B Sprint 3B.2 - 2026-01-11)

- Evidence-template matrix CLI command (`edsembli evidence-matrix`) showing heuristic matches using ADR-001 algorithm
- Template deprecation CLI command (`edsembli templates --show-deprecated`) listing deprecated templates
- Reports section added to MkDocs navigation (coverage.md and gaps.md)
- Heuristic matching algorithm with frame match (+3), indicator match (+5), preferred evidence (+10)

### Added (Phase 3B Sprint 3B.1 - 2026-01-11)

- Coverage report generator (`scripts/generate_coverage_report.py`) showing template distribution across frames, indicators, and sections
- Gaps report generator (`scripts/generate_gaps_report.py`) identifying indicators with <2 templates and sections with <3 templates
- Auto-generated reports: `reports/coverage.md` and `reports/gaps.md`
- French text placeholders (`text_fr: "TODO"`) added to all 36 templates in preparation for bilingual support
- Reports section added to `index.md` for easy navigation to coverage analysis

### Changed

- Template schema now supports bilingual content with `text_fr` field
- Gap reporting exits with code 1 when critical gaps exist (CI integration ready)

### Previous Work

- Initialize documentation scaffolding (index/framework/infrastructure, sources retention).
- Normalize ID examples and placeholder conventions across spec and examples.
- Add discussion notes and clarify examples as illustrative.
- Add privacy checklist and comment style guidance.
- Add expanded taxonomy files (indicators, CoL sections).
- Seed knowledge entities for Edsembli, ONSIS, and key policy/curriculum.
- Add initial templates library (36 comment templates).
- Add schemas and local validation/lint scripts.
- Implement traceability matrix generation (`scripts/generate_matrix.py`) and generate `datasets/traceability/matrix.csv` + `matrix.parquet`.
- Consolidate canonical docs under `docs/` and update all internal links.
- Add customization boundaries via `guidance/override-policy.md`.
- Install and document pre-commit hooks (local activation).
