---
id: doc.testing
type: document
title: Testing and Validation
version: 0.1.0
status: draft
tags: [testing, validation, ci]
refs: []
updated: 2026-01-11
---

# Testing and Validation

This repo focuses on structural correctness and drift prevention rather than unit tests.

## Local checks

Run these before opening a PR:

- `python scripts/validate.py` (schemas + front matter)
- `python scripts/lint.py` (reference integrity + placeholder conventions)
- `python scripts/coverage.py` (indicator coverage)

## CI

GitHub Actions runs the same checks on pull requests.

## What “passing” means

- All canonical files conform to their schemas.
- All IDs referenced by templates exist.
- Coverage meets the minimum bar (currently: every indicator has at least one template).
