---
id: doc.roadmap
type: document
title: Roadmap
version: 0.1.0
status: draft
tags: [roadmap]
refs: []
updated: 2026-01-11
---

# Roadmap

> Phased development plan for the Ontario Catholic Kindergarten CoL Framework

## Overview

This roadmap outlines the incremental development of the framework from
initial scaffolding through to agent-assisted tooling. Each phase builds
on the previous, ensuring a stable foundation before adding complexity.

---

## Phase 0: Scaffolding ✅

**Status:** Complete
**Goal:** Establish repository structure and governance documentation

### Deliverables

- [x] Repository structure with canonical folders
- [x] `index.md` - Landing page and navigation
- [x] `docs/framework.md` - Narrative design document
- [x] `docs/infrastructure.md` - Technical specification
- [x] `docs/glossary.md` - Canonical term definitions
- [x] `docs/requirements.md` - Functional requirements
- [x] `README.md` - Project overview
- [x] `docs/CONTRIBUTING.md` - Contribution guidelines
- [x] `docs/CHANGELOG.md` - Version history
- [x] `decisions/` - ADR structure with initial decisions
- [x] `sources/` - Research documentation preserved
- [x] `requirements.txt` - Python dependencies
- [x] `.gitignore` - Standard exclusions
- [x] `docs/PRIVACY.md` - No-PII operational checklist
- [x] `guidance/comment-style.md` - Comment style constraints

### Acceptance Criteria

- All governance documents in place
- ID naming convention documented
- Four frames defined with canonical IDs
- No PII in repository (verified)

---

## Phase 1: Content Population ✅

**Status:** Complete
**Goal:** Populate canonical content artifacts

### Deliverables

- [x] `taxonomy/frames.yaml` - Frame definitions with indicators
- [x] `references/bibliography.yaml` - Source citations
- [x] `examples/` - Sample patterns (evidence, comment template)
- [x] `taxonomy/indicators.yaml` - Expanded indicator definitions
- [x] `taxonomy/col-sections.yaml` - Key Learning / Growth / Next Steps
- [x] `taxonomy/tags.yaml` - Controlled vocabulary tags
- [x] `taxonomy/roles.yaml` - Stakeholder role definitions
- [x] `templates/` - Initial comment template library (36 templates)

### Acceptance Criteria

- All four frames have indicator definitions ✅
- At least 3 comment templates per frame per section (36 minimum) ✅
- All templates trace to specific indicators ✅
- Bibliography includes all cited sources ✅

---

## Phase 2: Validation Tooling ✅

**Status:** Complete
**Goal:** Implement validation scripts and schema enforcement

### Deliverables

- [x] `schemas/` - JSON Schema definitions (10 schemas)
- [x] `scripts/validate.py` - Schema/front matter validation runner
- [x] `scripts/lint.py` - Content linting (refs, indicators, placeholders, slot consistency)
- [x] `scripts/coverage.py` - Indicator-to-template coverage analysis
- [x] `scripts/generate_links.py` - Derived links generation
- [x] ADR 0004 - Placeholder convention documented
- [x] ADR 0005 - ID naming convention documented
- [x] Pre-commit hooks configured
- [x] CI pipeline (GitHub Actions)

### Acceptance Criteria

- All YAML files validate against schemas ✅
- ID naming convention enforced automatically ✅
- Broken reference detection ✅
- Slot↔text consistency checking ✅
- Pre-commit prevents invalid commits ✅
- CI runs validation on PRs ✅

---

## Phase 3: Traceability Matrix 🔗 ✅

**Status:** Complete
**Goal:** Build and visualize curriculum coverage

### Deliverables

- [x] `scripts/generate_matrix.py` - Matrix generation
- [x] `datasets/traceability/matrix.csv` - Human-readable export
- [x] `datasets/traceability/matrix.parquet` - Analytics-friendly export

- [ ] `scripts/build_matrix.py` - Matrix generator
- [ ] `reports/coverage.md` - Auto-generated coverage report
- [ ] `reports/gaps.md` - Uncovered indicators report
- [ ] Visualization tooling (networkx diagrams)

### Acceptance Criteria

- Matrix shows template-to-indicator mapping
- Coverage percentage calculated per frame
- Gap report identifies missing coverage
- Visualization renders frame relationships

### Tasks

1. Design matrix data structure
2. Implement matrix builder from taxonomy + templates
3. Generate Markdown coverage report
4. Implement gap analysis
5. Add networkx visualization
6. Integrate into CI for automatic updates

---

## Phase 4: Agent Integration 🤖

**Status:** Future
**Goal:** Enable AI-assisted template generation and validation

### Deliverables

- [ ] Agent prompt templates for comment generation
- [ ] Validation agent for curriculum alignment
- [ ] Suggestion agent for evidence-to-comment synthesis
- [ ] Integration patterns for LLM tooling

### Acceptance Criteria

- Agent can generate draft comments from evidence
- Generated comments validate against schemas
- Agent respects no-PII boundary
- Human review workflow documented

### Tasks

1. Design agent interface contracts
2. Create prompt templates for generation
3. Implement validation feedback loop
4. Document human-in-the-loop workflow
5. Test with sample evidence patterns
6. Security review for PII prevention

---

## Phase 5: SIS Integration Patterns 🔌

**Status:** Future
**Goal:** Document integration approaches (not implementation)

### Deliverables

- [ ] `docs/integration/` - Integration pattern documentation
- [ ] Export format specifications
- [ ] Import workflow documentation
- [ ] Board-specific configuration patterns

### Acceptance Criteria

- Clear documentation for Edsembli integration approach
- Export formats compatible with SIS import
- No direct API implementation (design only)
- Privacy considerations documented

### Tasks

1. Research Edsembli import/export capabilities
2. Document CSV/XML export formats
3. Design comment bank export workflow
4. Document board configuration patterns
5. Privacy impact assessment

---

## Timeline Estimates

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 0 | Complete | — |
| Phase 1 | 2-3 weeks | Phase 0 |
| Phase 2 | 1-2 weeks | Phase 1 |
| Phase 3 | 1-2 weeks | Phase 2 |
| Phase 4 | 3-4 weeks | Phase 3 |
| Phase 5 | 2-3 weeks | Phase 4 |

*Estimates assume part-time development effort.*

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-11 | Initial roadmap created |

---

## Related Documents

- [framework.md](framework.md) - Design narrative
- [infrastructure.md](infrastructure.md) - Technical specification
- [requirements.md](requirements.md) - Functional requirements
- [CHANGELOG.md](CHANGELOG.md) - Version history
