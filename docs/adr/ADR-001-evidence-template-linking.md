---
id: adr.001.evidence_template_linking
type: adr
title: "ADR-001: Evidence-Template Linking Strategy"
status: accepted
date: 2026-01-11
deciders: [framework-team]
tags: [adr, architecture, evidence, templates]
---

# ADR-001: Evidence-Template Linking Strategy

## Status

**Accepted**

## Context

The framework needs to connect evidence patterns (observable child behaviours) to comment templates. Two approaches exist:

1. **Explicit linking:** Each template declares which evidence patterns it can use via `evidence_ids: [...]`
2. **Heuristic matching:** Templates and evidence are linked at runtime by matching indicators/frames

### Current state

- `templates/comment_templates.yaml` has 36 templates with `indicators` and `frames` fields
- `evidence/patterns.yaml` has 15 patterns with `indicator` and `frame` fields
- There is no explicit `evidence_ids` field on templates
- The traceability matrix (`data/traceability_matrix.parquet`) links templates ↔ indicators ↔ references but not templates ↔ evidence

### Trade-offs

| Approach          | Pros                                          | Cons                                         |
| ----------------- | --------------------------------------------- | -------------------------------------------- |
| Explicit linking  | Precise, auditable, no runtime ambiguity      | High maintenance, coupling, more YAML edits  |
| Heuristic matching| Low coupling, scales automatically            | Less precise, may suggest mismatched pairs   |

## Decision

**We will use heuristic matching** for evidence-template linking, with optional explicit overrides.

### Rationale

1. **Scalability:** With 36 templates and 15 evidence patterns, explicit linking creates a 540-cell matrix to maintain. Heuristic matching scales O(n) with new templates/evidence.

2. **Separation of concerns:** Templates focus on structure/slots; evidence focuses on observable behaviours. Forcing explicit links couples two independently evolving taxonomies.

3. **Flexibility:** Educators may discover new template-evidence combinations. Heuristic matching allows experimentation without YAML changes.

4. **Fallback override:** Templates can optionally declare `preferred_evidence: [ep.001, ep.005]` to influence ranking without hard constraints.

### Heuristic algorithm

```python
def match_evidence(template: Template, evidence_pool: list[Evidence]) -> list[Evidence]:
    """Return evidence patterns ranked by relevance to template."""
    scores = []
    for ev in evidence_pool:
        score = 0
        # Frame match: +3
        if ev.frame in template.frames:
            score += 3
        # Indicator match: +5
        if ev.indicator in template.indicators:
            score += 5
        # Preferred evidence bonus: +10
        if ev.id in (template.preferred_evidence or []):
            score += 10
        scores.append((ev, score))
    # Return sorted by score descending, filter score > 0
    return [ev for ev, s in sorted(scores, key=lambda x: -x[1]) if s > 0]
```

## Consequences

### Positive

- No new YAML fields required on templates
- Evidence patterns remain independent
- Runtime flexibility for educator exploration
- Optional `preferred_evidence` allows soft constraints when needed

### Negative

- Heuristic may suggest low-relevance matches; UI must show relevance score
- Harder to audit "which evidence goes with which template" without running code
- May need tuning of score weights over time

### Mitigations

1. **Relevance threshold:** Only show matches with score ≥ 5 (at least indicator match)
2. **Audit report:** Add CLI command `edsembli evidence-matrix` to dump heuristic matches for review
3. **Preferred evidence:** Allow explicit soft-linking when educators identify strong pairs

## Alternatives considered

### Alternative A: Explicit linking via `evidence_ids`

Rejected because:
- Maintenance burden scales quadratically
- Couples template and evidence taxonomies
- Requires YAML edits for every new combination

### Alternative B: Vector similarity (embeddings)

Rejected for v1 because:
- Adds LLM/embedding dependency
- Overkill for 36 templates × 15 evidence patterns
- May revisit if corpus grows to 200+ templates

## Related decisions

- Slot type taxonomy (see `taxonomy/slot_guidance.yaml`)
- Template deprecation workflow (see ADR-002, planned)

## References

- `templates/comment_templates.yaml`
- `evidence/patterns.yaml`
- `data/traceability_matrix.parquet`
