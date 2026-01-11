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
