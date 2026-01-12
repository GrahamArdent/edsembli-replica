---
id: doc.changelog
type: document
title: Changelog
version: 0.1.0
status: draft
tags: [changelog]
refs: []
updated: 2026-01-11
---

# Changelog

All notable changes to this repository’s *canonical* artifacts are documented here.

The format is loosely based on Keep a Changelog, and this project aims to follow Semantic Versioning where it makes sense for schemas/artifacts.

## [Unreleased]

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
