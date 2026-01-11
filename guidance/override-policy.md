---
id: doc.guidance.override_policy
type: document
title: Override and Customization Policy
version: 0.1.0
status: draft
tags: [guidance, customization, governance]
refs:
  - ref.ontario.kindergarten.program.2016
  - ref.ontario.growing.success.2010
updated: 2026-01-11
---

# Override and Customization Policy

This policy defines what may be customized locally (e.g., by a board) and what must remain canonical to preserve traceability and compliance.

## Allowed overrides (local)

- **Wording adjustments** that preserve meaning and strengths-based tone.
- **Terminology localization** (e.g., “FDK” vs “Kindergarten”).
- **Faith-based extensions** where applicable (additive, non-exclusionary, and still aligned to indicators).
- **Length/format constraints** driven by SIS character limits.
- **Home-school strategies** localized to community resources.

## Not allowed (must remain canonical)

- **PII boundary**: no student-identifying information or student work samples.
- **Canonical IDs**: do not rename `frame.*`, `indicator.*`, `template.*`, `evidence.pattern.*`, or `ref.*` IDs.
- **Frame/indicator semantics**: do not alter indicator intent or switch indicators to “fit” a comment.
- **Traceability removal**: do not remove `indicators` or `refs` from templates.

## Required when customizing

- Keep upstream compatibility by using a fork/branch.
- Document changes (what/why) and maintain version bumps.
- Run local checks (`validate.py`, `lint.py`, `coverage.py`) before sharing.

## Recommended local extension model

Prefer additive overlays rather than edits-in-place:

- Add new templates alongside canonical ones.
- Keep canonical templates unchanged unless required.
- Use local tags to track board-specific variants.
