---
id: doc.release
type: document
title: Release and Versioning
version: 0.1.0
status: draft
tags: [release, versioning, governance]
refs: []
updated: 2026-01-11
---

# Release and Versioning

This repository versions *documents, schemas, and libraries* so changes are auditable and reviewable.

## What gets versioned

- Canonical Markdown documents (front matter: `version`, `updated`)
- JSON Schemas (field: `$version`)
- Taxonomy and libraries (YAML files; change history tracked via git)

## Versioning rules

Use semantic versioning concepts:

- **Patch**: typos, clarifications, non-behavioral edits
- **Minor**: additive content (new templates, new evidence patterns, new indicators metadata)
- **Major**: breaking contract changes (schema changes that invalidate existing artifacts)

## When to update CHANGELOG

Update CHANGELOG.md when you:

- Add/remove/rename canonical IDs
- Add/modify evidence patterns or templates
- Change schemas or validation behavior
- Introduce new governance/process documents

## Release process (lightweight)

1. Make changes on a branch.
2. Run local checks: `python scripts/validate.py`, `python scripts/lint.py`, `python scripts/coverage.py`.
3. Update front matter `version` and `updated` where applicable.
4. Update CHANGELOG.md.
5. Merge via PR.

Optional: tag the merge commit (e.g., `v0.2.0`) if you want externally visible milestones.
