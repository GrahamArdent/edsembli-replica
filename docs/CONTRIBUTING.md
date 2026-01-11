---
id: doc.contributing
type: document
title: Contributing Guide
version: 0.1.0
status: draft
tags: [contributing, governance]
refs: []
updated: 2026-01-11
---

# Contributing Guide

Thank you for helping define the Edsembli Replica Framework.

## 1. Principles

1.  **Privacy First**: No student data. Ever.
2.  **Canonical vs. Source**:
    - Editing "Truth"? Edit canonical docs in `docs/` (e.g., `docs/framework.md`, `docs/infrastructure.md`) or `schemas/`/`taxonomy/`/`knowledge/`.
    - Adding Research? Add a Markdown or PDF file to `sources/`.
3.  **Traceability**: If you make a claim, link it to a reference ID or a Source file.

## 2. How to make changes

### Editing the Framework (Narrative)
- Edit `docs/framework.md`.
- Keep it high-level.
- Update `CHANGELOG.md`.

### Editing the Specification (Infrastructure)
- Edit `docs/infrastructure.md`.
- If changing an ID scheme or data model, create a new ADR in `decisions/`.

### Editing Functional Requirements
- Edit `docs/requirements.md`.
- Use lowercase IDs: `req.category.number` (e.g., `req.privacy.1`).
- Use MUST/SHOULD/MAY language per RFC 2119.

### Adding new "Knowledge" (Patterns, Templates)
- Follow the ID naming convention: `type.domain.name`.
- Ensure it uses the correct Frontmatter schema.

## 3. Version Policy

All canonical files include a `version` field. When editing:

| Change Type | Version Bump | Example |
|-------------|--------------|--------|
| Typo/minor wording | Patch | `0.1.0` → `0.1.1` |
| New template/indicator | Minor | `0.1.0` → `0.2.0` |
| Breaking schema change | Major | `0.1.0` → `1.0.0` |

**Always update the `updated` date in front matter when making changes.**

## 3.1 Activate Pre-commit (recommended)

This repo includes a `.pre-commit-config.yaml`. To enable local checks on commit:

```bash
pip install pre-commit
pre-commit install
```

## 4. Decision Process (ADRs)

For significant architectural decisions (e.g., "We will switch from YAML to TOML"), please create an Architecture Decision Record in `decisions/`.
- Copy `decisions/0000-adr-template.md`.
- Number it sequentially.

Key decisions already documented:
- ADR 0001: Canonical vs sources distinction
- ADR 0002: Framework vs infrastructure split
- ADR 0003: Template library format (single YAML)
- ADR 0004: Curly-brace placeholder convention
- ADR 0005: ID naming convention (type.domain.name)
