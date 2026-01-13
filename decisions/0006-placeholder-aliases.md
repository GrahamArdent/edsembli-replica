# ADR 0006: Support common placeholder aliases at render time

- Status: accepted
- Date: 2026-01-12

## Context

Educators often encounter (or author) comment text using non-canonical placeholders such as `{Name}` or `{He/She}`.

In this repository, canonical placeholder convention is locked to lowercase snake_case curly-brace slots (see ADR 0004).
However, we want to reduce churn and make the system more tolerant of imported or legacy content without rewriting the canonical template library.

Key constraints:
- **Do not introduce PII** (placeholders should remain placeholders).
- Avoid destabilizing template validation and slot requirements.
- Keep behavior deterministic and testable.

## Decision

At render time, the engine will support a small, explicit alias mapping for common “teacher mental model” placeholders.

- Aliases are **case-insensitive**.
- Aliases are applied by normalizing both:
  1) placeholders found in the template text, and
  2) keys present in the provided slot values.

The initial supported aliases are:

| Alias placeholder | Canonical slot |
|---|---|
| `{Name}` | `{child}` |
| `{Student}` | `{child}` |
| `{He/She}` | `{pronoun_subject}` |
| `{He/She/They}` | `{pronoun_subject}` |
| `{Him/Her}` | `{pronoun_object}` |
| `{Him/Her/Them}` | `{pronoun_object}` |
| `{His/Her}` | `{pronoun_possessive}` |
| `{His/Her/Their}` | `{pronoun_possessive}` |

## Consequences

- Templates can remain canonical while the renderer tolerates a small set of legacy placeholders.
- Validation can continue to use canonical slot guidance.
- The alias mapping must remain narrow to avoid ambiguous placeholders and surprising substitutions.

## Alternatives considered

- **Rewrite templates to canonical placeholders**: rejected (unnecessary churn; breaks imported content).
- **Allow arbitrary aliases in templates/taxonomy**: rejected for v1 (too much complexity; harder to validate).
- **Add schema changes to formally encode aliases**: deferred (ADR-worthy but not required for the current goal).
