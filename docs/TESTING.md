---
id: doc.testing
type: document
title: Testing and Validation
version: 0.1.1
status: draft
tags: [testing, validation, ci]
refs: []
updated: 2026-01-12
---

# Testing and Validation

This repo focuses on structural correctness and drift prevention rather than unit tests.

## Local checks

Run these before opening a PR:

- `python scripts/validate.py` (schemas + front matter)
- `python scripts/lint.py` (reference integrity + placeholder conventions)
- `python scripts/coverage.py` (indicator coverage)

VGReport (UI ↔ engine) contract drift prevention:

- IPC contracts live in `contracts/`.
- Generated TS types live in `vgreport/src/contracts/generated.ts`.
- `python scripts/validate.py` fails if schemas and generated TS are out of sync.
- Regenerate via: `cd vgreport; npm run contracts:gen`

## VGReport Kindergarten alignment QA checklist

Run automated gates:

- Full repo gates: `./check.bat`
- VGReport unit tests: `cd vgreport && npm test`
- Tauri smoke E2E (boots desktop runtime): `cd vgreport && npm run e2e:tauri`

Manual spot-checks (no PII):

- Export Center → Clipboard preset: each box has a Copy button and copies plain text only
- Export Center → Copy all: includes headings and preserves CRLF newlines
- Export Center → CSV presets: file includes UTF-8 BOM, CRLF row endings, stable header order, always-quoted fields
- Export gating: unapproved ECE drafts and invalid renders export as empty

## CI

GitHub Actions runs the same checks on pull requests.

## What “passing” means

- All canonical files conform to their schemas.
- All IDs referenced by templates exist.
- Coverage meets the minimum bar (currently: every indicator has at least one template).
