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

## Quick Start

**Run all checks with one command:**
```bash
python scripts/check_all.py        # Full validation
python scripts/check_all.py --quick # Fast checks only (skips pytest/pyright)
```

## Individual Scripts

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

### Derived Dataset Validation
```bash
python scripts/validate_datasets.py
```
Validates `datasets/traceability/matrix.csv` (and `matrix.parquet` if present) against `datasets/traceability/matrix.schema.json`.

### Documentation Staging
```bash
python scripts/sync_docs.py
```
Copies canonical content into `docs_site/` for MkDocs consumption.

### Index Link Verification
```bash
python scripts/check_index.py
```
Verifies that all canonical files (docs, taxonomy, schemas, etc.) are linked in `index.md`.

### Quick Queries (CLI)
```bash
python scripts/edsembli_cli.py --help
python scripts/edsembli_cli.py template-search "belonging"
python scripts/edsembli_cli.py matrix-sql "select frame_id, count(*) as n from matrix group by 1 order by n desc"
```
Provides lightweight, local exploration tools (no network calls, no PII).

## Exit Codes

- `0`: All checks pass
- `1`: One or more checks failed

These scripts run locally and make no network calls.
