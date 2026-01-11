---
id: doc.framework
type: document
title: Framework (Ontario Catholic Kindergarten CoL + Edsembli)
version: 0.1.0
status: draft
tags: [framework, narrative, kindergarten, col]
refs: []
updated: 2026-01-11
---

# Framework (Ontario Catholic Kindergarten CoL + Edsembli)

> Purpose: a short, human-readable narrative of what this framework is and why it exists.
> For the structured specification (schemas, IDs, traceability, tooling), see `infrastructure.md`.
>
> Last updated: 2026-01-11

## 1) What this is

This repository defines a design-first framework for producing consistent, parent-friendly Kindergarten “Communication of Learning” (CoL) narrative comments aligned to Ontario’s four Frames, while keeping a strict **no-PII** boundary.

The framework is designed to be:
- **Auditable** (traceable to sources and internal decisions)
- **Maintainable** (clear canonical artifacts and conventions)
- **Reusable** (evidence patterns and comment templates, not student data)

## 2) What this is not

- Not an implementation of Edsembli (or any SIS)
- Not a storage location for student observations, names, photos, or any identifying information
- Not a “one-click report card generator”

## 3) Guiding principles

- **Privacy-first**: the canonical repo remains safe to share.
- **Clarity for families**: comments avoid jargon and stay concrete.
- **Grounded outputs**: important claims should be supported by durable citations/IDs.
- **Single source of truth**: canonical artifacts are authoritative; research inputs are reference-only.

## 4) Conceptual model (high-level)

- **Frames** are the primary organizing lens for Kindergarten learning.
- **Indicators / expectations** (where you choose to define them) make “coverage” concrete.
- **Evidence patterns** describe *how learning may show up* (structures/archetypes, not real observations).
- **Comment templates** support consistent CoL writing across:
  - Key Learning
  - Growth in Learning
  - Next Steps in Learning
- A **traceability matrix** links Frames/Indicators → Evidence Patterns → Comment Templates → References.

## 5) Canonical vs sources

- Canonical artifacts are the ones you should treat as “truth” and maintain over time.
- `sources/` contains saved background materials used to inform canonical decisions.

Start at `index.md` for the current canonical index.

## 6) How to use this framework (human workflow)

1) Start with the Frame and (optional) indicator you want to write about.
2) Choose an evidence pattern that fits the classroom context.
3) Select a comment template that matches the section (Key Learning / Growth / Next Steps) and desired tone.
4) Adapt the template with non-identifying details (no names/unique identifiers) in a separate, private system.
5) Keep improvements in canonical templates/patterns; keep student-specific content out of this repo.

## 7) Where the “spec” lives

All structured conventions and future “contracts” are documented in `infrastructure.md`, including:
- Canonical repository layout
- ID conventions and front matter expectations
- Schema and traceability design
- Governance/versioning guidance

## 8) References

- Background research is preserved in `sources/Finding Assembly Report Card Software Information.md`.
