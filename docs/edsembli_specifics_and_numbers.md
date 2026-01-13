---
id: doc.research.edsembli_specifics_and_numbers
type: document
title: Edsembli Specifics and Numbers (Extract)
version: 0.1.0
status: draft
tags: [research, edsembli, requirements, numbers]
refs: []
updated: 2026-01-12
---

# Edsembli Specifics and Numbers (Extract)

Purpose: capture **all explicit specifics and numbers** mentioned in the provided notes:
- “Edsembli Report Card Software Details”
- “Edsembli API Access and Data Options”

This is an extraction document (paraphrased), intended to be easy to quote when defining requirements.

## Sources (saved in repo)

- [sources/edsembli/Edsembli Report Card Software Details.md](sources/edsembli/Edsembli%20Report%20Card%20Software%20Details.md)
- [sources/edsembli/Edsembli API Access and Data Options.md](sources/edsembli/Edsembli%20API%20Access%20and%20Data%20Options.md)

---

## 1) Grade-level reporting structures (fields + scales)

### Kindergarten (Communication of Learning)
- Structure: organized into **Four Frames**
  - Belonging and Contributing
  - Self-Regulation and Well-Being
  - Demonstrating Literacy and Mathematics Behaviours
  - Problem Solving and Innovating
- Required content per frame: **3 subsections**
  - **Key Learning**
  - **Growth in Learning**
  - **Next Steps in Learning**
- Collaboration model: **Teacher + ECE** collaborate; **teacher is final author and signer**
- Anecdotal minimum mentioned: **“minimum of three sentences”** is typical (note: not necessarily a hard rule)

### Grades 1–8 (Elementary Provincial Report Card)
- Achievement scale: **letter grades** = **A, B, C, D, R**
- Per-subject fields: **letter grade + anecdotal comment**
- Learning Skills:
  - Count: **6**
  - Skill names:
    1. Responsibility
    2. Organization
    3. Independent Work
    4. Collaboration
    5. Initiative
    6. Self-Regulation
  - Learning Skills rating scale: **E / G / S / N**
    - E = Excellent
    - G = Good
    - S = Satisfactory
    - N = Needs Improvement

### Grades 9–12 (Secondary Provincial Report Card)
- Achievement scale: **percentage marks**
- Typical weighting mentioned:
  - **70%** = coursework
  - **30%** = final evaluation (examples given: exam, project, culminating task)

---

## 2) “Required” vs “optional” fields (as stated)

### Required fields mentioned (every report card)
- Student **OEN** (Ontario Education Number)
- Attendance data
- **Teacher signature**
- **Principal signature**

### Mandatory program indicators / checkboxes mentioned
- **IEP** (Individual Education Plan)
- **ESL/ELD** (English Language Learner)
- **French immersion/core** program indicators

### Optional/flexible notes
- Teachers have professional judgement over depth/length of anecdotal comments
- Teachers are not required to fill the entire comment box

---

## 3) Space and formatting constraints

### Constraint type
- Limits described as primarily **visual boundaries** (comment box size), not strict character counts

### Admin-configurable parameters mentioned
- Font style
- Font size
  - **12pt** is mentioned as a suggested size for legibility
- Comment box width/height

---

## 4) Parent access and communication expectations

### Parent portal
- Portal name: **Edsembli Connect**
- Parents access: report cards, IEPs, attendance

### Writing standard
- Use “plain language”
- Avoid technical jargon (“edu-babble”)

### Response time expectation mentioned
- Respond to parent concerns/questions within **2 business days**

### Catholic integration (qualitative)
- Reports may include reflections aligned to Catholic Graduate Expectations / faith-based values

---

## 5) Platform modules and tracked data (coverage)

### Core tracked categories mentioned
- Attendance: **days absent**, **times late**
- Achievement: **subject-specific grades**
- Narrative: **anecdotal comments**
- Learning Skills: “specialized learning skills” (i.e., separate from subject marks)

### Productivity features mentioned
- Comment banks exist at: **board / school / individual teacher** level
- Comment placeholders mentioned:
  - `{Name}`
  - `{He/She}`
- Batch actions:
  - Apply the same comment or grade to a group, then customize individual entries

### Compliance feature mentioned
- Audit logs: track who accessed/changed records (PHIPA/MFIPPA compliance cited)

### Data collection feature mentioned
- Digital verification: replace September paper verification workflows

---

## 6) API standards, protocols, and authentication (integration)

### API standards/protocols mentioned
- **OneRoster API**
  - Version mentioned: **1.1** (typical)
- **OData/REST APIs** for Finance/HRP
  - Finance/HRP platform mentioned: **Microsoft Dynamics 365 Business Central**
  - Supports standard CRUD operations (Create/Read/Update/Delete)
- “Web services” mentioned for specific exchanges
  - Example mentioned: “Xello Data Exchange” module

### Authentication mentioned
- OAuth standard mentioned: **OAuth 2.0**
- SSO/integration targets mentioned: Google Cloud Platform (and Microsoft integrations)

### Credentials / configuration specifics mentioned
- OneRoster:
  - Each tenant (school board) has a unique **apikey**
  - Admin setup detail: create a generic staff record named **`oneroster`** and link a unique vendor username
- OAuth:
  - Credentials: **Client ID** and **Client Secret**
  - Entered in Edsembli WebAdmin under:
    - **Setup > Email Settings** or
    - **Security**

### OneRoster documentation/testing URL mentioned
- `https://oneroster.edsemblicloud.com/swagger/index.html`

---

## 7) Import/export formats and “where” (data options)

### Exporting reports
- Formats mentioned: **CSV, PDF, XML**
- UI locations mentioned:
  - “Quick Reports” tile
  - “Data Mining” views
  - Student Reports section

### Importing marks
- Formats mentioned: **MWM**, **CSV**
- MWM described as: “Maplewood Format” (comma-delimited with specific quoting rules)

### OnSIS submissions
- Formats mentioned: **XML**, **CSV**
- Notes: batch files typically generated in XML for ministry uploads

### General imports (via partner integrations)
- Formats mentioned: **CSV, TSV, XML, JSON**

### Custom integrations
- Mentioned option: paid professional service for custom integrations

---

## 8) Implications for VGReport (non-implementation notes)

This extraction contains multiple items that imply substantially different scopes:
- “Full report card” scope: OEN, attendance, signatures, subject grades, learning skills, official layouts
- “Comment authoring tool” scope: narrative generation/preview/export for SIS entry

Keep this list as raw source facts; decide scope separately.
