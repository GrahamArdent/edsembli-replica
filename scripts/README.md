---
id: doc.scripts.readme
type: document
title: Scripts
version: 0.1.0
status: draft
tags: [scripts, validation]
refs: []
updated: 2026-01-11
---

# Scripts

Local scripts for validating, linting, and analyzing canonical artifacts.

## Usage

### Validation (schema + front matter)
```bash
python scripts/validate.py
```
Checks all YAML files against JSON Schemas and verifies Markdown front matter.

### Linting (references + placeholders)
```bash
python scripts/lint.py
```
Verifies that all `ref.*` and `indicator.*` references exist, and checks for bracket-style placeholders.

### Coverage Analysis
```bash
python scripts/coverage.py
```
Reports indicator-to-template coverage. Identifies indicators with no template references.

### Traceability Matrix Generation
```bash
python scripts/generate_matrix.py
```
Generates `datasets/traceability/matrix.csv` and `datasets/traceability/matrix.parquet` linking frames, indicators, evidence patterns, templates, and references.

## Exit Codes

- `0`: All checks pass
- `1`: One or more checks failed

These scripts run locally and make no network calls.
