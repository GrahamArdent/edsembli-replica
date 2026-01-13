---
id: doc.research.edsembli_report_card_requirements_vs_vgreport
type: document
title: Edsembli Report Card Requirements vs VGReport (Gap + Options)
version: 0.1.0
status: draft
tags: [research, requirements, edsembli, comparison]
refs:
  - doc.vgreport.frontend_design
  - doc.integration.sis_formats
  - doc.framework
updated: 2026-01-12
---

# Edsembli Report Card Requirements vs VGReport (Gap + Options)

## Scope and source

This document extracts **specifics, requirements, and configuration options** from these saved source notes:

- [sources/edsembli/Edsembli Report Card Software Details.md](sources/edsembli/Edsembli%20Report%20Card%20Software%20Details.md)
- [sources/edsembli/Edsembli API Access and Data Options.md](sources/edsembli/Edsembli%20API%20Access%20and%20Data%20Options.md)

It then compares those requirements to **VGReport’s current design + repo reality**, primarily as described in:
- docs/frontend.md
- docs/integration/sis-formats.md
- docs/framework.md

**Important:** The source note is a secondary summary (not an official Ministry/Edsembli spec). Treat these items as *requirements to validate* where they influence implementation.

---

## A) What the source note says Edsembli supports (capabilities)

### A1. Product format
- **Web-based interface** (browser-accessed, cloud-hosted)
- **“Live Form” editing**: teacher edits on a screen that looks like the final printed report card; reduces “line counting” risk

### A2. Coverage (data tracked)
- Attendance: **days absent** and **times late**
- Achievement: **subject-specific grades**
- Narrative: **anecdotal comments**
- Non-achievement: **learning skills** (separate evaluation areas)

### A3. Efficiency features
- **Comment banks** (board/school/teacher level) with placeholders (e.g., `{Name}`, `{He/She}`)
- **Batch actions** (apply common comment/grade to a group, then customize)

### A4. Governance/compliance features
- **Audit logs**: track who accessed/changed records (privacy compliance)
- **Digital verification**: parent self-serve verification ("September paper flood" replacement)

---

## B) Grade-level reporting requirements (as described in the source note)

### B1. Kindergarten (Communication of Learning)
- **Entirely anecdotal**, organized by the **Four Frames**:
  - Belonging and Contributing
  - Self-Regulation and Well-Being
  - Demonstrating Literacy and Mathematics Behaviours
  - Problem Solving and Innovating
- For each frame, comments cover **Key Learning**, **Growth in Learning**, **Next Steps in Learning**
- **Teacher + ECE collaboration** is expected; teacher is final author/signer

### B2. Grades 1–8 (Elementary Provincial Report Card)
- Achievement as **letter grades**: A through D and R
- Each subject has **letter grade + anecdotal comment**
- **Learning Skills**: six areas evaluated using **E/G/S/N** scale:
  - Responsibility
  - Organization
  - Independent Work
  - Collaboration
  - Initiative
  - Self-Regulation

### B3. Grades 9–12 (Secondary Provincial Report Card)
- Achievement as **percentage marks**
- Mentions typical **70% coursework / 30% final evaluation** weighting (exam/project/culminating)

---

## C) Required vs optional fields (as described in the source note)

### C1. Required fields
- Student **OEN**
- Attendance data
- **Teacher and principal signatures**

### C2. Required indicators / program checkboxes
- Mandatory indicators for:
  - **IEP**
  - **ESL/ELD**
  - **French immersion/core** programs

### C3. Optional/flexible fields
- Anecdotal comment depth is teacher professional judgment
- For Kindergarten, note claims a typical minimum (e.g., “minimum of three sentences”), but teachers are not required to fill the entire comment box

---

## D) Space / length constraints (as described in the source note)

### D1. How limits work
- Limits are primarily **visual boundaries of the printed box**, not a strict character count

### D2. Board-level configuration options
- Administrators can set:
  - Font styles
  - Font sizes (note mentions 12pt suggested)
  - Comment box width/height

### D3. Comment bank strategy
- Comment banks help teachers stay within visual constraints, then personalize

---

## E) Parent access and expectations (as described in the source note)

- Parents use **Edsembli Connect** portal for report cards, IEPs, attendance
- Communication standard: **plain language** and avoid “edu-babble”
- Mentions expectation that schools respond to parent concerns within **two business days**
- Catholic boards may include **faith-based reflections** aligned to Catholic Graduate Expectations

---

## F) VGReport: current system setup (repo reality)

### F1. Current product direction
- VGReport is a **desktop app** concept (Tauri + React) rather than a web portal
- Primary scope is **Kindergarten Communication of Learning** narratives (Four Frames + Key Learning/Growth/Next Steps)
  - See docs/frontend.md and docs/framework.md

### F2. Data model (current design)
- Proposed local SQLite storage in docs/frontend.md includes:
  - `students` (name + pronouns)
  - `report_periods` (Fall/Feb/June)
  - `drafts` (per student + period + frame + section)
  - `evidence_snippets` (personal evidence bank)

### F3. Integration/export posture
- This repo already defines SIS integration exports focused on **Kindergarten CoL**:
  - Template bank export (CSV/JSON)
  - Assembled comment export (txt/JSON)
  - See docs/integration/sis-formats.md

### F4. What’s explicitly not part of the canonical “framework”
- The canonical framework docs emphasize a **no-PII boundary** in the repo itself
  - See docs/framework.md
- VGReport (the app) can still be local-first with PII in local SQLite; but the repo should not store real student data

---

## G) Comparison: Edsembli requirements vs VGReport (today)

### G1. High-level comparison table

| Area | Edsembli (per source note) | VGReport (current design/repo) | Gap / Notes |
|------|-----------------------------|---------------------------------|------------|
| Product model | Cloud/web + parent portal | Desktop/offline-first app | Different delivery model; VGReport would export into SIS rather than replace it |
| Editing model | “Live Form” WYSIWYG report card | Live preview + planned print/PDF export | Similar intent; VGReport needs fidelity to printed forms |
| Kindergarten structure | 4 Frames + 3 subsections | Matches (Frames + Key/Growth/Next Steps) | Strong alignment |
| Elementary (1–8) structure | Letter grades + learning skills | Not in scope / not modeled | Major scope expansion if pursued |
| Secondary (9–12) structure | Percentage marks + weighting | Not in scope / not modeled | Major scope expansion if pursued |
| Attendance | Days absent + lates | Not present in current VGReport schema | Add only if VGReport aims to generate full official report cards |
| OEN | Required | Not present | High-PII; likely avoid unless necessary |
| Signatures | Teacher + principal | Not present | If exporting only comments, signatures irrelevant |
| Program checkboxes | IEP, ESL/ELD, French | Mentioned as per-student flags in docs/frontend.md (design) | Needs explicit requirement decision per export target |
| Comment banks | Built-in; placeholders | VGReport has template system; export formats exist | Already aligned conceptually |
| Audit logs | Tracks access/changes | VGReport local app not specified | Might be optional unless compliance requires it |
| Plain language | Explicit expectation | Strongly aligned (tone/readability discussed) | Good fit |

### G2. The key difference: VGReport is a “comment production tool,” not a full SIS

Edsembli, per the source note, manages:
- Official grades/skills, attendance, signatures, program flags, and parent portal distribution.

VGReport (as currently designed) is best positioned to:
- Help a teacher assemble **high-quality narrative comments** (especially Kindergarten CoL)
- Provide “live validation” and export formats that make SIS entry faster and more consistent

If VGReport’s goal stays “Edsembli replica for writing comments,” then many Edsembli fields (OEN, signatures, full attendance) are likely **out of scope**.

---

## H) Options for aligning VGReport with the source note

### H1. Minimal alignment (Kindergarten-first, comment-only)
Focus on:
- Four Frames + Key/Growth/Next Steps
- Comment bank export + copy-to-clipboard workflows
- Plain-language checks and visual “box fit” preview (print/PDF fidelity)

Recommended alignment changes (still Kindergarten-only):

- Make the 12 required inputs first-class: 4 Frames × (Key Learning, Growth, Next Steps)
- Add “soft guardrails” for completeness (heuristics, not hard enforcement), e.g.:
  - “aim for ~3 sentences”
  - “include at least one concrete observation + one growth statement + one actionable next step”
- Prefer box-fit validation over raw character counts (character count remains as a secondary diagnostic)
- Treat board-level layout as config inputs to box-fit (font style, font size such as 12pt, box width/height)
- Support ECE collaboration as structured supporting notes that the teacher can incorporate (teacher remains final author)
- Ensure comment bank templates support placeholders that match common practice (e.g., {Name}, {He/She})
- Keep exports aligned to the SIS entry shape (12-box mapping in the output, consistent encoding/line endings)

Deliberately do **not** model:
- OEN, signatures, attendance, grades

### H2. “Full report card” alignment (larger scope)
If you eventually want VGReport to generate complete provincial report cards, you’ll need:
- Attendance fields
- Program checkboxes
- Elementary/secondary grading systems and learning skills
- Report templates that match official form layouts
- Auditability and policy controls (board rules vary)

---

## I) Follow-ups / validation questions

1. Is VGReport intended to export **only comments** into Edsembli, or to become a full report card system?
2. For elementary (1–8), do we want to support:
   - Learning Skills only?
   - Letter grades + comments?
   - Both?
3. For PII minimization: do we avoid OEN entirely and treat it as SIS-owned data?
4. Should “box fit” be implemented as:
   - character-count heuristics, or
   - real page layout (PDF template) to enforce visual constraints?
