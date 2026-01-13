---
id: doc.requirements
type: document
title: Functional Requirements
version: 0.1.2
status: stable
tags: [requirements, governance]
refs: []
updated: 2026-01-12
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

## 6. VGReport Kindergarten Completeness (12-box workflow)

These requirements define what VGReport considers “complete” and “export-ready” for the Kindergarten 12-box workflow (4 Frames × 3 Sections).

- **req.kg.complete.1**: The system MUST treat each Kindergarten box (Frame × Section) as an independent required field for export readiness.
- **req.kg.complete.2**: For Edsembli-aligned exports, the system MUST block export if any of the 12 Kindergarten boxes are empty.
- **req.kg.complete.3**: For Edsembli-aligned exports, the system MUST block export if any of the 12 Kindergarten boxes are not approved (Teacher/ECE approval workflow).
- **req.kg.complete.4**: The system MUST block export on hard template/render errors (e.g., required placeholder missing) and MUST surface a clear, actionable error message.
- **req.kg.complete.5**: The system SHOULD warn (but MUST NOT block export) on soft guardrails such as sentence-count heuristics, repetition indicators, and box-fit heuristic overflows unless explicitly configured otherwise.
- **req.kg.complete.6**: Any UI label claiming “complete” (e.g., progress summary) MUST state whether it means “draft complete” (non-empty) or “export-ready” (approved + non-empty + no blocking errors).
