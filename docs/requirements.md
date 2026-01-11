---
id: doc.requirements
type: document
title: Functional Requirements
version: 0.1.0
status: draft
tags: [requirements, governance]
refs: []
updated: 2026-01-11
---

# Functional Requirements

> Scope: Requirements for the *tooling* and *workflow* that this framework supports.
> This is distinct from the Python `requirements.txt` which lists libraries.

## 1. Traceability & Integrity

- **req.trace.1**: Every Comment Template MUST be traceable back to at least one specific Frame or Expectation.
- **req.trace.2**: Every Evidence Pattern MUST cite its source (e.g., `ref.ontario.kindergarten.program.2016`).
- **req.integrity.1**: Canonical artifacts MUST have stable UIDs (`id` field in frontmatter).

## 2. Privacy & Safety

- **req.privacy.1**: The repository content MUST NOT contain PII (Personally Identifiable Information).
- **req.privacy.2**: Templates MUST use slots (`{name}`) rather than hardcoded fake names to prevent accidental copying.

## 3. Schemas & Validation

- **req.schema.1**: All canonical Markdown files (Entities, Docs) MUST function with the defined YAML frontmatter schema.
- **req.validation.1**: The system MUST be able to validate that all internal links (`ref.*`) resolve to an existing ID.

## 4. Output Generation

- **req.gen.1**: The system MUST be able to export a "Matrix View" (CSV/Parquet) of the relationships between Frames and Templates.
- **req.gen.2**: The system SHOULD allow filtering templates by "Tone" (e.g., Parent-friendly vs. Formal).

## 5. Workflow

- **req.workflow.1**: Changes to `docs/framework.md` (Narrative) MUST be manually reviewed to ensure they align with `docs/infrastructure.md` (Spec).
