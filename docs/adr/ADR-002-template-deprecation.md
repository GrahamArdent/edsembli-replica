---
id: adr.002.template_deprecation
type: adr
title: "ADR-002: Template Deprecation Workflow"
status: accepted
date: 2026-01-11
deciders: [framework-team]
tags: [adr, architecture, templates, lifecycle]
---

# ADR-002: Template Deprecation Workflow

## Status

**Accepted**

## Context

Templates evolve over time. Language changes, pedagogical guidance updates, or better alternatives emerge. We need a controlled way to:

1. Mark templates as deprecated without breaking existing references
2. Guide users toward replacement templates
3. Eventually remove obsolete templates

### Current state

- Templates have `status: draft | stable` only
- No mechanism to indicate "this template is outdated, use X instead"
- No lifecycle metadata (created_at, deprecated_at)

## Decision

**Add a `replaces` field and expand `status` values** to support a deprecation workflow.

### Schema changes

```yaml
# Template schema additions
status:
  enum: [draft, stable, deprecated, archived]

replaces:        # Optional: ID of template this one supersedes
  type: string
  pattern: "^tmpl\\.[a-z0-9_]+$"

deprecated_by:   # Optional: ID of template that supersedes this one
  type: string
  pattern: "^tmpl\\.[a-z0-9_]+$"

lifecycle:       # Optional lifecycle metadata
  type: object
  properties:
    created: { type: string, format: date }
    deprecated: { type: string, format: date }
    archived: { type: string, format: date }
```

### Status lifecycle

```
draft → stable → deprecated → archived
  │                  │
  └──────────────────┘ (can revert if deprecation premature)
```

| Status       | Meaning                                      | Visibility                    |
| ------------ | -------------------------------------------- | ----------------------------- |
| `draft`      | Work in progress, not for production         | Hidden in production selectors|
| `stable`     | Approved for use                             | Fully visible                 |
| `deprecated` | Superseded, still usable but discouraged     | Visible with warning          |
| `archived`   | Removed from active use                      | Hidden, kept for audit trail  |

### Deprecation workflow

1. **Identify replacement:** Create new template with improved language
2. **Link templates:** Add `replaces: tmpl.old_id` to new template
3. **Mark deprecated:** Change old template to `status: deprecated` and add `deprecated_by: tmpl.new_id`
4. **Notify users:** CLI/UI shows "This template is deprecated. Consider using: tmpl.new_id"
5. **Archive after grace period:** After 6 months with no usage, change to `status: archived`

### Example

```yaml
# Old template (deprecated)
- id: tmpl.key_learning.exploration.001
  status: deprecated
  deprecated_by: tmpl.key_learning.exploration.002
  lifecycle:
    created: "2025-09-01"
    deprecated: "2026-01-15"
  text: "{child} explores materials..."

# New template (replacement)
- id: tmpl.key_learning.exploration.002
  status: stable
  replaces: tmpl.key_learning.exploration.001
  lifecycle:
    created: "2026-01-15"
  text: "{child} actively explores materials..."
```

## Consequences

### Positive

- Clear migration path when templates improve
- Audit trail of template evolution
- Users guided toward better alternatives
- Old reports remain valid (deprecated templates still exist)

### Negative

- Additional YAML fields to maintain
- Lint rules needed to validate `replaces`/`deprecated_by` consistency
- UI must handle deprecation warnings gracefully

### Mitigations

1. **Lint check:** Add to `scripts/lint.py`:
   - If `status: deprecated`, `deprecated_by` should be set
   - If `deprecated_by` is set, target template should exist and be `stable`
   - If `replaces` is set, old template should be `deprecated` or `archived`

2. **CLI command:** `edsembli templates --show-deprecated` to list migration pairs

## Alternatives considered

### Alternative A: Delete deprecated templates

Rejected because:
- Breaks references in existing reports
- No audit trail
- No migration guidance

### Alternative B: Version numbers on templates

Rejected because:
- Adds complexity (tmpl.foo.v1, tmpl.foo.v2)
- Harder to query "latest stable"
- Deprecation status is clearer than version comparison

## Related decisions

- ADR-001: Evidence-Template Linking (heuristic matching unaffected by deprecation)
- Slot guidance taxonomy (`taxonomy/slot_guidance.yaml`)

## References

- `templates/comment_templates.yaml`
- `schemas/template.schema.json`
