---
id: process.reporting.workflow
type: process
title: Standard Operating Procedure - Reporting Cycle
version: 0.1.0
status: draft
tags: [workflow, reporting, sop]
refs:
  - ref.ontario.growing.success.2010
updated: 2026-01-11
---

# SOP: Kindergarten Reporting Cycle

## 1. Objective
To produce accurate, strengths-based, and PII-free Communication of Learning (CoL) narratives that adhere to Ministry and Board standards.

## 2. Roles
- **Classroom Teacher**: Primary author of narratives; verifies pedagogical accuracy.
- **ECE**: Co-author/contributor; verifying observation details.
- **Principal**: Final reviewer/approver.

## 3. Workflow Steps

### Phase 1: Evidence Gathering (Ongoing)
1.  **Observe**: Capture learning moments in the classroom.
2.  **Document**: Create *Evidence Records* (notes, photos, videos) stored in the secure board platform (NOT in this repo).
3.  **Tag**: Tag evidence with relevant Frames and Indicators (e.g., `indicator.belonging.relationships`).

### Phase 2: Synthesis & Drafting (Reporting Period)
1.  **Review Evidence**: aggregate observations for a specific child per frame.
2.  **Select Template**: Choose a `comment_template` that matches the student's key learning.
    - *Input*: Child's demonstrated skills.
    - *Tool*: Template Library (`templates/comment_templates.yaml`).
3.  **Fill Slots**: Replace placeholders (`{child}`, `{evidence}`) with specific details from Phase 1.
    - *Constraint*: Ensure no PII remains other than the {child} name which is inserted at generation time.
4.  **Draft Narrative**: Combine Key Learning, Growth, and Next Steps into a cohesive paragraph.

### Phase 3: Review & Finalization
1.  **Partner Review**: Teacher and ECE review drafts for accuracy and tone.
2.  **Technical Review**: Check against constraints (character limits, banned words).
3.  **Submission**: Paste final text into Edsembli SIS.

## 4. Quality Control Checklist
- [ ] Tone is parent-friendly and strengths-based?
- [ ] Connects strictly to the Frame (not subject-specific reporting)?
- [ ] Next Steps are specific and actionable?
- [ ] No unreplaced placeholders (e.g., `{evidence}`)?
