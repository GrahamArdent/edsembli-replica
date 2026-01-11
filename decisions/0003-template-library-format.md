# ADR 0003: Store comment templates as a YAML collection (initially)

- Status: accepted
- Date: 2026-01-11

## Context

We need a canonical library of CoL comment templates to support:
- consistent authoring
- traceability to frames/indicators
- future validation and coverage reporting

A question arises early: should each template be stored as its own file, or should templates be stored as a single collection file?

## Decision

We will store the initial comment template library as a single YAML collection:

- `templates/comment_templates.yaml`

Each template remains uniquely addressable by its stable `id`.

## Rationale

- Enables fast iteration early (avoids managing dozens of small files)
- Simplifies validation (one schema, one entrypoint)
- Still supports traceability (templates have stable IDs)

## Consequences

- The file may grow large over time.
- If it becomes unwieldy, we may split into per-template files or per-frame files later via a documented migration.

## Alternatives considered

- One file per template: rejected for initial stage due to overhead.
- One file per frame: acceptable, but deferred until the library grows.
