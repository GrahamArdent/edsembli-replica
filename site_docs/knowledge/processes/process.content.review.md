---
id: process.content.review
type: process
title: Content Review Checklist
version: 0.1.0
status: draft
tags: [workflow, review, quality]
refs:
  - ref.ontario.growing.success.2010
updated: 2026-01-11
---

# SOP: Content Review Checklist

## 1. Objective
To ensure all new templates, evidence patterns, and documentation meet framework quality standards before being marked as `stable`.

## 2. Roles
- **Author**: Creates initial draft
- **Reviewer**: Checks against criteria below
- **Approver**: Marks status as `stable`

## 3. Review Criteria

### 3.1 Privacy Check
- [ ] No real student names, identifiers, or photos
- [ ] No real teacher/school names
- [ ] Placeholders use `{slot}` format only
- [ ] No data that could identify an individual

### 3.2 Curriculum Alignment
- [ ] Mapped to correct Frame(s)
- [ ] Mapped to specific Indicator(s)
- [ ] References include `ref.ontario.kindergarten.program.2016`
- [ ] Language aligns with Ontario Kindergarten Program

### 3.3 Style Compliance
- [ ] Tone is strengths-based and parent-friendly
- [ ] No deficit language or comparative rankings
- [ ] Appropriate length (not too long/short)
- [ ] No banned phrases (see guidance/comment-style.md)

### 3.4 Technical Validity
- [ ] Front matter passes schema validation
- [ ] All `ref.*` IDs exist in bibliography
- [ ] All `indicator.*` IDs exist in taxonomy
- [ ] ID follows `type.domain.name` convention

### 3.5 Completeness
- [ ] All required fields populated
- [ ] Observable behaviors/signals documented
- [ ] Teacher moves/prompts included (for evidence patterns)
- [ ] Sample observation template provided

## 4. Review Process

1. **Author** creates content with `status: draft`
2. **Author** runs `python scripts/validate.py` and `python scripts/lint.py`
3. **Reviewer** uses this checklist to assess
4. **Reviewer** provides feedback or approves
5. **Approver** changes `status: stable` and increments version
6. **Author** commits with descriptive message

## 5. Escalation
If reviewer and author disagree, escalate to team lead for decision. Document rationale in an ADR if it establishes new precedent.
