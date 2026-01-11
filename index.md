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

## Explanation (why it exists)

- [Framework](docs/framework.md)
	- The conceptual framework and decisions (intended to be the narrative “what/why”).

## Reference (contracts and canonical definitions)

- [Infrastructure](docs/infrastructure.md)
	- How the framework is made functional (file layout, conventions, schemas, tooling, governance).
- [Glossary](docs/glossary.md)
	- Canonical definitions and controlled vocabulary (Frame, Indicator, Evidence Pattern, etc.).
- [Functional Requirements](docs/requirements.md)
	- What the tooling/workflow must do (distinct from Python `requirements.txt`).

## Taxonomy & Sources of Truth

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

## Libraries (evidence + templates)

- [Evidence Patterns](evidence/README.md)
	- Reusable observation archetypes (15 patterns covering all frames).
- [Templates library](templates/README.md)
	- How templates are organized and used.
- [Comment templates (YAML)](templates/comment_templates.yaml)
	- Initial canonical template set (36 templates, non-PII).

## How-to (processes)

- [Reporting Process SOP](knowledge/processes/process.reporting.workflow.md)
	- Standard workflow for the reporting cycle.
- [Content Review Process](knowledge/processes/process.content.review.md)
	- Quality checklist for new content.
- [Contributor Onboarding](knowledge/processes/process.onboarding.contributor.md)
	- Setup guide for new contributors.
- [Entities](knowledge/entities/)
	- Detailed records of tools, policies, and organizations.

## Datasets (planned/derived)

- [Traceability Matrix](datasets/traceability/README.md)
	- Coverage and audit datasets (generated + planned extensions).

## Validation & Automation

- [Schemas](schemas/README.md)
	- JSON Schema contracts for canonical artifacts (10 schemas).
- [Validation scripts](scripts/README.md)
	- Local validation and linting.
- [Testing and validation](docs/TESTING.md)
	- What checks exist (local + CI) and what “passing” means.

## Guidance & Safety

- [Privacy checklist](docs/PRIVACY.md)
	- No-PII rules and review checklist.
- [Security policy](docs/SECURITY.md)
	- How to report issues; reinforces the no-PII boundary.
- [Comment style guide](guidance/comment-style.md)
	- Tone/structure constraints for CoL narratives.
- [Board customization guide](guidance/board-customization.md)
	- How boards can adapt templates locally.
- [Override and customization policy](guidance/override-policy.md)
	- Explicit boundaries for local adaptations vs canonical content.

## Examples (Illustrative Only)

- [Evidence Pattern Sample](examples/evidence-pattern-sample.md)
	- Original structural template (superseded by `evidence/` folder).
- [Comment Template Sample](examples/comment-template-sample.md)
	- Original structural template (superseded by `templates/` folder).

> **Note:** The `examples/` folder contains the original illustrative samples used during design.
> Canonical content now lives in `evidence/` and `templates/`.

> Note: `examples/` is illustrative (structure-focused) and contains no PII.
> Canonical libraries, when created, should live under `evidence/` and `templates/` (or the canonical locations defined in `docs/infrastructure.md`).

## Sources (reference inputs, not canonical)

- [Finding Assembly Report Card Software Information](sources/Finding%20Assembly%20Report%20Card%20Software%20Information.md)
	- Saved background research used to inform the framework.

## Planned artifacts (not yet created)

- Traceability matrix extensions: additional derived views (e.g., per-frame exports)

## Conventions

- Keep canonical documents free of PII/student-identifying information.
- Treat `sources/` as reference-only; do not cite it as “authority” without extracting a supported claim into canonical docs.

## Project files

- [README](README.md)
- [Discussion notes](docs/discussion.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](docs/CHANGELOG.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Release and versioning](docs/RELEASE.md)
- [Python dependencies](requirements.txt)

## Audits

- [Audits](audits/README.md)
	- Periodic repository audits and snapshots.

## Architecture Decision Records (ADRs)

- [ADR 0000: Template](decisions/0000-adr-template.md)
- [ADR 0001: Canonical vs Sources](decisions/0001-canonical-vs-sources.md)
- [ADR 0002: Framework vs Infrastructure Split](decisions/0002-framework-vs-infrastructure-split.md)
- [ADR 0003: Template Library Format](decisions/0003-template-library-format.md)
- [ADR 0004: Placeholder Convention](decisions/0004-placeholder-convention.md)
- [ADR 0005: ID Naming Convention](decisions/0005-id-naming-convention.md)
