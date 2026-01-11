# Sample Comment Template
# Demonstrates structure for a Communication of Learning comment
# Type: Comment Template (template.comment)

---
id: template.comment.belonging.sample
type: comment_template
frame: frame.belonging
section: key_learning
status: draft
version: 0.1.0
created: 2026-01-11
updated: 2026-01-11
refs:
  - ref.ontario.kindergarten.program.2016
  - ref.ontario.growing.success.2010
---

## Overview

This sample demonstrates how comment templates are structured for the
Communication of Learning (CoL) reports. Templates provide reusable
language patterns that educators can customize with student-specific
observations.

**Important:** These are structural patterns, not actual student comments.

## Template Structure

### Comment Template Schema

```yaml
template:
  id: "[unique identifier following naming convention]"
  frame: "[frame.belonging | frame.self_regulation | frame.literacy_math | frame.problem_solving]"
  section: "[key_learning | growth | next_steps]"

  # The template text with placeholders
  text: |
    {child} demonstrates {skill} by {evidence}.
    {pronoun_subject} {example}.

  # Placeholders that must be customized
  placeholders:
    - child: "{child}"
    - pronoun_subject: "{pronoun_subject}"
    - skill: "{skill}"
    - evidence: "{evidence}"
    - example: "{example}"

  # Curriculum alignment
  indicators:
    - "[indicator.id]"

  # Usage guidance
  notes: |
    [When to use this template, customization tips]
```

## Example Templates (Fictional)

### Key Learning - Belonging Frame

```yaml
template:
  id: template.comment.keyl_belonging_relationships_01
  frame: frame.belonging
  section: key_learning

  text: |
    {child} is developing a sense of belonging within our
    classroom community. {pronoun_subject} {evidence},
    demonstrating an understanding that {pronoun_subject_lower} {be_verb} a valued
    member of our learning family.

  placeholders:
    - child: "{child}"
    - pronoun_subject: "{pronoun_subject}"
    - pronoun_subject_lower: "{pronoun_subject_lower}"
    - be_verb: "{be_verb}"
    - evidence: "{evidence}"

  indicators:
    - indicator.belonging.relationships
    - indicator.belonging.community

  notes: |
    Use when student shows emerging sense of classroom membership.
    Customize with specific examples from observations.
```

### Growth - Belonging Frame

```yaml
template:
  id: template.comment.grow_belonging_relationships_01
  frame: frame.belonging
  section: growth

  text: |
    Since the beginning of the year, {child} has shown growth in
    {pronoun_possessive} ability to {skill}. {pronoun_subject} now
    {change}, whereas previously {previous}.

  placeholders:
    - child: "{child}"
    - pronoun_subject: "{pronoun_subject}"
    - pronoun_possessive: "{pronoun_possessive}"
    - skill: "{skill}"
    - change: "{change}"
    - previous: "{previous}"

  indicators:
    - indicator.belonging.relationships

  notes: |
    Requires comparison to earlier observations.
    Focus on positive trajectory, not deficits.
```

### Next Steps - Belonging Frame

```yaml
template:
  id: template.comment.next_belonging_relationships_01
  frame: frame.belonging
  section: next_steps

  text: |
    A next step for {child} is to {goal}. At school,
    we will {school_strategy}. At home, you can support this by
    {home_strategy}.

  placeholders:
    - child: "{child}"
    - goal: "{goal}"
    - school_strategy: "{school_strategy}"
    - home_strategy: "{home_strategy}"

  indicators:
    - indicator.belonging.relationships

  notes: |
    Always include both school and home components.
    Goals should be achievable and observable.
```

## Template Categories

Templates are organized by:

| Category | Naming Pattern | Example |
|----------|----------------|---------|
| Key Learning | `template.comment.keyl_[frame]_[indicator]_[nn]` | `template.comment.keyl_belonging_relationships_01` |
| Growth | `template.comment.grow_[frame]_[indicator]_[nn]` | `template.comment.grow_self_reg_emotions_03` |
| Next Steps | `template.comment.next_[frame]_[indicator]_[nn]` | `template.comment.next_literacy_reading_02` |

## Privacy and Usage

- Templates contain **NO** student data
- Placeholders are filled at runtime by educators
- Actual populated comments exist only in the SIS
- This repository stores patterns only

## Integration Notes

Templates connect to:

1. **Frames** ([taxonomy/frames.yaml](../taxonomy/frames.yaml)) - Curriculum alignment
2. **Indicators** - Specific learning expectations
3. **Evidence Patterns** ([evidence-pattern-sample.md](evidence-pattern-sample.md)) - Supporting observations
4. **Traceability Matrix** - Validation that all indicators have templates

## Related Files

- [taxonomy/frames.yaml](../taxonomy/frames.yaml) - Frame definitions
- [evidence-pattern-sample.md](evidence-pattern-sample.md) - Evidence pattern example
- [docs/infrastructure.md](../docs/infrastructure.md) - Schema specifications
- [docs/glossary.md](../docs/glossary.md) - Term definitions
