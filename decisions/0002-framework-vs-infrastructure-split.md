# ADR 0002: Keep framework narrative separate from infrastructure specification

- Status: accepted
- Date: 2026-01-11

## Context

We need both:
- a short, human-readable explanation of what the framework is (for educators/maintainers)
- a structured specification for IDs, schemas, traceability, and tooling (for long-term maintainability)

If combined, the narrative becomes too long and the spec becomes inconsistent.

## Decision

- `docs/framework.md` is a short narrative: intent, boundaries, principles, and high-level model.
- `docs/infrastructure.md` is the structured specification: repository layout, conventions, schemas, traceability, governance, and tooling.

## Consequences

- Readers can quickly understand the “why” without wading through operational details.
- The spec becomes the single place for MUST/SHOULD rules.
- Future automation and validation work has a clear contract to follow.

## Alternatives considered

- Single monolithic doc: rejected (hard to maintain; hard to navigate).
- Put everything in infrastructure: rejected (loses human-friendly overview).
