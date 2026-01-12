---
id: doc.index
type: document
title: Canonical Index
version: 0.2.0
status: stable
tags: [index, canonical, source-of-truth]
refs: []
updated: 2026-01-11
---

# Canonical Index

Start here for the current, authoritative documents and the saved research inputs.

Last updated: 2026-01-11

## Project Status

- **Version**: 0.2.0 (Active Development)
- **Validation**: Strict (Pre-commit hooks, Type checking)
- **Documentation**: Canonical files in root, auto-synced to site.

## Quick Start

1. **Setup**: Run `pip install -r requirements.lock.txt` and `pre-commit install`.
2. **Concept**: Read [docs/framework.md](docs/framework.md) for the core philosophy.
3. **Validate**: Run `.\check --quick` to verify everything works.
4. **CLI**: Run `python scripts/edsembli_cli.py --help` to explore tools.

## Explanation (why it exists)

- [Framework](docs/framework.md)
	- The conceptual framework and decisions (intended to be the narrative “what/why”).

## Reference (contracts and canonical definitions)

- [Infrastructure](docs/infrastructure.md)
	- How the framework is made functional (file layout, conventions, schemas, tooling, governance).
- [Glossary](docs/glossary.md)
	- Standard vocabulary for the project.
- [SIS Integration Formats](docs/integration/sis-formats.md)
	- Export formats for integrating templates and comments with Student Information Systems.
- [Board Customization Guide](guidance/board-customization.md)
	- How to customize the framework for specific school boards.
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
- [Slot Guidance](taxonomy/slot_guidance.yaml)
	- Slot types, validation rules, and pronoun localization (en/fr).
- [Bibliography](references/bibliography.yaml)
	- Source citations with stable reference IDs.

## Libraries (evidence + templates)

- [Evidence Patterns](evidence/README.md)
	- Reusable observation archetypes (15 patterns covering all frames).
- [Templates library](templates/README.md)
	- How templates are organized and used.

## Board Configuration

- [Board Configuration Schema](schemas/board_config.schema.json)
	- JSON Schema for board-specific settings.
- [NCDSB Configuration](config/boards/ncdsb.yaml)
	- Northeast Catholic District School Board preset.
- [TCDSB Configuration](config/boards/tcdsb.yaml)
	- Toronto Catholic District School Board preset.
- [Comment templates (YAML)](templates/comment_templates.yaml)
	- Initial canonical template set (36 templates, non-PII).
- [Assembly Library](lib/assembly.py)
	- Slot filling functions for rendering templates with child data.
- [Readability Library](lib/readability.py)
	- Text analysis using textstat for readability scoring.

## AI Agent System

- [Generation Agent](lib/agents/generation.py)
	- AI-assisted template generation with example retrieval.
- [Validation Agent](lib/agents/validation.py)
	- Quality assurance with schema, privacy, and readability checks.
- [Comment Assembly Pipeline](lib/pipeline/assemble.py)
	- Complete comment assembly following guidance/comment-assembly.md rules.

## Agent Prompts

- [System Prompt: Generation](prompts/system_generation.yaml)
	- Template generation system prompt for AI agents.
- [System Prompt: Validation](prompts/system_validation.yaml)
	- Template validation system prompt for quality assurance.
- [System Prompt: Simplification](prompts/system_simplification.yaml)
	- Template simplification prompt for readability improvement.
- [System Prompt: Installation](prompts/system_installation.yaml)
	- Setup assistant with checks, balances, and standards gates.

## How-to (processes)

- [Reporting Process SOP](knowledge/processes/process.reporting.workflow.md)
	- Standard workflow for the reporting cycle.
- [Content Review Process](knowledge/processes/process.content.review.md)
	- Quality checklist for new content.
- [Contributor Onboarding](knowledge/processes/process.onboarding.contributor.md)
	- Setup guide for new contributors.

## Datasets (planned/derived)

- [Traceability Matrix](datasets/traceability/README.md)
	- Coverage and audit datasets (generated + planned extensions).

## Reports (auto-generated)

- [Coverage Report](reports/coverage.md)
	- Template distribution across frames, indicators, and sections.
- [Gaps Report](reports/gaps.md)
	- Identifies indicators with <2 templates, sections with <3 templates.

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
- [Comment assembly rules](guidance/comment-assembly.md)
	- Character limits, section requirements, readability targets.
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
- [Implementation Gameplan](docs/GAMEPLAN.md)
	- Phased development plan with tasks, deliverables, and success metrics.
- [Frontend Gameplan](docs/frontend.md)
	- Tauri/React UI plan (phases, deliverables, and UX layout).
- [Changelog](docs/CHANGELOG.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Release and versioning](docs/RELEASE.md)

## Audits

- [Audits](audits/README.md)
	- Periodic repository audits and snapshots.

## Architecture Decision Records (ADRs)

### Legacy ADRs (decisions/ folder)

- [ADR 0000: Template](decisions/0000-adr-template.md)
- [ADR 0001: Canonical vs Sources](decisions/0001-canonical-vs-sources.md)
- [ADR 0002: Framework vs Infrastructure Split](decisions/0002-framework-vs-infrastructure-split.md)
- [ADR 0003: Template Library Format](decisions/0003-template-library-format.md)
- [ADR 0004: Placeholder Convention](decisions/0004-placeholder-convention.md)
- [ADR 0005: ID Naming Convention](decisions/0005-id-naming-convention.md)

### New ADRs (docs/adr/ folder)

- [ADR-001: Evidence-Template Linking](docs/adr/ADR-001-evidence-template-linking.md)
	- Decision to use heuristic matching over explicit linking.
- [ADR-002: Template Deprecation Workflow](docs/adr/ADR-002-template-deprecation.md)
	- Lifecycle states and replaces/deprecated_by fields.

## CLI Tools

- **Quick Shortcuts** ⚡
	- `.\check` — run all validation checks
	- `.\check --quick` — fast checks only (recommended during development)
- **Master Check** (`scripts/check_all.py`) ⭐
	- `python scripts/check_all.py` — run ALL validation checks
	- `python scripts/check_all.py --quick` — fast checks only
- **Edsembli CLI** (`scripts/edsembli_cli.py`)
	- `edsembli search <query>` — fuzzy template search
	- `edsembli matrix-sql <sql>` — DuckDB queries over traceability matrix
	- `edsembli evidence-matrix [--template ID]` — show heuristic evidence-template matches
	- `edsembli templates [--show-deprecated]` — list templates with deprecation status
	- `edsembli review <template_file>` — validate template draft with quality checks
	- `edsembli export [--format csv|json] [--board <id>]` — export template bank for SIS import
	- `edsembli export-comment --child-file <json> [--board <id>]` — export assembled student comment
- **Index Checker** (`scripts/check_index.py`)
	- Verifies all canonical files are linked in `index.md`

## Configuration Files

- `mkdocs.yml` — Documentation site configuration
- `pyrightconfig.json` — Type checking settings
- `.pre-commit-config.yaml` — Git hooks (ruff, pytest, secrets)
- `pyproject.toml` — Linter and test settings
- `requirements.in` — Source dependency list (compile with pip-tools)
