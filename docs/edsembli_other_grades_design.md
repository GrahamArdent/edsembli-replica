---
id: doc.design.edsembli_other_grades
type: document
title: Edsembli Other Grades (1–8, 9–12) — Design Capture
version: 0.1.0
status: draft
tags: [design, edsembli, requirements, report_cards, elementary, secondary]
refs:
  - doc.research.edsembli_specifics_and_numbers
  - doc.research.edsembli_report_card_requirements_vs_vgreport
updated: 2026-01-12
---

# Edsembli Other Grades (1–8, 9–12) — Design Capture

Purpose: a **design reference** capturing what “other grades” (beyond Kindergarten CoL) look like in the provided Edsembli notes, so we can align later if scope expands.

This is not implementation work.

## Sources (saved in repo)

- [sources/edsembli/Edsembli Report Card Software Details.md](sources/edsembli/Edsembli%20Report%20Card%20Software%20Details.md)
- [sources/edsembli/Edsembli API Access and Data Options.md](sources/edsembli/Edsembli%20API%20Access%20and%20Data%20Options.md)
- [docs/edsembli_specifics_and_numbers.md](docs/edsembli_specifics_and_numbers.md)

---

## 1) Cross-grade “form” characteristics (applies to 1–8 and 9–12)

### 1.1 Live form editing (WYSIWYG)

- Teachers input data into a digital form that looks like the final printed report card.
- Practical consequence: the system should provide **real-time box fit feedback** (not “submit to check”).

### 1.2 Space constraints

- Limits are described as **physical box constraints**, not strict character counts.
- Board-level configuration parameters mentioned:
  - Font style
  - Font size (12pt suggested)
  - Comment box width/height

### 1.3 Required fields and indicators (if generating “full” report cards)

The source note describes these as required/mandatory on report cards:

- Student OEN
- Attendance data (days absent, times late)
- Teacher signature
- Principal signature
- Program indicators / checkboxes:
  - IEP
  - ESL/ELD
  - French immersion/core

Design implication: if we ever expand beyond “comment-only export”, these fields need clear ownership rules (SIS-owned vs app-owned) and strong privacy posture.

### 1.4 Teacher efficiency features

- Comment banks (board/school/teacher)
- Placeholders like {Name} and {He/She}
- Batch actions (apply to group, then customize)

### 1.5 Governance/compliance features

- Audit logs (who accessed/changed records)
- Digital verification workflows for parent-updated info (described as replacing “September paper flood”)
- Parent portal access expectations (Edsembli Connect mentioned)

---

## 2) Grades 1–8 (Elementary Provincial Report Card) — What the form needs

### 2.1 Achievement per subject

- Achievement scale: A, B, C, D, R
- Per-subject fields:
  - Letter grade
  - Anecdotal comment

Design capture:
- The form is naturally modeled as a **subject list/table**, where each row has (grade, comment).
- “Live form” constraints imply each subject comment field needs a fit indicator against its printed box.

### 2.2 Learning Skills block

- There are 6 learning skills:
  1. Responsibility
  2. Organization
  3. Independent Work
  4. Collaboration
  5. Initiative
  6. Self-Regulation
- Learning skills rating scale: E (Excellent), G (Good), S (Satisfactory), N (Needs Improvement)

Design capture:
- This is best represented as a **fixed grid**:
  - Rows = the 6 skills
  - Cells = term rating (E/G/S/N)
- Provide fast keyboard entry and a “missing ratings” checklist.

### 2.3 Elementary workflow expectations (implied)

- Batch actions matter more because the number of fields grows quickly (multiple subjects + 6 learning skills).
- Comment bank selection + personalization becomes essential to speed.

---

## 3) Grades 9–12 (Secondary Provincial Report Card) — What the form needs

### 3.1 Achievement per course

- Achievement scale: percentage mark

Design capture:
- The form is naturally modeled as a **course list/table**, where each row has (percent, optional comment if required by board/course).

### 3.2 Weighting (typical)

- A “typical” weighting described:
  - 70% coursework
  - 30% final evaluation (exam/project/culminating task)

Design capture:
- At minimum, treat this as a displayable rubric/metadata reference tied to the course.
- If implementing later, clarify whether the app is expected to store:
  - the 70/30 split as data (editable per course), or
  - the final computed percent only (with weighting owned by the markbook/SIS).

---

## 4) Export/integration alignment (later-scope design notes)

If we later align beyond Kindergarten, integrations and exports likely need to handle:

- Rosters and enrollments (OneRoster 1.1 mentioned)
- Grade synchronization (pull/push marks/comments between tools and SIS)
- Attendance data export (days absent, times late)
- Bulk imports/exports:
  - Reports: CSV/PDF/XML
  - Marks import: MWM/CSV
  - OnSIS submissions: XML/CSV
  - General imports: CSV/TSV/XML/JSON

Design capture: keep “export shape” consistent with how teachers fill the form (subject rows, learning skills grid, course rows).

---

## 5) Open decisions to resolve before implementation

- Scope boundary: comment-only tool vs full report-card generator
- Ownership of PII-heavy and compliance fields (OEN, attendance, signatures): SIS-owned vs app-owned
- Board variability: how much is configurable (fonts/box sizes) and where those configs live
- Fidelity target: heuristic fit vs actual rendered PDF layout for box-fit validation
