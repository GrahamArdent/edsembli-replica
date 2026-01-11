# ADR 0001: Separate canonical artifacts from source inputs

- Status: accepted
- Date: 2026-01-11

## Context

The repository includes both:
- design artifacts meant to be maintained as “truth” over time
- background research and other inputs used to inform those decisions

If these are mixed, traceability gets muddy and future edits risk treating research drafts as authoritative.

## Decision

We will separate artifacts into:
- Canonical docs/datasets at repo root and planned canonical folders (schemas/taxonomy/references/knowledge/datasets)
- Reference-only inputs under `sources/`

Canonical artifacts may cite sources, but sources are not treated as authoritative until distilled into canonical docs with durable references.

## Consequences

- Improves maintainability and auditability.
- Allows sources to be kept intact while canonical content remains concise.
- Requires discipline to extract and cite claims rather than linking to raw research.

## Alternatives considered

- Keep everything in a single document: rejected (hard to maintain; encourages drift).
- Treat sources as canonical: rejected (too noisy; not curated).
