---
id: doc.guidance.comment_assembly
type: document
title: Comment Assembly Rules
version: 0.1.2
status: stable
tags: [guidance, assembly, comments, col]
refs:
  - ref.ontario.kindergarten.program.2016
updated: 2026-01-12
---

# Comment Assembly Rules

This document defines constraints for assembling complete CoL narrative comments from templates.

## Applicability to VGReport Kindergarten (12-box workflow)

VGReport’s Kindergarten UX is a **12-box workflow** (4 Frames × 3 Sections), where each box is entered and exported independently.

Therefore:
- The **3-section assembled comment** rules in this document apply directly to:
  - CLI/template-bank workflows that generate a single combined narrative, and
  - any export format that produces a single 3-section comment.
- For **VGReport 12-box exports**, constraints SHOULD be evaluated **per box** (per Frame × Section), because SIS entry and copy/paste happen per box.

Guidance for VGReport:
- Hard blockers (export-stopping) SHOULD be per-box: empty box, unapproved box, hard render/placeholder errors.
- Soft guardrails (warnings) MAY be derived from these assembly rules (sentence length, readability targets), but SHOULD remain non-blocking unless explicitly configured.
- The UI MAY also provide student-level rollups (e.g., “3/12 boxes too long”), but those rollups MUST be traceable to specific boxes.

## Section requirements

A complete CoL comment consists of three sections in this order:

| Section       | Required | Max templates | Purpose                                |
| ------------- | -------- | ------------- | -------------------------------------- |
| `key_learning`| Yes      | 2             | Current strengths + evidence           |
| `growth`      | Yes      | 1             | Progress comparison (now vs. before)   |
| `next_steps`  | Yes      | 1             | Goal + school strategy + home strategy |

## Character limits

These limits reflect typical Student Information System (SIS) field constraints:

| Scope             | Min chars | Max chars | Rationale                        |
| ----------------- | --------- | --------- | -------------------------------- |
| Per section       | 100       | 600       | Readability + SIS field limits   |
| Full comment      | 400       | 1500      | Report card layout constraints   |
| Per sentence      | 20        | 200       | Cognitive load / readability     |

> **Note:** Some boards have tighter limits (e.g., 1200 chars total). See `guidance/board-customization.md` for override patterns.

## Readability targets

| Metric                         | Target range | Library        |
| ------------------------------ | ------------ | -------------- |
| Flesch Reading Ease            | 60–80        | textstat       |
| Flesch-Kincaid Grade Level     | 6–8          | textstat       |
| Automated Readability Index    | 6–8          | textstat       |

Comments outside these ranges should be flagged for simplification (too complex) or elaboration (too simple).

## Slot fill constraints

When filling slots at assembly time:

| Slot type     | Constraint                                                                 |
| ------------- | -------------------------------------------------------------------------- |
| `identity`    | Must match child record exactly (name, pronouns)                           |
| `pronoun`     | Must be internally consistent across all templates in the comment          |
| `observation` | Must be observable behaviour (no inferred traits)                          |
| `attribute`   | Should not name other children                                             |
| `growth`      | Must reference a prior state; avoid "always" or "never"                    |
| `next_step`   | Must be specific + achievable; include who-what-when                       |

See `taxonomy/slot_guidance.yaml` for the full slot type taxonomy and validation rules.

## Indicator coverage

A complete comment should cover **at least 2 distinct indicators** from the four frames:

- Belonging and Contributing
- Self-Regulation and Well-Being
- Demonstrating Literacy and Mathematics Behaviours
- Problem Solving and Innovating

Assembly logic should warn if:
- Only one indicator is referenced
- The same indicator appears in more than one section
- No indicator is referenced at all

## Template compatibility

Not all templates can be combined. Compatibility rules:

| Rule                    | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `frame_match`           | All templates should share at least one common frame         |
| `tone_consistency`      | Avoid mixing `formal` and `parent_friendly` tones            |
| `pronoun_agreement`     | All templates must use the same pronoun set                  |
| `no_duplicate_evidence` | Evidence phrases should not repeat across sections           |

## Assembly workflow

```
1. Select templates for each section (respecting section limits)
2. Validate indicator coverage ≥ 2 distinct
3. Fill slots with child-specific data
4. Check pronoun consistency across all filled templates
5. Concatenate sections with paragraph breaks
6. Compute readability scores
7. Validate total length ≤ 1500 chars
8. Return assembled comment or list of validation errors
```

## Error handling

| Error code              | Meaning                                      | Resolution                        |
| ----------------------- | -------------------------------------------- | --------------------------------- |
| `ERR_SECTION_MISSING`   | Required section has no template             | Select at least one template      |
| `ERR_OVER_LIMIT`        | Total chars exceed max                       | Shorten or remove template        |
| `ERR_UNDER_LIMIT`       | Total chars below min                        | Add detail or another template    |
| `ERR_LOW_INDICATOR`     | Fewer than 2 indicators covered              | Select more diverse templates     |
| `ERR_READABILITY_HIGH`  | Flesch-Kincaid > 8                           | Simplify vocabulary/sentences     |
| `ERR_PRONOUN_MISMATCH`  | Inconsistent pronouns across templates       | Regenerate with consistent set    |

## Future extensions

- **Locale-aware limits:** French comments may have different char limits
- **Board presets:** Pre-configured constraint sets per school board
- **Auto-simplification:** LLM-assisted rewriting when readability fails
