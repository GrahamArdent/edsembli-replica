---
id: doc.discussion
type: document
title: Discussion / Working Notes
version: 0.1.0
status: draft
tags: [discussion, notes]
refs: []
updated: 2026-01-11
---

# Discussion / Working Notes

> Purpose: Keep design-review findings, decisions, and rationale in one place.
> This file is a living reference for future refactors.
>
> Last updated: 2026-01-11

## 1) Snapshot: What we have so far

This repository is a design-first framework for Ontario Kindergarten Communication of Learning (CoL) narrative comments.

Core artifacts:
- `index.md` — canonical navigation
- `framework.md` — short narrative (what/why)
- `infrastructure.md` — specification/contract (how)
- `glossary.md` — controlled vocabulary
- `requirements.md` — functional requirements for tooling/workflow
- `taxonomy/frames.yaml` — canonical frame taxonomy with representative indicators
- `references/bibliography.yaml` — canonical reference records
- `examples/` — sample evidence patterns and comment template shapes

## 2) Review findings (gaps and inconsistencies)

### 2.1 ID consistency drift

Observed mismatches that reduce auditability and complicate validation:
- `frame.self_regulation` vs `frame.selfregulation` (underscore vs none)
- Requirement IDs in the spec examples used a non-numbered style, while `requirements.md` uses numbered IDs.

### 2.2 Evidence Pattern vs Template naming mismatch

- The specification described evidence patterns as `evidence.pattern.*`.
- The sample evidence pattern used an ID prefix `template.evidence.*`.

This matters because later validation and traceability depend on predictable prefixes and folder placement.

### 2.3 Template schema field mismatch

- The comment template sample used `col_section` in front matter.
- The specification described a `section` field and also introduced fields like `tone`, `slots`, and template constraints.

### 2.4 Placeholder style inconsistency vs privacy requirement

- `requirements.md` explicitly requires slot-style placeholders such as `{name}`.
- Examples used bracket placeholders like `[Child's name]` and `[STUDENT]`.

Slot-style placeholders reduce accidental copy/paste of names and enable consistent generation/validation.

### 2.5 Canonical front matter consistency

The spec recommends YAML front matter for canonical Markdown, but several canonical docs did not yet include it.

## 3) Convention decisions (standardized choices)

These choices are made to reduce ambiguity and enable validation later.

### 3.1 Frame IDs

- Canonical frame IDs use underscores for multi-word names.
- Decision: `frame.self_regulation` is canonical.

### 3.2 Requirement IDs

- Decision: requirements use numbered IDs: `req.<category>.<number>` (example: `req.privacy.1`).
- Rationale: stable ordering, easy referencing, low friction.

### 3.3 Evidence pattern IDs

- Decision: evidence patterns use `evidence.pattern.*` IDs.
- Rationale: evidence patterns are a first-class artifact type distinct from comment templates.

### 3.4 Comment template fields

- Decision: use `section` (not `col_section`) with allowed values:
  - `key_learning`
  - `growth`
  - `next_steps`

### 3.5 Placeholder format

- Decision: use slot placeholders in curly braces everywhere (examples):
  - `{child}`
  - `{pronoun_subject}` / `{pronoun_possessive}`
  - `{evidence}`
  - `{strength}`
  - `{next_step}`

## 4) Recommended structural refinements

### 4.1 Treat infrastructure as the contract

Restructure `infrastructure.md` so it clearly separates:
1) Normative rules (MUST/SHOULD/MAY)
2) Schema/field definitions
3) Tooling/workflows (advisory)

### 4.2 Clarify canonical vs illustrative

`examples/` should be explicitly labeled as either:
- illustrative only (non-canonical), or
- seed canonical content that will migrate into `evidence/` and `templates/`.

Current stance: examples are illustrative shapes and should not be treated as a complete canonical library.

## 5) Suggested next files (when ready)

Not required immediately, but useful next steps:
- `PRIVACY.md` — operational checklist for no-PII reviews
- `guidance/comment-style.md` — tone/voice constraints (parent-friendly, strength-based, length limits, banned phrases)
- `taxonomy/indicators.yaml` — expanded indicator set (separate from frames)
- `taxonomy/col-sections.yaml` — canonical definition of CoL sections
- `knowledge/entities/` seed entities (Edsembli, ONSIS, key policy docs)

Additional gap closures completed (2026-01-11):
- Initial comment template library in `templates/comment_templates.yaml` (see ADR 0003)
- JSON Schemas in `schemas/` and local checks in `scripts/` (`validate.py`, `lint.py`)

## 6) Consistency audit (2026-01-11)

Goal: verify that the canonical artifacts reflect the standardized conventions in section 3.

### Checks performed

Searched the repository for the following known drift markers:
- `frame.selfregulation`
- `col_section`
- `template.evidence.`
- bracket placeholders like `[Child's name]` / `[STUDENT]`
- `req.privacy.no_pii`
- bracket pronoun/verb placeholders like `[he/she/they]` / `[is/are]`

Also confirmed presence of the canonical forms:
- `frame.self_regulation`
- `evidence.pattern.`

### Results

- No drift markers remain in canonical artifacts.
- Matches for the drift markers above appear only in this file as historical notes in section 2.
- Canonical forms are present in:
  - `taxonomy/frames.yaml` (frames and indicators)
  - `infrastructure.md` (ID examples)
  - `glossary.md` (frame ID table)
  - `examples/` (updated sample IDs and slot placeholders)

---

## 7) Second Review (2026-01-11)

### 7.1 New artifacts created

Closed previously identified gaps:

| Artifact | Purpose |
|----------|---------|
| `taxonomy/tags.yaml` | Controlled vocabulary for categorization |
| `taxonomy/roles.yaml` | Stakeholder role definitions |
| `decisions/0004-placeholder-convention.md` | ADR for `{slot}` placeholder style |
| `decisions/0005-id-naming-convention.md` | ADR for `type.domain.name` pattern |
| `schemas/tags.schema.json` | JSON Schema for tags taxonomy |
| `schemas/roles.schema.json` | JSON Schema for roles taxonomy |
| `scripts/coverage.py` | Indicator-to-template coverage reporter |

### 7.2 Existing files updated

| File | Change |
|------|--------|
| `CONTRIBUTING.md` | Added version policy section, listed ADRs |
| `schemas/README.md` | Documented new schemas, listed planned schema |
| `scripts/README.md` | Added coverage.py documentation |
| `scripts/validate.py` | Added tags.yaml, roles.yaml, scripts/README.md to validation |
| `scripts/lint.py` | Added slot↔text consistency checking |
| `index.md` | Added links to tags.yaml and roles.yaml |

### 7.3 Remaining gaps (tracked for future phases)

| Gap | Priority | Notes |
|-----|----------|-------|
| Pre-commit hooks | High | Phase 2 roadmap item |
| CI pipeline | High | Phase 2 roadmap item |
| `knowledge/processes/` | Medium | Workflow/SOP templates |
| Traceability matrix | Medium | Phase 3 roadmap item |
| `references/links.md` | Low | Human-readable link list (can be generated) |
| Evidence patterns schema | Low | Deferred until evidence patterns created |

### 7.4 Drift prevention status

Current protections in place:
- ✅ JSON Schema validation (9 schemas)
- ✅ Reference ID lint check
- ✅ Indicator ID lint check
- ✅ Placeholder style lint check
- ✅ Slot↔text consistency lint check
- ✅ YAML front matter enforcement
- ✅ ID naming pattern regex in schemas
- ✅ Formal ADRs for key conventions (0004, 0005)

Remaining to implement:
- ⏳ Pre-commit hooks
- ⏳ CI/CD pipeline
- ⏳ Automated coverage tracking in CI
- ⏳ Changelog enforcement

---

## 8) Third Review (2026-01-11)

### 8.1 Automated Enforcement Designed

To alleviate drift, we designed the automation config (pending activation):
- `.pre-commit-config.yaml` created:
  - Runs trailing-whitespace fixer
  - Runs `validate.py`, `lint.py`, `coverage.py` locally on commit
- `.github/workflows/ci.yml` created:
  - Runs strict validation on every Push/PR
  - Installs clean environment

### 8.2 Content Gaps Closed

Created missing content artifacts based on framework spec:
- `knowledge/processes/process.reporting.workflow.md`: SOP for reporting cycle.
- `evidence/evidence.pattern.block_play.md`: First canonical evidence pattern (canonicalized from sample).
- `references/links.md`: Human-readable link list derived from bibliography.

### 8.3 Schema Enhancements

- Updated `schemas/document.frontmatter.schema.json` to support `process` and `evidence_pattern` types.
- Updated `scripts/validate.py` to scan `evidence/` and `knowledge/processes/`.

### 8.4 Validation Status

- `validate.py`: PASS (including new files)
- `lint.py`: PASS
- `coverage.py`: PASS (100%)

### 8.5 Recommendations

1. **Activate Automation**: The config files exist. Next step is `pip install pre-commit && pre-commit install`.
2. **Expand Evidence**: Use the Block Play pattern as a template for 10-15 more patterns.
3. **Strict Mode**: Consider making coverage check fail build if <100%.

---

## 9) Final Implementation (2026-01-11)

All recommendations from Section 8 have been implemented.

### 9.1 Evidence Patterns Created (15 total)

| Pattern | Frame | Context |
|---------|-------|---------|
| `block_play` | Belonging | Cooperative building |
| `dramatic_play` | Belonging | Role-playing scenarios |
| `music_movement` | Belonging | Songs and dance |
| `snack_time` | Self-Regulation | Daily routine |
| `circle_time` | Self-Regulation | Group gathering |
| `outdoor_play` | Self-Regulation | Gross motor play |
| `conflict_resolution` | Self-Regulation | Peer disagreements |
| `transition_time` | Self-Regulation | Activity changes |
| `read_aloud` | Literacy/Math | Interactive reading |
| `writing_centre` | Literacy/Math | Mark-making |
| `math_manipulatives` | Literacy/Math | Counters, patterns |
| `art_creation` | Problem Solving | Open-ended art |
| `inquiry_investigation` | Problem Solving | Science exploration |
| `construction_building` | Problem Solving | LEGO, loose parts |
| `sand_water` | Problem Solving | Sensory exploration |

### 9.2 Processes Created (3 total)

- `process.reporting.workflow.md` - Reporting cycle SOP
- `process.content.review.md` - Quality review checklist
- `process.onboarding.contributor.md` - New contributor setup

### 9.3 Schemas & Scripts

- `evidence_patterns.schema.json` created
- All 10 schemas now have `$version` field
- `coverage.py` now supports `--strict` flag
- `generate_links.py` created for auto-generating links.md

### 9.4 GitHub Integration

- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/template_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- Pre-commit changelog check added

### 9.5 Documentation

- `guidance/board-customization.md` - Board adaptation guide
- `datasets/traceability/README.md` - Traceability folder structure
- Updated `index.md` with all new content
- Updated `evidence/README.md` with pattern inventory

### 9.6 Final Validation Status

- `validate.py`: ✅ PASS
- `lint.py`: ✅ PASS
- `coverage.py`: ✅ PASS (100%)
- All schemas versioned: ✅
- GitHub templates: ✅
- Pre-commit configured: ✅

```

---

## 10) Deep Dive and Production Hardening (2026-01-11)

### 10.1 Critical Gaps Identified

**Safety Gap: PII Detection**
- **Issue**: Strict No-PII policy existed but had no automated enforcement
- **Risk**: Contributors could accidentally commit OEN numbers, phone numbers, or emails
- **Solution**: Implemented `check_pii_safety()` in validate.py with regex patterns for:
  - Ontario Education Numbers (9 digits)
  - Phone numbers (various formats)
  - Email addresses

**Localization Gap: English-Only Schema**
- **Issue**: Ontario requires bilingual (French) support but schemas only supported English
- **Risk**: Retrofitting localization later would be painful
- **Solution**: Updated schemas to support `_fr` suffix fields:
  - `text_fr` in comment templates
  - `name_fr`, `description_fr` in frames, indicators, tags

**Discovery Gap: No User Interface**
- **Issue**: Framework only accessible through raw YAML/MD files
- **Risk**: Teachers cannot easily browse or search templates
- **Solution**: Implemented MkDocs with Material theme for searchable documentation site

**Test Coverage Gap: Minimal Testing**
- **Issue**: Only 3 unit tests existed (regex patterns only)
- **Risk**: No regression protection for refactoring validate.py, lint.py, or coverage.py
- **Solution**: Expanded to 16 tests covering:
  - PII detection (5 tests)
  - Validation behavior (4 tests)
  - Lint and coverage functionality (4 tests)
  - Regex patterns (3 tests)

**CI/CD Gap: Incomplete Pipeline**
- **Issue**: GitHub Actions only ran validation scripts, not code quality checks
- **Risk**: Code style drift, untested code merging to main
- **Solution**: Enhanced CI pipeline to run:
  - Ruff linting and formatting
  - Pytest test suite
  - MkDocs documentation build
  - All validation scripts

**Slot Guidance Gap: No Controlled Vocabulary**
- **Issue**: Templates use placeholders like `{evidence}`, `{strength}` with no guidance
- **Risk**: Inconsistent slot usage, unclear expectations for teachers
- **Solution**: Created `taxonomy/slot_guidance.yaml` with:
  - 12 slot type definitions
  - Examples and validation rules
  - Guidance for evidence quality, goal specificity

### 10.2 Tooling Recommendations Research

**Evaluated Tools:**
- **Ruff** (adopted): Replaced need for flake8, isort, black - 10x faster
- **Typer** (installed): Future CLI tool building (planned)
- **MkDocs Material** (adopted): Professional documentation site
- **Pytest** (expanded): Test framework with 16 tests now passing
- **Rich** (installed): Future CLI output enhancement

**Deferred Tools:**
- **DuckDB** (in requirements, not yet used): Future query interface over YAML/Parquet
- **SQLAlchemy** (in requirements, not yet used): Future relational layer

### 10.3 Files Created

**Testing Infrastructure:**
- `tests/test_lint.py` - Lint functionality tests
- `tests/test_coverage.py` - Coverage reporting tests
- `tests/test_pii_safety.py` - PII detection tests (5 tests)
- `tests/test_validation_behavior.py` - Validation logic tests (4 tests)

**Documentation Infrastructure:**
- `mkdocs.yml` - MkDocs configuration with Material theme
- `scripts/stage_docs.py` - Documentation staging script
- `site_docs/` - Temporary staging directory (gitignored)

**Taxonomy Expansion:**
- `taxonomy/slot_guidance.yaml` - Controlled vocabulary for template placeholders

**Configuration:**
- `pyproject.toml` - Ruff and Pytest configuration
- Updated `.github/workflows/ci.yml` - Enhanced CI pipeline
- Updated `.gitignore` - Added site/, .pytest_cache/, .ruff_cache/

**Audit Reports:**
- `audits/audit.2026-01-11.post-optimization.md` - Post-implementation audit

### 10.4 Schema Enhancements

Updated 5 schemas for localization support:
- `comment_templates.schema.json`: Added `text_fr` field
- `frames.schema.json`: Added `name_fr`, `description_fr` fields
- `indicators.schema.json`: Added `name_fr`, `description_fr` fields
- `tags.schema.json`: Added `name_fr`, `description_fr` fields
- `document.frontmatter.schema.json`: Added `audit` type support

### 10.5 Quality Metrics (Post-Implementation)

| Metric | Before | After |
|--------|--------|-------|
| Tests | 3 | 16 |
| Test Coverage | Regex only | Full behavior |
| CI Steps | 3 | 8 |
| Localization | ❌ | ✅ Ready |
| PII Detection | ❌ Manual only | ✅ Automated |
| Documentation Site | ❌ | ✅ MkDocs |
| Code Linting | ❌ Manual | ✅ Automated |
| Slot Guidance | ❌ | ✅ 12 slots defined |

### 10.6 Remaining Recommendations

**Query Interface (Medium Priority)**
- Use DuckDB to enable SQL queries over templates
- Example: "Show all templates for frame.belonging in key_learning section"
- CLI tool: `edsembli search --frame belonging --section key_learning`

**Evidence→Template Linkage (Medium Priority)**
- Add `evidence_patterns` field to comment template schema
- Enable "which templates go with which evidence patterns" queries

**French Content Population (Low Priority)**
- Begin translating content to populate `*_fr` fields
- Coordinate with French Immersion educators

### 10.7 Discussion File Automation

**Current Approach:** Manual updates after significant work sessions

**Automation Challenges:**
- AI conversation transcripts not directly accessible for auto-append
- Would require external tooling to capture conversation context
- Risk of noise vs. signal (verbatim chat vs. design decisions)

**Recommended Hybrid Approach:**
1. **Manual Documentation** (current): After each session, append key decisions/changes
2. **Git Commit Messages**: Use detailed commit messages as partial log
3. **ADRs for Major Decisions**: Continue using ADRs in `decisions/` folder
4. **Audit Reports**: Use `audits/` folder for milestone reviews

**Potential Future Automation:**
- Pre-commit hook that prompts: "Update discussion.md? (y/n)"
- Template in `.github/` for session notes
- Git alias: `git discuss` that opens discussion.md in editor

**Decision:** Keep discussion.md as a curated design journal, not verbatim transcript. Update manually after each session with key outcomes. This session (Section 10) now documented.
