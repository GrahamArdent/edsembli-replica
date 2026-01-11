---
id: doc.schemas.readme
type: document
title: Schemas
version: 0.1.0
status: draft
tags: [schemas, validation]
refs: []
updated: 2026-01-11
---

# Schemas

This folder contains JSON Schema contracts for canonical YAML files and Markdown front matter.

## Intended use

- Validate canonical files locally via `scripts/validate.py`.
- Later: enforce in CI and pre-commit.

## Files

### Front Matter Schemas
- `document.frontmatter.schema.json` - Markdown document front matter
- `entity.frontmatter.schema.json` - Knowledge entity front matter

### Taxonomy Schemas
- `frames.schema.json` - Four frames taxonomy
- `indicators.schema.json` - Indicator definitions
- `col_sections.schema.json` - Key Learning / Growth / Next Steps
- `tags.schema.json` - Controlled vocabulary tags
- `roles.schema.json` - Stakeholder roles

### Content Schemas
- `bibliography.schema.json` - Reference citations
- `comment_templates.schema.json` - Comment template library
- `evidence_patterns.schema.json` - Evidence pattern definitions

### Planned (not yet created)
- None - all schemas implemented!
