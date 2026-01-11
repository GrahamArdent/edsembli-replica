# ADR 0005: ID naming convention (type.domain.name)

- Status: accepted
- Date: 2026-01-11

## Context

Canonical artifacts need stable, unique identifiers for:
- Cross-referencing between documents
- Validation and linting
- Traceability matrix construction
- Future database/search indexing

Without a convention, IDs drift (e.g., `frame.selfregulation` vs `frame.self_regulation`), breaking validation and traceability.

## Decision

All canonical IDs follow the **`type.domain.name`** pattern:

```
type.domain.name
type.domain.subdomain.name
```

### Type Prefixes

| Prefix | Used For | Example |
|--------|----------|---------|
| `doc.*` | Canonical documents | `doc.framework`, `doc.infrastructure` |
| `ref.*` | Bibliography citations | `ref.ontario.kindergarten.program.2016` |
| `entity.*` | Tools, boards, policies | `entity.tool.edsembli`, `entity.board.ncdsb` |
| `frame.*` | Four Kindergarten Frames | `frame.belonging`, `frame.self_regulation` |
| `indicator.*` | Specific indicators | `indicator.belonging.relationships` |
| `evidence.*` | Evidence patterns | `evidence.pattern.block_play` |
| `template.*` | Comment templates | `template.comment.belonging.key_learning.01` |
| `req.*` | Functional requirements | `req.privacy.1` |
| `tag.*` | Controlled vocabulary tags | `tag.curriculum`, `tag.assessment` |
| `role.*` | Stakeholder roles | `role.teacher`, `role.parent` |

### Rules

1. **Lowercase only**: `frame.self_regulation`, not `frame.Self_Regulation`
2. **Underscores for multi-word**: `self_regulation`, not `selfregulation` or `self-regulation`
3. **Dots for hierarchy**: `template.comment.belonging.key_learning.01`
4. **Stable IDs**: Changing an ID is a breaking change requiring migration
5. **No spaces or special characters**: Only `[a-z0-9_.]`

### Validation

IDs are validated via JSON Schema patterns:
```json
"pattern": "^type\\.[a-z0-9_\\.]+$"
```

## Rationale

1. **Predictable structure**: Easy to parse, sort, and filter
2. **Self-documenting**: ID reveals what type of artifact it is
3. **Collision-resistant**: Type prefix prevents `teacher` (role) colliding with `teacher` (tag)
4. **Machine-readable**: Supports automated validation and indexing
5. **Human-readable**: Meaningful names, not UUIDs

## Consequences

- All canonical files must declare an `id` field following this convention
- JSON Schemas enforce ID patterns
- `lint.py` can verify cross-references resolve
- Changing the convention requires a migration ADR

## Alternatives Considered

- **UUIDs**: Rejected; not human-readable, hard to debug
- **Sequential numbers**: Rejected; doesn't scale across artifact types
- **Flat names**: Rejected; collision risk, no type information
- **Hyphens instead of underscores**: Rejected; underscores are more common in identifiers
