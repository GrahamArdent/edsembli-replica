# Sample Evidence Pattern
# Demonstrates structure for a kindergarten observation
# Type: Evidence Pattern (evidence.pattern)

---
id: evidence.pattern.belonging.sample
type: evidence_pattern
frame: frame.belonging
indicators:
  - indicator.belonging.relationships
  - indicator.belonging.community
status: draft
version: 0.1.0
created: 2026-01-11
updated: 2026-01-11
refs:
  - ref.ontario.kindergarten.program.2016
---

## Context

This sample evidence pattern demonstrates how educators can document
observations that support the "Belonging and Contributing" frame. This
is NOT real student data—it is a structural template only.

## Pattern Structure

### Observation Template

```yaml
observation:
  date: YYYY-MM-DD
  context: "[Learning area or activity type]"
  setting: "[Indoor/Outdoor/Transition]"

  # What was observed (factual, no interpretation)
  what_happened: |
    {child} was [doing what] during [activity].
    [Specific observable actions or statements.]

  # Connection to frame indicators
  indicators_observed:
    - indicator.belonging.relationships

  # Potential comment elements (for CoL synthesis)
  key_learning_elements:
    - "[Skill or understanding demonstrated]"
  growth_elements:
    - "[Progress from previous observations]"
  next_steps_elements:
    - "[Suggested focus for continued development]"
```

### Example Observation (Fictional)

```yaml
observation:
  date: 2026-01-15
  context: "Collaborative block play"
  setting: "Indoor - Construction Centre"

  what_happened: |
    During free exploration time, {child} noticed that another
    child was having difficulty balancing blocks for a tall tower.
    {child} offered to hold the base steady and suggested using
    larger blocks at the bottom. The two children worked together
    for approximately 10 minutes, taking turns adding blocks.

  indicators_observed:
    - indicator.belonging.relationships
    - indicator.belonging.community

  key_learning_elements:
    - "Demonstrates cooperative play skills"
    - "Offers help to peers spontaneously"
    - "Uses problem-solving language ('maybe we could...')"

  growth_elements:
    - "Previously engaged primarily in parallel play"
    - "Now initiating collaborative interactions"

  next_steps_elements:
    - "Continue providing opportunities for small-group projects"
    - "Encourage {child} to share strategies during reflection time"
```

## Privacy Notes

- **NO** real student names, identifying information, or actual observations
- This is a structural template only
- Actual evidence would be stored in the SIS, not in this repository
- The framework provides patterns; implementation stores no PII

## Usage

Educators would use this pattern to:

1. Structure their observation notes consistently
2. Connect observations to specific frame indicators
3. Prepare elements for the Communication of Learning synthesis
4. Maintain alignment with curriculum expectations

## Related Files

- [taxonomy/frames.yaml](../taxonomy/frames.yaml) - Frame and indicator definitions
- [docs/glossary.md](../docs/glossary.md) - Term definitions
- [docs/infrastructure.md](../docs/infrastructure.md) - Schema specifications
