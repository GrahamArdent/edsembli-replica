---
id: doc.index
type: document
title: Canonical Index
version: 0.1.0
status: draft
tags: [index, canonical]
refs: []
updated: 2026-01-11
---

# Canonical Index

Start here for the current, authoritative documents and the saved research inputs.

Last updated: 2026-01-11

## Core (canonical)

- [Framework](framework.md)
	- The conceptual framework and decisions (intended to be the narrative “what/why”).
- [Infrastructure](infrastructure.md)
	- How the framework is made functional (file layout, conventions, schemas, tooling, governance).
- [Glossary](glossary.md)
	- Canonical definitions and controlled vocabulary (Frame, Indicator, Evidence Pattern, etc.).
- [Functional Requirements](requirements.md)
	- What the tooling/workflow must do (distinct from Python `requirements.txt`).

## Taxonomy & References

- [Frames Taxonomy](taxonomy/frames.yaml)
	- Canonical definitions of the four kindergarten frames with indicators.
- [Indicators Taxonomy](taxonomy/indicators.yaml)
	- Expanded indicator metadata (evidence signals, frame mapping).
- [CoL Sections Taxonomy](taxonomy/col-sections.yaml)
	- Canonical definition of Key Learning / Growth / Next Steps.
- [Tags Taxonomy](taxonomy/tags.yaml)
	- Controlled vocabulary for categorization.
- [Roles Taxonomy](taxonomy/roles.yaml)
	- Stakeholder role definitions (teacher, ECE, parent, etc.).
- [Bibliography](references/bibliography.yaml)
	- Source citations with stable reference IDs.

## Evidence & Templates

- [Evidence Patterns](evidence/README.md)
	- Reusable observation archetypes (e.g., Block Play).
- [Templates library](templates/README.md)
	- How templates are organized and used.
- [Comment templates (YAML)](templates/comment_templates.yaml)
	- Initial canonical template set (non-PII).

## Knowledge Base

- [Reporting Process SOP](knowledge/processes/process.reporting.workflow.md)
	- Standard workflow for the reporting cycle.
- [Entities](knowledge/entities/)
	- Detailed records of tools, policies, and organizations.

## Schemas & Validation

- [Schemas](schemas/README.md)
	- JSON Schema contracts for canonical artifacts.
- [Validation scripts](scripts/README.md)
	- Local validation and linting.

## Guidance & Safety

- [Privacy checklist](PRIVACY.md)
	- No-PII rules and review checklist.
- [Comment style guide](guidance/comment-style.md)
	- Tone/structure constraints for CoL narratives.

## Examples

- [Evidence Pattern Sample](examples/evidence-pattern-sample.md)
	- Template structure for documenting kindergarten observations.
- [Comment Template Sample](examples/comment-template-sample.md)
	- Template structure for Communication of Learning comments.

> Note: `examples/` is illustrative (structure-focused) and contains no PII.
> Canonical libraries, when created, should live under `evidence/` and `templates/` (or the canonical locations defined in `infrastructure.md`).

## Sources (reference inputs, not canonical)

- [Finding Assembly Report Card Software Information](sources/Finding%20Assembly%20Report%20Card%20Software%20Information.md)
	- Saved background research used to inform the framework.

## Planned artifacts (not yet created)

- Traceability: `datasets/traceability/matrix.parquet` (or `matrix.csv`)

## Conventions

- Keep canonical documents free of PII/student-identifying information.
- Treat `sources/` as reference-only; do not cite it as “authority” without extracting a supported claim into canonical docs.

## Project files

- [README](README.md)
- [Discussion notes](discussion.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Python dependencies](requirements.txt)

## Architecture Decision Records (ADRs)

- [ADR 0000: Template](decisions/0000-adr-template.md)
- [ADR 0001: Canonical vs Sources](decisions/0001-canonical-vs-sources.md)
- [ADR 0002: Framework vs Infrastructure Split](decisions/0002-framework-vs-infrastructure-split.md)
- [ADR 0003: Template Library Format](decisions/0003-template-library-format.md)
- [ADR 0004: Placeholder Convention](decisions/0004-placeholder-convention.md)
- [ADR 0005: ID Naming Convention](decisions/0005-id-naming-convention.md)
