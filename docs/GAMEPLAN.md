---
id: doc.gameplan
type: document
title: Implementation Gameplan – Ontario Catholic Kindergarten CoL Framework
version: 0.1.0
status: draft
tags: [gameplan, implementation, roadmap]
refs:
  - doc.framework
  - doc.infrastructure
  - doc.roadmap
  - doc.requirements
updated: 2026-01-12
---

# Implementation Gameplan

> This document translates the design artifacts (framework, infrastructure, roadmap) into concrete development phases with tasks, acceptance criteria, and technology choices.

## Executive Summary

The framework design is **complete** through Phase 3. What remains is:

1. **Phase 3B**: Enhance traceability tooling (coverage reports, gap analysis)
2. **Phase 4**: Agent integration (template generation, validation feedback)
3. **Phase 5**: SIS integration patterns (export formats, board configuration)

This gameplan breaks each phase into **2-week sprints** with specific deliverables.

---

## Current State Assessment

### ✅ Completed

| Component | Status | Evidence |
|-----------|--------|----------|
| Repository structure | Complete | All canonical folders exist |
| Governance docs | Complete | PRIVACY, CONTRIBUTING, CHANGELOG |
| Taxonomy (frames, indicators, sections, tags, roles) | Complete | 4 frames, 13 indicators, 3 sections |
| Templates library | Complete | 36 templates (12/frame × 3/section) |
| Evidence patterns | Complete | 15 patterns with frame/indicator links |
| Bibliography | Complete | 14 canonical references |
| Schemas | Complete | 10 JSON Schema definitions |
| Validation scripts | Complete | validate.py, lint.py, coverage.py |
| Traceability matrix | Complete | matrix.parquet + matrix.csv |
| Pre-commit hooks | Complete | Ruff, pytest, pyright, secrets |
| CI pipeline | Complete | GitHub Actions |
| Slot guidance | Complete | slot_guidance.yaml with types, validation rules |
| Assembly rules | Complete | guidance/comment-assembly.md |
| ADRs | Complete | ADR-001 (evidence linking), ADR-002 (deprecation) |

### 🔄 Partially Complete

| Component | Status | Gap |
|-----------|--------|-----|
| Bilingual support | Schema ready | No French translations in templates yet |
| Readability checks | Lint integrated | Not blocking CI (warnings only) |
| Coverage reports | Matrix exists | No auto-generated gap report |
| DuckDB CLI | Working | Limited to SQL queries only |

### ❌ Not Started

| Component | Notes |
|-----------|-------|
| Agent prompts | Phase 4 |
| Template generation pipeline | Phase 4 |
| Validation agent | Phase 4 |
| Export formats (SIS) | Phase 5 |
| Board configuration patterns | Phase 5 |
| Next.js UI | Optional, deprioritized |

---

## Technology Stack (Finalized)

### Core (Keep)

| Tool | Purpose | Status |
|------|---------|--------|
| **Python 3.14** | Runtime | In use |
| **Pydantic** | Schema validation, typed models | In use (expand) |
| **DuckDB** | Local analytics over parquet | In use |
| **Typer + Rich** | CLI interface | In use |
| **MkDocs Material** | Documentation site | In use |
| **pytest** | Testing | In use (16 tests) |
| **Ruff** | Lint + format | In use |
| **pyright** | Type checking | In use |

### Add

| Tool | Purpose | Phase |
|------|---------|-------|
| **textstat** | Readability scoring | Now (added to requirements.in) |
| **Jinja2** | Template rendering with slots | Phase 4 |

### Remove / Defer

| Tool | Reason |
|------|--------|
| frictionless | Unused; DuckDB covers dataset validation |
| networkx | Unused; matrix covers traceability |
| sqlalchemy | Unused; DuckDB sufficient |
| Vector stores | Defer to Phase 4 if needed |
| LangGraph | Defer to Phase 4; plain Python first |

---

## Phase 3B: Traceability Enhancement (2 weeks)

**Goal:** Complete the traceability story with automated reports and gap analysis.

### Sprint 3B.1 (Week 1)

#### Tasks

1. **[TASK-3B1-1] Coverage report generator**
   - Create `scripts/generate_coverage_report.py`
   - Outputs: `reports/coverage.md`
   - Shows: templates per frame, templates per indicator, overall %
   - Acceptance: Report renders in MkDocs

2. **[TASK-3B1-2] Gap analysis report**
   - Create `scripts/generate_gaps_report.py`
   - Outputs: `reports/gaps.md`
   - Shows: indicators without templates, frames with <3 templates/section
   - Acceptance: CI fails if critical gaps exist

3. **[TASK-3B1-3] Add bilingual placeholder templates**
   - Add `text_fr: "TODO"` to all 36 templates
   - Lint will warn (not fail) until translations done
   - Acceptance: Schema validates, lint warns

#### Deliverables

- [x] `scripts/generate_coverage_report.py`
- [x] `scripts/generate_gaps_report.py`
- [x] `reports/coverage.md` (auto-generated)
- [x] `reports/gaps.md` (auto-generated)
- [x] Updated `templates/comment_templates.yaml` with `text_fr` stubs

### Sprint 3B.2 (Week 2)

#### Tasks

1. **[TASK-3B2-1] Evidence-template matrix CLI**
   - Add `edsembli evidence-matrix` command
   - Shows heuristic matches with relevance scores
   - Uses algorithm from ADR-001

2. **[TASK-3B2-2] Template deprecation CLI**
   - Add `edsembli templates --show-deprecated`
   - Lists deprecated templates with their replacements

3. **[TASK-3B2-3] Integrate reports into MkDocs**
   - Add `reports/` to nav
   - Configure macros plugin to embed coverage stats

#### Deliverables

- [x] `edsembli evidence-matrix` command
- [x] `edsembli templates --show-deprecated` command
- [x] MkDocs nav updated with reports section

---

## Phase 4: Agent Integration (4 weeks)

**Goal:** Enable AI-assisted template generation with human-in-the-loop validation.

### Sprint 4.1 (Week 1-2): Foundation

#### Tasks

1. **[TASK-4-1-1] Prompt templates library**
   - Create `prompts/` directory
   - System prompts for: generation, validation, simplification
   - Store as YAML with metadata (model, temp, tokens)

2. **[TASK-4-1-2] Slot fill function**
   - `lib/assembly.py`: `fill_slots(template, child_data) -> str`
   - Uses Jinja2 for rendering
   - Validates against slot_guidance.yaml rules
   - Returns filled text or validation errors

3. **[TASK-4-1-3] Readability gate function**
   - `lib/readability.py`: `check_readability(text) -> ReadabilityResult`
   - Uses textstat
   - Returns scores + pass/fail + suggestions

#### Deliverables

- [x] `prompts/system_generation.yaml`
- [x] `prompts/system_validation.yaml`
- [x] `prompts/system_simplification.yaml`
- [x] `lib/assembly.py`
- [x] `lib/readability.py`
- [x] Tests for assembly + readability

### Sprint 4.2 (Week 3-4): Agent Pipeline

#### Tasks

1. **[TASK-4-2-1] Template generation agent**
   - Input: frame, indicator, section, evidence pattern ID
   - Output: draft template matching schema
   - Flow: retrieve examples → generate → validate → return

2. **[TASK-4-2-2] Validation feedback agent**
   - Input: draft template YAML
   - Output: validation report (schema, lint, readability, indicator alignment)
   - Suggest fixes for common issues

3. **[TASK-4-2-3] Comment assembly pipeline**
   - Input: child_data (slots), selected template IDs
   - Output: assembled comment or error list
   - Follows rules from `guidance/comment-assembly.md`

4. **[TASK-4-2-4] Human review CLI**
   - `edsembli review <draft.yaml>`
   - Shows diff against similar existing templates
   - Prompts for approve/reject/edit

#### Deliverables

- [ ] `lib/agents/generation.py`
- [ ] `lib/agents/validation.py`
- [ ] `lib/pipeline/assemble.py`
- [ ] `edsembli review` command
- [ ] Integration tests with mock LLM responses

---

## Phase 5: SIS Integration Patterns (3 weeks)

**Goal:** Document and implement export formats compatible with Edsembli and other SIS.

### Sprint 5.1 (Week 1-2): Export Formats

#### Tasks

1. **[TASK-5-1-1] Research SIS import capabilities**
   - Document Edsembli CSV/XML import formats
   - Identify field mappings (template → SIS field)
   - Add to `docs/integration/sis-formats.md`

2. **[TASK-5-1-2] Comment bank export**
   - `edsembli export --format csv --output bank.csv`
   - Columns: id, frame, section, tone, text, text_fr
   - Compatible with SIS bulk import

3. **[TASK-5-1-3] Assembled comment export**
   - `edsembli export-comment --child-file data.json --output comment.txt`
   - Fills slots and exports final comment

#### Deliverables

- [ ] `docs/integration/sis-formats.md`
- [ ] `edsembli export` command
- [ ] `edsembli export-comment` command
- [ ] Sample CSV exports in `examples/exports/`

### Sprint 5.2 (Week 3): Board Configuration

#### Tasks

1. **[TASK-5-2-1] Board config schema**
   - Create `schemas/board_config.schema.json`
   - Fields: char_limits, locale, required_sections, custom_slots

2. **[TASK-5-2-2] Board presets**
   - Create `config/boards/` directory
   - Add NCDSB, TCDSB presets (example)
   - Export command respects board limits

3. **[TASK-5-2-3] Update guidance docs**
   - Expand `guidance/board-customization.md`
   - Link to board presets

#### Deliverables

- [ ] `schemas/board_config.schema.json`
- [ ] `config/boards/ncdsb.yaml`
- [ ] `config/boards/tcdsb.yaml`
- [ ] Updated `guidance/board-customization.md`

---

## Phase 6: French Translations (Ongoing)

**Goal:** Complete bilingual support for all templates.

### Approach

1. **Translator workflow:**
   - Export English templates: `edsembli export --format translation-csv`
   - Translator fills `text_fr` column
   - Import: `edsembli import-translations translations.csv`

2. **Validation:**
   - Lint enforces `text_fr` presence on `status: stable`
   - Schema validates slot consistency between `text` and `text_fr`

3. **Phased rollout:**
   - Phase 6A: `key_learning` templates (12 templates)
   - Phase 6B: `growth` templates (12 templates)
   - Phase 6C: `next_steps` templates (12 templates)

### Deliverables

- [ ] `edsembli export --format translation-csv`
- [ ] `edsembli import-translations`
- [ ] All 36 templates with verified `text_fr`

---

## Testing Strategy

### Unit Tests (Current: 16, Target: 50+)

| Area | Current | Target | Notes |
|------|---------|--------|-------|
| Schema validation | 4 | 10 | Add edge cases |
| Lint rules | 3 | 8 | Deprecation, bilingual, readability |
| Matrix generation | 2 | 5 | Coverage edge cases |
| Assembly | 0 | 10 | Slot fill, pronoun agreement |
| Readability | 0 | 5 | Score boundaries |
| CLI commands | 7 | 12 | New commands |

### Integration Tests

- [ ] End-to-end: evidence → template → assembly → export
- [ ] Agent pipeline with mock LLM
- [ ] Board config + export compatibility

### Regression Tests

- [ ] Golden outputs for matrix generation
- [ ] Golden outputs for report generation
- [ ] Template count assertions (36 minimum)

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM output quality varies | High | Validation agent + human review gate |
| French translations delayed | Medium | English-only export path available |
| SIS format changes | Medium | Abstract export layer, document versions |
| Template sprawl | Medium | Deprecation workflow enforced |
| Readability thresholds too strict | Low | Configure per-board in board_config |

---

## Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| Template coverage | 100% frames | 100% indicators | Phase 3B |
| Test coverage | ~60% | 80% | Phase 4 |
| French templates | 0% | 100% | Phase 6 |
| Agent generation accuracy | N/A | 80% accepted after review | Phase 4 |
| Export compatibility | 0 boards | 2 boards | Phase 5 |

---

## Appendix: File Creation Summary

### New files to create

```
prompts/
  system_generation.yaml
  system_validation.yaml
  system_simplification.yaml

lib/
  assembly.py
  readability.py
  agents/
    __init__.py
    generation.py
    validation.py
  pipeline/
    __init__.py
    assemble.py

reports/
  coverage.md (generated)
  gaps.md (generated)

docs/integration/
  sis-formats.md

config/boards/
  ncdsb.yaml
  tcdsb.yaml

schemas/
  board_config.schema.json
```

### Modified files

```
scripts/
  edsembli_cli.py (add new commands)
  generate_coverage_report.py (new)
  generate_gaps_report.py (new)

templates/
  comment_templates.yaml (add text_fr stubs)

guidance/
  board-customization.md (expand)

mkdocs.yml (add reports to nav)
```

---

## Next Action

Start **Phase 3B Sprint 1** by creating the coverage report generator:

```bash
# Create the coverage report generator
python scripts/generate_coverage_report.py

# View the generated report
mkdocs serve
# Navigate to Reports > Coverage
```

---

*Document generated: 2026-01-12*
*Based on: framework.md, infrastructure.md, ROADMAP.md, requirements.md*
