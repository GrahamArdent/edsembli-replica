---
id: doc.vgreport.frontend_design
type: document
title: VGReport – Frontend User Experience Design
version: 0.6.0
status: draft
tags: [technical, governance]
refs: []
updated: 2026-01-12
product_name: VGReport
license: Open Source (MIT)
---

# VGReport: Frontend Design Strategy

This is the UX and architecture design spec for VGReport.

Implementation tracking lives in:
- `docs/frontend_gameplan.md`

## 1. Design Philosophy
For a single-user kindergarten teacher, the application must function as a **"Pedagogical Cockpit."** It should not merely be a form-filler; it should be a **thinking partner** that guides the teacher from observation to formal reporting without administrative friction.

### Core UX Pillars
1.  **Cognitive Offloading**: Teachers hold too much in their heads. The UI must visualize the structure (Frames, Sections) so the teacher doesn't have to remember it.
2.  **Live Validation**: as described in the original "Edsembli" analysis, the "Live Form" concept is critical. Feedback on length, tone, and constraints must be instantaneous (no "Submit to check errors").
3.  **Context Preservation**: When switching between "Belonging" and "Math," the context of the specific student (name, pronouns, needs) must remain anchored on screen.

---

## 2. Gap Analysis: What the Initial Design Missed

### Critical Gaps Identified

| Gap | Impact | Resolution |
|-----|--------|------------|
| **Offline-First** | Teachers often work in classrooms with unreliable WiFi, on buses, or at home without internet. A server-dependent app will frustrate them. | App must function 100% offline with local data storage. |
| **Data Persistence** | Where do student drafts live? The initial design didn't specify. Loss of work = major trust damage. | Local SQLite database or JSON files with explicit "Save" feedback. |
| **Autosave** | Teachers don't think about saving. They expect Google Docs-style resilience. | Implement debounced autosave (every 2 seconds of inactivity) with visual indicator. |
| **Multi-Term Reports** | Kindergarten has 3 reporting periods: Initial Observations (Fall), Communication of Learning (Feb), and Final (June). | Data model must support `report_period` per student, with ability to copy/reference prior terms. |
| **Print/PDF Export** | The final artifact is a *printed* or *PDF* report card, not a screen. | Dedicated "Print Preview" mode with proper page-break handling and PDF generation. |
| **Observation Library** | Teachers reuse evidence snippets. "She counts to 20" might apply to Math *and* Problem Solving. | Personal "Evidence Bank" with tagging and search, separate from templates. |
| **Undo/Redo** | Accidental deletions happen. | Command pattern history stack (Ctrl+Z / Ctrl+Y). |
| **Keyboard Shortcuts** | Power users (experienced teachers) want speed. Tab between fields, Ctrl+S to save, etc. | Full keyboard navigation and shortcut system. |
| **Accessibility** | Teachers may have visual impairments or use screen readers. | WCAG 2.1 AA compliance as a baseline. |
| **Dark Mode** | Long evening writing sessions cause eye strain. | System-preference detection + manual toggle. |

### Secondary Gaps (Nice-to-Have)

| Gap | Resolution |
|-----|------------|
| Mobile/Tablet Support | Responsive design for iPad use during parent conferences. |
| Spell Check | Integration with browser/OS spell check + custom "edu-babble" dictionary. |
| Collaboration Indicators | Even for single-user, show "Last edited: Jan 11, 2026 at 3:45pm". |
| Backup/Restore | Export entire classroom data as a `.zip` for backup. |

---

## 3. Technology Stack Re-Evaluation

## 3A. Pre-Implementation Blockers & Prerequisites

### Blockers (must resolve before starting Phase 1)

| Item | Status | Why it matters | Action |
|------|--------|----------------|--------|
| **Rust toolchain** (`rustc`, `cargo`) | Installed via `winget` (Rustup). `rustc 1.92.0`, `cargo 1.92.0`, `rustup 1.28.2` | Required to build the Tauri desktop shell. | Restart terminal/VS Code so PATH includes `%USERPROFILE%\.cargo\bin`, then verify `rustc --version` and `cargo --version`. |
| **WebView2 Runtime (Windows)** | Unknown | Tauri uses the system WebView (Edge WebView2) for rendering. If missing, the app won’t launch for some users. | **Decision**: target **Evergreen WebView2**; installer/first-run must detect and install if missing (bundle offline installer for restricted environments). |

### Non-blocking prerequisites (recommended)

| Item | Why it matters | Action |
|------|----------------|--------|
| **Node.js** | Needed for Vite/React tooling. | Already installed; keep to an LTS line (18+). |
| **Python packaging toolchain** | Needed to ship the engine without requiring Python installed on teacher machines. | Plan to bundle a Python sidecar binary (see Section 3B). |

### Decisions (locked)

| Topic | Decision | Rationale |
|-------|----------|-----------|
| WebView runtime | **Evergreen WebView2** (default requirement) | Best security/update story and smallest VGReport footprint; avoids owning patch cadence. |
| Runtime fallback | Bundle **offline Evergreen installer** option | Supports schools with restricted internet or device management constraints. |

## 3B. Architectural Gap: Packaging the Python “Engine”

The plan currently assumes the React UI can “call Python”. In a production desktop build, **we must ship a standalone engine binary**; we cannot rely on a teacher having the right Python version and packages.

**Recommendation**: Build a dedicated `vgreport-engine` executable using **PyInstaller** (or similar) and ship it as a Tauri sidecar.

Key decisions to make before implementation:
- **Sidecar interface**: Choose IPC mechanism (stdin/stdout JSON protocol is simplest) and lock the message schema.
- **Dependency footprint**: Confirm the engine’s dependencies (e.g., `duckdb`, `ruamel.yaml`, `rich`) and whether any are optional.
- **Encoding**: Ensure UTF-8 output consistently (we already saw Windows encoding pitfalls in tests).

## 3C. Architectural Gap: Type Synchronization (Python ↔ UI)

We have schemas/models and validations in Python, but the UI will be TypeScript. If we don’t enforce a shared contract, we will get drift (UI expects slots that backend doesn’t provide, etc.).

**Recommendation**: Make **JSON Schema the source of truth** for request/response contracts and use them to generate TypeScript types.

### Current Codebase Reality

The existing engine uses **`@dataclass`** (not Pydantic) for core types like `AssemblyRequest` and `AssemblyResult`. Rather than migrating all code to Pydantic, we will:

1. **Hand-write JSON Schema files** for the IPC contract (see Section 3D below).
2. **Generate TypeScript types** from those schemas using `json-schema-to-typescript`.
3. **Validate at runtime** in the sidecar using a lightweight JSON Schema validator (e.g., `jsonschema` package).

This approach avoids a large refactor while still ensuring type safety across the boundary.

Practical options:
- **JSON Schema (chosen)**: export JSON Schemas for templates/requests/responses and generate TS.
- **FastAPI/OpenAPI (defer)**: adopt only if we later add an HTTP API for cloud sync or third-party integration.

### Contract policy (how we prevent drift)

1. **JSON Schema is the source of truth** (hand-maintained in `/contracts/`).
2. A script generates **TypeScript types** from those schemas into `vgreport/src/contracts/`.
3. CI fails if generated TS files are out of date with the schema.
4. Python sidecar validates incoming requests against the schema at runtime.

This keeps VGReport stable even as templates/slots evolve.

---

## 3D. IPC Protocol Specification

The React frontend communicates with the Python sidecar via **stdin/stdout JSON messages**. This section defines the wire protocol.

### Message Format

All messages are newline-delimited JSON (NDJSON). Each message has a standard envelope:

```json
// Request (Frontend → Sidecar)
{
  "id": "uuid-v4",
  "method": "render_comment",
  "params": { ... }
}

// Response (Sidecar → Frontend)
{
  "id": "uuid-v4",
  "result": { ... },
  "error": null
}

// Error Response
{
  "id": "uuid-v4",
  "result": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required slot: evidence",
    "details": { "slot": "evidence" }
  }
}
```

### Supported Methods

**Current implementation status (repo reality):** the sidecar currently implements `health`, `list_templates`, `get_template`, `render_comment`, and `debug_info`.
Methods like `validate_comment` and `get_evidence_matrix` remain planned work.

| Method | Description | Params | Result |
|--------|-------------|--------|--------|
| `list_templates` | Get all available templates | `{ board_id, frame?, section? }` | `{ templates: Template[] }` |
| `get_template` | Get a single template by ID | `{ template_id }` | `{ template: Template }` |
| `render_comment` | Render a comment with slot values | `{ template_id, slots: Record<string, string> }` | `{ text, char_count, validation }` |
| `validate_comment` | Validate without rendering | `{ text, frame, section }` | `{ valid, errors[], warnings[] }` |
| `get_evidence_matrix` | Get evidence requirements | `{ board_id }` | `{ matrix: EvidenceMatrix }` |
| `health` | Check sidecar is running | `{}` | `{ status: "ok", version }` |

### Type Definitions (JSON Schema)

Schemas will be stored in `/contracts/` and versioned:

```
contracts/
├── ipc-request.schema.json
├── ipc-response.schema.json
├── template.schema.json
├── render-params.schema.json
└── validation-result.schema.json
```

### Encoding

- All messages MUST be UTF-8 encoded.
- The sidecar MUST set `PYTHONIOENCODING=utf-8` and use `encoding="utf-8"` for all I/O.
- Windows: sidecar launch must include environment variables to force UTF-8 (learned from E2E test issues).

### Startup Handshake

1. Frontend spawns sidecar process.
2. Frontend sends `{ "method": "health", "id": "init" }` and waits up to 5 seconds.
3. Sidecar responds with `{ "id": "init", "result": { "status": "ok", "version": "1.0.0" } }`.
4. If no response, frontend shows error: "Engine failed to start."

---

### The Core Question: Web App vs. Desktop App?

For a **single-user, local-first** teacher tool, the "React + FastAPI" approach has a significant drawback: **it requires running a server**. The teacher would need to:
1. Open a terminal or click a script.
2. Wait for FastAPI to start.
3. Open a browser.

This is acceptable for developers but **awkward for teachers**. A native desktop app (double-click to launch) is superior UX.

### Technology Options Compared

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **React + FastAPI (Web)** | Industry standard, easy to develop, full React ecosystem. | Requires server, not truly offline, no native feel. | ⚠️ Acceptable for MVP |
| **Electron + React** | Native desktop app, offline-first, file system access. | Heavy (150MB+), memory hog, security concerns. | ❌ Overkill |
| **Tauri + React** | Lightweight native app (10MB), Rust security, can spawn Python sidecar. | Newer ecosystem, Rust knowledge helpful. | ✅ **Best for Production** |
| **PyWebView + React** | Pure Python deployment, embeds browser, direct Python calls. | Limited to what PyWebView supports, less polished. | ⚠️ Acceptable if Tauri is too complex |
| **SvelteKit** | Simpler than React, excellent DX, smaller bundle. | Smaller ecosystem, less hiring pool. | ⚠️ Consider if team prefers |

### Recommended Stack: **Tauri + React + TypeScript**

**Why Tauri?**
1. **Native Experience**: Double-click `KinderReport.exe` and it opens. No server, no browser tab.
2. **Tiny Footprint**: ~10MB installer vs. Electron's 150MB+.
3. **Offline-First by Design**: All data lives on the local filesystem.
4. **Python Sidecar**: Tauri can spawn your existing Python logic as a background process and communicate via IPC.
5. **Security**: Rust-based backend is inherently safer than Electron's Node.js.
6. **Future Proof**: Can later add auto-update, system tray, native notifications.

**The Architecture**:
```
┌─────────────────────────────────────────────────────────┐
│                    Tauri Shell (Rust)                   │
│  ┌───────────────────────┐  ┌────────────────────────┐  │
│  │   React Frontend      │  │   Python Sidecar       │  │
│  │   (TypeScript)        │◄─┤   (edsembli engine)    │  │
│  │                       │  │                        │  │
│  │   - UI Components     │  │   - Template logic     │  │
│  │   - State (Zustand)   │  │   - Slot rendering     │  │
│  │   - Local Storage     │  │   - Validation         │  │
│  └───────────────────────┘  └────────────────────────┘  │
│                         ▲                               │
│                         │ IPC (JSON)                    │
│                         ▼                               │
│              ┌─────────────────────┐                    │
│              │  SQLite Database    │                    │
│              │  (students, drafts) │                    │
│              └─────────────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

---

## 4. The User Journey (Revised)

### Phase 0: Installation
*   Teacher downloads `VGReport-Setup.exe` (Windows) or `.dmg` (Mac).
*   Double-click to install. No Python, no Node, no dependencies for the user.

### Phase 1: First Launch ("Onboarding Wizard")
1.  **Welcome Screen**: "Let's set up your classroom."
2.  **Board Selection**: Dropdown: "Which school board are you part of?" (TCDSB, NCDSB, etc.)
3.  **Roster Import**: Drag-and-drop a CSV or manually add students.
4.  **Reporting Period**: "Which report are you working on?" (Initial Observations / February / June)
5.  **Done**: "You're ready to start writing!"

### Phase 2: The "Writing Session" (The Core Loop)
1.  **Select Student**: Sidebar shows roster with progress indicators.
2.  **Select Frame**: Horizontal tabs: [Belonging] [Self-Reg] [Literacy/Math] [Prob Solving]
3.  **Compose Each Section**:
    *   For each of "Key Learning", "Growth", "Next Steps":
        *   Pick a template from a searchable dropdown.
        *   Fill in the "slot questions" (evidence, change, goal, etc.)
4.  **Watch the Preview**: Right panel updates in real-time.
5.  **Autosave**: Green checkmark pulses every time data is saved.

### Phase 3: Finalization & Export
1.  **Review All**: A "Summary View" shows all students and their completion status.
2.  **Export Options**:
    *   "Export to PDF" (formatted like the official Ontario form)
    *   "Export to CSV" (for SIS import)
    *   "Copy to Clipboard" (for pasting into Edsembli manually)
3.  **Archive**: Mark the reporting period as "Complete". Data is locked but viewable.

---

## 4A. Teacher Workflow Modes (Elementary vs. Secondary)

Teachers do not all write reports the same way. VGReport must support multiple valid workflows without forcing a single mental model.

### Teacher contexts

**Elementary (homeroom-style)**
- Primary organizing unit is typically a single class roster.
- Writing tends to be **student-by-student** (maintaining narrative cohesion per student).
- Success looks like: steady “next student” momentum + parent-facing, consistent exports.

**Secondary (period-based)**
- Primary organizing unit is **period/class** (multiple groups).
- Writing often alternates between **student-by-student** and **section-by-section** (batching by topic).
- Success looks like: strong scoping + progress visibility (“who’s left in Period 3?”) + batch exports.

**Design principle:** one product, two contexts. Defaults and emphasis can adapt based on whether the teacher is working with one roster or multiple class groups.

### Core concept: Class/Cycle as the “working context”

The app should keep “where am I?” obvious and stable by showing (and keying drafts under):
- **Class / Period** (elementary: often one; secondary: many)
- **Cycle** (term/quarter/semester/reporting period)

This context should drive draft scoping, progress calculations, and export defaults.

### Two primary writing modes (both supported)

Because teachers may prefer different approaches at different times, VGReport should support both modes and allow frictionless switching.

**Mode A — Student Flow (finish one student at a time)**
- Optimized for linear progression: **Next / Previous Student**, mark complete, quick flags.
- Preview is a first-class tool for tone/length and export fidelity.

**Mode B — Section Flow (batch by section across many students)**
- Optimized for batching: choose a section (e.g., Math) and move student-to-student within that section.
- Fast insertion and variation tools are emphasized (rubric phrases, starters, quick adjustments).

**Switching principle:** switching modes must not reset or fork data; it changes layout, shortcuts, and default navigation only.

### Export Center (support preference without chaos)

Export is a high-stakes moment and must be predictable. Provide an explicit **Export Center** with saved presets:
- **PDF per student** (export a folder)
- **Combined PDF** (one file)
- **CSV** (SIS import)
- **Copy to clipboard** (for pasting into other systems)

Each preset should store per-class/per-cycle settings (naming conventions, included sections, formatting style).

### Writing style support (individualized AND standards-based)

Support both "compose" (individual narrative) and "assemble" (standards/rubric phrases):
- **Rubric phrase library** (tagged by section + proficiency + tone)
- **Teacher scratchpad/observations** per student (not exported)
- **Repetition guardrails**: detect reused sentences across many students and suggest variation

### Progress + work queue

Teachers need to know “what’s left” at the right level:
- Per-student completion (not started / in progress / needs review / complete)
- Per-class progress (“22/28 complete”) and optionally per-section coverage
- A **Work Queue** view: Incomplete, Flagged, Needs Review, Recently edited

### Keyboard-first productivity

Prioritize a keyboardable core loop:
- Quick student switch/search
- Next/prev student (student flow)
- Next/prev student within current section (section flow)
- Fast open for Export Center and Settings

### Recommendations (high-ROI v1 workflow upgrades)

If we need to pick a small set of improvements with outsized impact:
1. **Class/Cycle selector** as a stable working context.
2. **Two writing modes** (Student Flow / Section Flow) with seamless switching.
3. **Completion + Work Queue** (progress at student + class levels).
4. **Export Center with presets** (PDF per student, combined PDF, CSV, clipboard) + saved settings.
5. **Rubric phrase library** + light repetition warnings (to balance speed and authenticity).

---

## 4B. Kindergarten-Specific Considerations

VGReport v1 is designed for **Ontario kindergarten teachers**. This section captures UX considerations specific to that context.

### The kindergarten reality

- 20–30 children, same teacher all day, play-based learning
- Usually team-taught with an ECE (Early Childhood Educator)
- Three formal reporting periods: Initial Observations (Fall), Communication of Learning (February), Final (June)
- Reports are **narrative**, not grades—very personal, parent-facing
- Evidence comes from play: "during block play," "at the water table," "during outdoor exploration"

### How kindergarten teachers actually work

- Observations happen *during* class, often scribbled on sticky notes or typed on a phone
- Writing happens in 40-minute prep blocks, after school, or weekends (exhausted, on the couch)
- Mental model: "What did I notice about this kid?" → "What does that mean for their development?"
- Worries: sounding repetitive, getting pronouns wrong, parents comparing reports

### Gaps in the current design (kindergarten lens)

| Gap | Why it matters | Ideas |
|-----|----------------|-------|
| **No observation capture workflow** | Teachers arrive with sticky notes, not structured evidence. The current design assumes evidence is ready. | Quick-capture mode with timestamp + context (block play, snack, outdoor). Per-student "evidence drawer" that accumulates throughout the term. |
| **No term-to-term continuity** | Teachers need to reference Fall when writing February/June. Growth language depends on prior state. | "Compare to Fall" panel. "Copy from prior term and adjust" workflow. Growth trajectory visualization (Fall → Feb → June). |
| **ECE collaboration missing** | Kindergarten is team-taught. ECE observations are valuable but currently have no place. | "ECE observations" field per student (not exported). "Shared notes" for team discussions. Future: invite ECE to contribute directly. |
| **Developmental language not surfaced** | Kindergarten phrasing is specific: "beginning to," "with support," "independently," "consistently." | Developmental modifier picker. Frame-specific language banks. Auto-suggest modifiers by term (Fall = more "beginning to"). |
| **Parent audience not explicitly designed for** | The primary reader is a parent, not administrator. | Reading level indicator. Tone check (encouraging? specific?). "Parent view" preview. Jargon detector ("emergent literacy" → "learning to read"). |
| **No support for students needing different handling** | IEP, ELL, mid-year arrivals need different treatment. | Per-student flags (IEP, ELL, New arrival). IEP-aware templates. "More space needed" indicator. |
| **No emotional support for the teacher** | Writing 25 deeply personal reports is exhausting. The UI feels clinical. | Gentle encouragement ("12 done—halfway there!"). "Take a break" prompt after 45 min. Session summary. Option to hide progress pressure. |

### Workflow ideas that match kindergarten mental models

**Observation-first flow (alternative to template-first)**

Instead of: Pick template → Fill slots

Consider: Review observations → Select relevant ones → Generate comment

This matches how teachers think: "What did I notice about Aiden?" → "He's really into the water table and started sharing better."

**"Story arc" view per student**

Kindergarten reports tell a developmental story. Teachers want to see the arc:
- Fall: "Aiden is beginning to share materials during play."
- February: "Aiden now shares materials with prompting."
- June: "Aiden independently shares and takes turns with peers."

A timeline/arc view helps teachers write with continuity.

**Play context selector**

Instead of a generic "observation" slot, offer context-aware prompts:
- Block area / Dramatic play / Art / Sensory / Outdoor / Snack / Circle
- Each context has typical observations: "Block area → building, collaborating, problem-solving"

**"Write once, personalize many" for common observations**

Some observations apply to multiple students with minor tweaks:
- Write a base comment
- Apply to students with auto-personalization (name, pronouns)
- Edit individually as needed

### What kindergarten teachers would say about the current design

**Positive:**
- Three-pane layout makes sense (roster, editor, preview)
- Frame tabs match Ontario kindergarten structure
- Autosave is essential—they will love this
- Character count helps (boards have limits)

**Concerns:**
- "Where do I put my observations before I write?"
- "How do I see what I wrote in Fall when I'm writing February?"
- "What about my ECE's observations?"
- "Can I see this one kid's whole story across the year?"
- "I don't want to pick a template—I want to describe what I saw and have it help me write"
- "What if I want to write the same thing for 5 kids who all did the same thing?"

### Recommendations: Kindergarten-focused v1 additions (high ROI)

If narrowing to kindergarten for v1, prioritize:

1. **Observation capture mode** — quick add, timestamped, context-tagged, per-student drawer
2. **Term continuity view** — side-by-side Fall/Feb/June for current student
3. **Developmental language bank** — modifiers + frame-specific phrases + auto-suggestion by term
4. **ECE notes field** — text area per student (not exported)
5. **Gentle progress + session awareness** — encouragement, break prompts, session stats

These align with how kindergarten teachers actually work, without changing the core architecture.

---

## 4C. Comprehensive Workflow Brainstorming (Raw Notes)

This section captures the full thinking process for UX improvements. These are not all prioritized or validated—they're brainstorming notes to be refined later.

### Teacher workflow lens (what they're actually trying to do)

**Core mental model:**
- "I have 30 kids, 6 periods (or one class all day), and a deadline. I need to get from roster → meaningful comments → export without thinking about the tool."
- Their mental model: pick class/period → pick student → fill in recurring categories → review tone/length → export.

### High-leverage workflow improvements (no big architecture change)

**Class/period-first navigation**
- Make "Period" or "Class" the primary selector (top-left), and treat roster as scoped to that period by default.
- Teachers think in periods (secondary) or single class (elementary), not global rosters.
- Current design doesn't make "where am I?" obvious enough.

**Student progression mode**
- Add "Next student / Previous student" controls + keyboard shortcuts.
- Optional "Auto-advance after save" toggle.
- The fastest workflow is linear: next → write → save → next.

**Completion visibility**
- Per-student completion indicator: "3/5 sections filled", char count status.
- Period-level progress bar: "22/28 students complete".
- Teachers want to know "who's left?" at a glance.

**Quick filters**
- "Incomplete only", "Needs review", "Flagged", "Recently edited".
- Reduces cognitive load late in the cycle when most students are done.

### Drafting + writing quality (teacher tone + consistency)

**Comment intent helpers**
- Lightweight tone toggles: "Encouraging / Neutral / Firm" that adjust template phrasing.
- Even if it's just guidance + suggested starters, this helps teachers maintain appropriate tone.

**Rubric-based starters**
- Many teachers start from rubric language (Ontario curriculum expectations).
- A "rubric phrases" drawer (per section) would speed writing without sounding robotic.
- Tag phrases by proficiency level: Beginning / Developing / Proficient / Extending.

**Variation guardrails**
- Warn when the same phrase appears across many students.
- Teachers worry about copy/paste optics ("Did the teacher just use the same comment for everyone?").
- Even a "reused text" indicator ("Used in 12 students") is helpful.
- Optional: "suggest variations" helper (deterministic swaps, not AI).

**Read-aloud preview**
- Preview should mimic final export (line breaks, headings, spacing).
- Highlight missing sections or over-limit sections.
- Some teachers read reports aloud to catch awkward phrasing—support this mentally.

### Data-entry ergonomics (reduce friction)

**Faster add/edit student**
- Inline add at top of roster (no modal).
- Keep focus in the keyboard flow.
- Avoid modal-heavy CRUD when entering many names (e.g., importing from a list).

**Smarter defaults**
- Remember last-selected template per section/per period.
- Remember last student; reopen where they left off.
- "Resume session" on app launch.

**Bulk actions**
- Import roster CSV (even minimal: name, pronouns).
- Bulk delete/merge duplicates.
- Bulk assign default templates to a period.

### Error prevention + confidence

**Autosave transparency**
- Make save state unmissable but calm: "Saved 2s ago".
- Add "Last saved" timestamp per draft and per student.
- Visual indicator that doesn't distract (subtle pulse, not flashing).

**"Export readiness" checklist**
- Before export, show blockers:
  - Missing students
  - Empty required sections
  - Over/under length
- Show warnings:
  - Tone inconsistency
  - Repeated phrases
- "You're ready to export" confirmation when clean.

**Undo safety**
- Teachers will experiment with phrasing—make undo/redo obvious.
- Scoped undo (per field, not just global).
- "Restore previous version" per student (mini version history).

### Export workflow (where teachers lose time)

**Export presets**
- "End-of-term PDF", "CSV for SIS", "Copy to clipboard".
- Saved settings per school (columns, separators, naming).
- Don't make them configure export every time.

**File naming conventions**
- Default to `Period - StudentLast, StudentFirst - Term.pdf`.
- Or a batch naming scheme the teacher configures once.
- Teachers care about sorting and findability.

**Batch export**
- Export all students in a period to a folder (PDF per student).
- Plus a combined PDF (all students in one file).
- This is often the real need for secondary teachers.

### Accessibility + keyboard-first

**True keyboard loop**
- `Ctrl+K` quick switch student.
- `Ctrl+Enter` commit section.
- `Alt+N/P` next/prev student.
- `Ctrl+,` settings.
- Teachers often work fast on a keyboard; mousing slows them down.

**Focus + tab order**
- Ensure predictable tabbing: student list → section tabs → fields → preview actions.
- No "focus traps" or weird jump behavior.

**Better labels**
- Replace placeholder-only inputs with proper labels.
- Helps screen readers and reduces entry mistakes.
- Current design uses placeholders—not accessible.

### Information architecture ideas (if you want a slightly bolder UX)

**"Roster" vs "Work Queue"**
- Two modes:
  - Roster is the database (all students, all time).
  - Work Queue is the editing session (today's period, incomplete students).
- This matches teacher thinking: "Who do I need to write about today?"

**Split preview modes**
- "Student view" (what prints).
- "Teacher view" (editing aids: missing markers, suggested starters, rubric notes).
- Toggle between them.

**Session-based workflow**
- "Start Term" wizard:
  1. Import roster
  2. Pick sections
  3. Set templates
  4. Define char targets
  5. Then you're in production mode.
- Onboarding that sets everything up correctly.

### Questions to sharpen priorities (pick the best 3–5 changes)

**Question 1: Do teachers typically write comments student-by-student or section-by-section?**
- Answer: BOTH (hence dual mode support).
- Student-by-student: maintains narrative cohesion (elementary).
- Section-by-section: batching efficiency (secondary, large rosters).

**Question 2: Is the primary output PDF per student, one combined PDF, or CSV into an SIS?**
- Answer: ALL THREE (hence Export Center with presets).
- PDF per student: for filing/printing.
- Combined PDF: for review/backup.
- CSV: for SIS import.

**Question 3: Are comments expected to be highly individualized or more standards-based (rubric phrases)?**
- Answer: BOTH (hence rubric library + personalization tools).
- Individualized: narrative, observation-based (kindergarten).
- Standards-based: curriculum alignment, rubric phrasing (upper grades).

### Elementary vs secondary structure insight

**Elementary (homeroom):**
- Kids don't have different teachers throughout the day.
- They stay in the same class with the same teacher.
- Mental model: "my class" (singular).
- Navigation priority: student list, not period switching.

**Secondary (period-based):**
- Students rotate through 4–8 teachers per day.
- Teacher sees 100–150 students across periods.
- Mental model: "Period 3 English" (multiple classes).
- Navigation priority: period/class selector, then student.

**Design implication:**
- Onboarding/settings should ask "Elementary vs Secondary" (or detect by whether periods/classes are defined).
- Default entry point changes: elementary lands on student list, secondary lands on period selector.
- But features stay the same—just different emphasis.

### Additional kindergarten-specific workflow ideas (beyond section 4B)

**Pronouns complexity**
- Kindergarten teachers are hyper-aware of pronouns (they/them is common, misgendering is a big mistake).
- Pronoun picker should be visible and obvious: He/Him, She/Her, They/Them, custom.
- Auto-populate across all templates once set.

**Photo/artifact reference**
- Teachers sometimes photograph student work or play interactions.
- "Attach photo" to an observation (not exported, just for teacher memory).
- Later: "What was that photo from block play?" → jogs memory.

**"Compare to last year" (long-term context)**
- Some teachers have the same students multiple years (JK → SK).
- "View last year's report" button (if available).
- Helps with long-term growth language.

**Parent conference prep mode**
- Export "conference notes" (not the full report).
- Bullet points, specific examples, talking points.
- Teachers need both the formal report and informal notes for parent meetings.

**Mid-year arrival handling**
- Students join mid-term.
- Need a "started in February" flag.
- Adjust templates to acknowledge limited observation period: "Since joining our class in February, Aiden has..."

---

## 4D. Senior UX Review: The "Kindergarten Logic"

*Critique and refinement from a Senior Product Design lens, specifically targeting the "Kindergarten Teacher" persona.*

### Critique: The "Synthesis Gap"
The current design (Observation Capture → Template → Report) skips the messy middle step: **Synthesis**.
- **The Problem**: Teachers don't just "plug observations into templates." They stare at a pile of sticky notes (mental or physical) and try to find a pattern. "He played with blocks... he shared the truck... he counted to 5." → *Synthesis*: "He is demonstrating structural awareness and pro-social behavior."
- **The Fix**: We need a **"Staging Area" or "Drafting Board"** view.
    - **Left Pane:** A pile of "Observation Cards" for that student (collected over the term).
    - **Right Pane:** The Report Editor.
    - **Interaction:** Drag an observation card into the editor, and it *suggests* the relevant frame/sentence.
    - **Why:** This mirrors the cognitive process of "sorting the evidence."

### Critique: Visuals are the Anchor
Kindergarten is highly visual. Teachers remember *images*, not text dates.
- **The Problem**: A list of text observations ("Jan 12: Block play") is high cognitive load.
- **The Fix**: **Visual Evidence Anchors**. Even if we don't export photos, the input validation should allow pasting a photo as a "memory jogger."
    - The teacher sees the photo of the tower -> remembers the complex negotiation that happened -> writes the comment.
    - *Action:* Add "Upload/Paste Photo" to the Observation Capture schema (stored locally, not exported).

### Critique: The "Translation Tax"
Teachers constantly mentally translate "Kid Speak" (what happened) to "Parent Speak" (warm narrative) to "Curriculum Speak" (assessment).
- **The Problem**: The app currently asks them to write the final output directly.
- **The Fix**: **"Language Toggles" or "Tone Tuners"**.
    - Allow entering raw notes: "played in sand, made a tunnel."
    - "Magic Button" (Start with...) -> Suggests: "Demonstrated inquiry skills by exploring properties of materials..."
    - *Why:* Reduces the "writer's block" of formalizing simple play.

### Critique: Anxiety Management (The "Sunday Night" Factor)
Report writing is often done under duress (deadlines, late nights).
- **The Problem**: A UI full of red "Incomplete" dots and progress bars induces anxiety.
- **The Fix**: **Zero-Distraction "Zen Mode"**.
    - A button that hides the Roster, the Progress Bars, and the Menus.
    - Just the Student Name, the ONE prompt being answered, and the text box.
    - "Just one thought at a time."

### Refined Workflow: The "Pedagogical Loop"
1.  **Capture (Throughout Term):** Quick phone/tablet entry. "Photo + Tag + 3 words." (e.g., [Photo of art], #Belonging, "shared crayons")
2.  **Review (Mid-Term):** "Gallery Walk" view of a student's term. Spot the gaps. "Oh, I have nothing for Math." -> Plan activities to fill gaps.
3.  **Synthesize (Report Time):** Drag "Crayons" and "Blocks" cards into the "Belonging" bucket. App suggests: "X is learning to share materials..."
4.  **Refine (Final Polish):** The "Read Aloud" test.

### Final Verdict
The "Three-Pane Studio" is solid *production* UI, but we need to ensure the *inputs* (observations) are rich enough to make the production easy. V1 can launch without the full "Staging Area," but the data model *must* support attaching media and raw notes to students now, or we paint ourselves into a corner.

---

## 4E. Senior UX Review: Elementary (Homeroom) Workflow

*Critique and workflow improvements from a Senior Product Design lens for an Elementary homeroom teacher (Grades 1–8), where reporting is still narrative-heavy but less observation/play-driven than kindergarten.*

### How an elementary teacher thinks (practical mental model)

Elementary homeroom report writing is typically a loop of:
- **“Who is this student as a learner?”** (identity + tone consistency across subjects)
- **“What evidence do I have?”** (assignments, conversations, informal checks)
- **“What is the next step?”** (instructional focus + student goal)
- **“How do I say it parent-facing?”** (encouraging + specific + readable)

Compared to kindergarten, the evidence is less “moments” and more “work samples and trends,” but the pain is the same: *volume + consistency + avoiding repetition.*

### Critique: The “Thread Consistency” problem

Elementary teachers often need comments across multiple subject areas (and sometimes learning skills), and parents read them as one story.
- **The Problem:** If each subject is written in isolation, the report can feel like unrelated fragments.
- **Workflow improvement:** Add a concept of a **Student Narrative Thread** (not exported verbatim, but used to guide writing).
  - A 1–3 sentence “student snapshot” (strengths, growth areas, supports) that stays visible while writing other sections.
  - A lightweight “tone target” (Encouraging / Neutral / Firm) plus readability indicator for parent-facing clarity.

### Critique: Teachers batch work, but not always by “section”

Even in elementary, teachers commonly batch by:
- **Subject/strand** (write all Math in a sitting)
- **Student group** (IEP/ELL first, or students needing careful wording)
- **“Needs review” pass** (final polish later)

**Workflow improvement:** Expand “Work Queue” into a teacher-native tool:
- Saved filters: “IEP flagged”, “ELL flagged”, “Not started”, “Over character limit”, “Needs tone check”.
- A “Review pass” mode that shows one student’s full report on one screen for coherence.

### Critique: Repetition anxiety is bigger in elementary than it looks

Teachers absolutely reuse phrasing (it’s unavoidable), but they fear it looking lazy.
- **The Problem:** Copy/paste is fast but risky, and it produces sameness.
- **Workflow improvement:** Provide a **Variation Assistant** that is *deterministic and teacher-controlled*.
  - Example: teacher picks a “base sentence” and selects 2–3 acceptable variants.
  - Highlight repeated sentences across the class and let the teacher intentionally diversify.
  - Keep this non-AI for predictability (and to avoid “hallucinated” claims).

### Critique: Accommodations and supports need first-class handling

In elementary, many reports must reflect supports (IEP, accommodations, ELL scaffolds) without exposing sensitive details incorrectly.
- **The Problem:** Teachers keep accommodations in separate documents and forget to align wording.
- **Workflow improvement:** Add a **Supports Drawer** per student (not exported by default) that can insert safe, approved phrasing.
  - “With support” / “With prompting” / “Using visuals” / “Using assistive technology” modifiers.
  - A “sensitivity guardrail” that warns if prohibited terms appear (board policy varies).

### Critique: “Evidence selection” should be easier than “evidence entry”

In elementary, the evidence is often already present (notes, rubrics, quick checks), but is scattered.
- **Workflow improvement:** Evidence should be **selectable and re-usable**.
  - Minimal v1 concept: a per-student “Evidence snippets” drawer (already in the schema as `evidence_snippets`).
  - Allow tagging by subject/strand and marking as “strong evidence” vs “anecdotal”.
  - The main win: reduce retyping and improve specificity.

### UI emphasis recommendations for elementary defaults

If the app is in “Elementary context” (homeroom):
- Default to **Student Flow** (narrative cohesion is king).
- Keep **Student identity** anchored: name + pronouns + flags + “Student Narrative Thread”.
- Make **Review/Polish** a first-class step (one-screen full report view).

### “V1 but high impact” elementary workflow upgrades

If we want a focused set of elementary improvements with strong ROI:
1. **Student Narrative Thread** (always-visible snapshot while writing).
2. **Work Queue filters** oriented around real teacher batching.
3. **Deterministic Variation Assistant** (teacher-controlled phrase variation).
4. **Supports Drawer** for safe accommodations language.
5. **Review Pass** mode for coherence before export.

---

## 5. UI Layout: "The Three-Pane Studio" (Detailed)

```
┌──────────────────────────────────────────────────────────────────────┐
│  [Logo]  VGReport              [Settings ⚙️]  [Help ❓]  [Dark 🌙]   │
├────────────┬─────────────────────────────────────────┬───────────────┤
│            │                                         │               │
│  ROSTER    │              WORKSPACE                  │   PREVIEW     │
│            │                                         │               │
│  ┌───────┐ │  ┌─────────────────────────────────┐   │  ┌──────────┐ │
│  │Francis│ │  │ [Belonging] [Self-Reg] [L&M] [PS]│   │  │ ┌──────┐ │ │
│  │ ●●●○  │ │  └─────────────────────────────────┘   │  │ │Francis│ │ │
│  ├───────┤ │                                         │  │ └──────┘ │ │
│  │Maria  │ │  ┌─────────────────────────────────┐   │  │          │ │
│  │ ●●○○  │ │  │ KEY LEARNING                    │   │  │ Belonging│ │
│  ├───────┤ │  │                                 │   │  │ ──────── │ │
│  │James  │ │  │ Template: [Developing sense...▼]│   │  │ Francis  │ │
│  │ ○○○○  │ │  │                                 │   │  │ is devel-│ │
│  ├───────┤ │  │ Observation:                    │   │  │ oping... │ │
│  │...    │ │  │ ┌─────────────────────────────┐ │   │  │          │ │
│  └───────┘ │  │ │ sharing toys with peers     │ │   │  │ Growth   │ │
│            │  │ │ during block play...        │ │   │  │ ──────── │ │
│  ──────────│  │ └─────────────────────────────┘ │   │  │ Since... │ │
│  + Add     │  └─────────────────────────────────┘   │  │          │ │
│  Student   │                                         │  │ 📊 547   │ │
│            │  ┌─────────────────────────────────┐   │  │ chars    │ │
│  ──────────│  │ GROWTH                          │   │  │ ✓ Valid  │ │
│  Progress: │  │ ...                             │   │  │          │ │
│  12/25     │  └─────────────────────────────────┘   │  │ [Copy]   │ │
│  Complete  │                                         │  │ [Export] │ │
│            │  ┌─────────────────────────────────┐   │  └──────────┘ │
│            │  │ NEXT STEPS                      │   │               │
│            │  │ ...                             │   │               │
│            │  └─────────────────────────────────┘   │               │
│            │                                         │               │
└────────────┴─────────────────────────────────────────┴───────────────┘

Legend: ● = Frame complete  ○ = Frame incomplete
```

### Component Breakdown

| Component | Responsibility | Key Interactions |
|-----------|----------------|------------------|
| `<Sidebar />` | Student roster, progress tracking, global actions | Click to select student, drag to reorder |
| `<FrameTabs />` | Switch between the 4 developmental frames | Click tab, keyboard arrow keys |
| `<SectionEditor />` | Template selection + slot input for one section | Dropdown, textarea, autosave |
| `<LivePreview />` | Rendered report card with validation | Read-only, copy button, length indicator |
| `<SettingsModal />` | Board config, theme, export preferences | Modal overlay |

---

## 6. Data Model

### Local Storage Schema (SQLite)

```sql
-- Core Entities
CREATE TABLE students (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    pronouns_subject TEXT,  -- "He", "She", "They"
    pronouns_object TEXT,   -- "him", "her", "them"
    pronouns_possessive TEXT, -- "his", "her", "their"
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE report_periods (
    id TEXT PRIMARY KEY,  -- "2025-fall", "2026-feb", "2026-june"
    name TEXT,            -- "Initial Observations"
    board_id TEXT,        -- "tcdsb"
    is_active BOOLEAN,
    locked_at DATETIME
);

CREATE TABLE drafts (
    id TEXT PRIMARY KEY,
    student_id TEXT REFERENCES students(id),
    report_period_id TEXT REFERENCES report_periods(id),
    frame TEXT,           -- "belonging", "self_regulation", etc.
    section TEXT,         -- "key_learning", "growth", "next_steps"
    template_id TEXT,     -- "template.comment.belonging.key_learning.01"
    slot_values JSON,     -- {"evidence": "...", "change": "..."}
    rendered_text TEXT,   -- Cached output
    updated_at DATETIME,
    UNIQUE(student_id, report_period_id, frame, section)
);

-- Personal Evidence Bank
CREATE TABLE evidence_snippets (
    id TEXT PRIMARY KEY,
    student_id TEXT REFERENCES students(id),
    text TEXT,
    tags JSON,  -- ["math", "collaboration"]
    created_at DATETIME
);
```

---

## 7. Development Gameplan
This section has moved to `docs/frontend_gameplan.md` to keep the design spec focused.

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tauri + Python sidecar complexity | Medium | High | Fallback: PyWebView if IPC is too painful |
| Contract drift (Python ↔ TS) | Medium | High | Generate TS types from a shared schema and fail CI on drift |
| Teacher finds UI confusing | Medium | High | Early paper prototyping, user testing |
| PDF export doesn't match official form | Medium | Medium | Use Ontario's official PDF as pixel reference |
| Data loss due to bug | Low | Critical | Autosave + backup reminders + crash recovery |
| Performance with large roster | Low | Low | SQLite handles thousands of records easily |

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Time to complete one student's report | < 15 minutes |
| Crash rate | 0 crashes per session |
| Autosave reliability | 100% (no lost work) |
| PDF export accuracy | Visually indistinguishable from official form |
| App startup time | < 3 seconds |
| Installer size | < 50 MB |

---

## 10. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-11 | Rejected Streamlit | Not suitable for professional UX; no offline support |
| 2026-01-11 | Chose Tauri over Electron | 10x smaller, faster, more secure |
| 2026-01-11 | Chose React over Svelte | Larger ecosystem, more hiring options, team familiarity |
| 2026-01-11 | Chose SQLite over JSON files | Better query support, ACID compliance, handles scale |
| 2026-01-11 | Python sidecar over rewriting in Rust/JS | Reuse existing validated logic |
| 2026-01-11 | Product name: **VGReport** | Clear, professional, domain-relevant |
| 2026-01-11 | Open-source licensing | Community-driven development, transparency for educators |
| 2026-01-11 | Design for future cloud sync | Add `user_id` to schema, use UUIDs, prepare for sync layer |
| 2026-01-11 | Manual JSON Schema (not Pydantic) | Existing codebase uses `@dataclass`; avoid large refactor |
| 2026-01-11 | Minimal sidecar deps | Exclude pandas/pyarrow/duckdb from sidecar to keep bundle <50MB |
| 2026-01-11 | NDJSON IPC protocol | Simple stdin/stdout JSON; no HTTP overhead for desktop app |
| 2026-01-11 | MIT License | Maximum permissiveness for educational community adoption |
| 2026-01-12 | Support both writing workflows | Teachers can work student-by-student or section-by-section; UI should support both |
| 2026-01-12 | Multiple export formats | Preferences vary; support PDF-per-student, combined PDF, CSV, and clipboard |
| 2026-01-12 | Kindergarten-first v1 scope | Design for Ontario kindergarten teachers specifically; expand later |
| 2026-01-12 | Observation capture before writing | Teachers collect evidence during play; need a place to store observations before report writing |
| 2026-01-12 | Term-to-term continuity | Growth language requires seeing prior term; provide side-by-side Fall/Feb/June view |
| 2026-01-12 | ECE collaboration field | Kindergarten is team-taught; include ECE notes even if not exported |
---

## 11. Resolved Questions

| Question | Decision | Implication |
|----------|----------|-------------|
| **Product Name** | **VGReport** | Branding, installer name, window title, documentation |
| **Licensing** | **MIT License** | `LICENSE` file created; maximum permissiveness for educators |
| **Multi-user Future** | **Yes** | Data model must include `user_id`, sync-ready schema, conflict resolution strategy |
| **ECE Collaboration** | TBD (Phase 2) | Consider "share via link" or local export/import for now |
| **Contract Generation** | Manual JSON Schema + `json-schema-to-typescript` | No Pydantic migration needed; schemas in `/contracts/` |

---

## 12. Next Immediate Action
Implementation and next actions are tracked in `docs/frontend_gameplan.md`.

---

## 13. Cloud-Ready Data Model Addendum

Since we're designing for future multi-user/cloud sync, the schema needs these additions:

```sql
-- Add to all tables for sync support
ALTER TABLE students ADD COLUMN sync_id UUID UNIQUE;  -- Global identifier
ALTER TABLE students ADD COLUMN user_id TEXT;          -- Owner (for future)
ALTER TABLE students ADD COLUMN synced_at DATETIME;    -- Last cloud sync
ALTER TABLE students ADD COLUMN is_dirty BOOLEAN DEFAULT TRUE;  -- Needs sync

-- Conflict resolution: "last write wins" with tombstones
CREATE TABLE sync_tombstones (
    entity_type TEXT,      -- "student", "draft", etc.
    entity_id TEXT,
    deleted_at DATETIME,
    user_id TEXT
);
```

**Sync Strategy (Future)**:
1. Local-first: All writes go to SQLite immediately.
2. Background sync: When online, push dirty records to cloud.
3. Conflict resolution: Timestamp-based "last write wins" with manual merge UI for conflicts.
4. Offline queue: Failed syncs are retried automatically.
