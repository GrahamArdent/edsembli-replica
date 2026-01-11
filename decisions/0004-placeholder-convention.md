# ADR 0004: Use curly-brace slot placeholders

- Status: accepted
- Date: 2026-01-11

## Context

Comment templates require placeholders that educators fill in with specific details (child's name, evidence, next steps, etc.). Multiple placeholder styles exist in the wild:

- Bracket style: `[Child's name]`, `[STUDENT]`, `[he/she/they]`
- Curly-brace style: `{child}`, `{pronoun_subject}`, `{evidence}`
- Angle-bracket style: `<name>`, `<evidence>`
- Double-curly (Jinja/Mustache): `{{child}}`, `{{evidence}}`

We need a single convention for consistency and validation.

## Decision

All comment templates use **curly-brace slot placeholders**:

```
{child}
{pronoun_subject}
{pronoun_possessive}
{pronoun_object}
{evidence}
{strength}
{change}
{previous}
{goal}
{school_strategy}
{home_strategy}
{next_step}
```

## Rationale

1. **Validation-friendly**: Easy to parse with regex `\{[a-z_]+\}`
2. **Distinct from prose**: Unlikely to appear in natural English
3. **Copy-paste safety**: Reduces accidental inclusion of actual names
4. **Consistent with template engines**: Familiar pattern for programmatic expansion
5. **Lowercase with underscores**: Aligns with ID naming convention

## Consequences

- All existing templates must use this style (enforced by lint.py)
- Documentation must list canonical slot names
- Future tooling can auto-expand slots from structured data

## Canonical Slot Names

| Slot | Purpose |
|------|---------|
| `{child}` | Child's name (filled at report time) |
| `{pronoun_subject}` | he/she/they |
| `{pronoun_possessive}` | his/her/their |
| `{pronoun_object}` | him/her/them |
| `{evidence}` | Specific observable evidence |
| `{strength}` | Identified strength or skill |
| `{change}` | Description of growth/change |
| `{previous}` | Previous state (for growth comparison) |
| `{goal}` | Next step learning goal |
| `{school_strategy}` | How school will support the goal |
| `{home_strategy}` | How home can support the goal |
| `{next_step}` | General next step description |

## Alternatives Considered

- **Bracket style**: Rejected; looks like editorial notes, easy to confuse
- **Double-curly**: Rejected; overkill for static templates, conflicts with Jinja if used later
- **Angle-bracket**: Rejected; conflicts with HTML/XML if templates rendered in web UI
