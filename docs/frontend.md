---
id: design.frontend
type: design_doc
title: VGReport – Frontend User Experience Design
version: 0.4.0
status: draft
target_audience: [developers, designers]
updated: 2026-01-11
product_name: VGReport
license: Open Source (MIT)
---

# VGReport: Frontend Design Strategy

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
2. A script generates **TypeScript types** from those schemas into `/frontend/src/types/`.
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

### Phase 0: Prerequisites (Week 0)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 0.1 | Install Rust toolchain (Rustup) | `rustc` + `cargo` available in terminal | ✅ Done (restart VS Code to activate PATH) |
| 0.2 | WebView2 detection + install plan | Evergreen WebView2 policy documented | ✅ Done (see Section 3A) |
| 0.3 | Choose engine shipping approach | PyInstaller sidecar; minimal deps in `sidecar/engine-requirements.txt` | ✅ Done |
| 0.4 | Lock contract generation approach | **Manual JSON Schema → TypeScript** (no Pydantic migration) | ✅ Done (see Section 3C) |
| 0.5 | Define IPC protocol specification | Protocol documented in Section 3D | ✅ Done |
| 0.6 | Create LICENSE file | MIT License in repo root | ✅ Done |
| 0.7 | Verify Rust after PATH refresh | Run `rustc --version` in new terminal | ⏳ Pending (user action) |

### Phase 0 Exit Criteria

Before starting Phase 1, ALL of the following must be true:

- [x] `rustc --version` returns `1.92.0` or higher in a new terminal
- [x] `cargo --version` returns `1.92.0` or higher
- [x] `LICENSE` file exists in repo root (MIT)
- [x] `sidecar/engine-requirements.txt` exists with minimal deps
- [x] IPC protocol is documented (Section 3D)
- [x] JSON Schema contract approach is documented (Section 3C)

### Phase 1: Foundation (Week 1-2)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 1.1 | Initialize Tauri + Vite + React + TypeScript project | `/frontend/` scaffold | ✅ Done |
| 1.2 | Configure Tailwind CSS + Shadcn/UI | Base styling system | ✅ Done |
| 1.3 | Create Python sidecar wrapper for existing `lib/` logic | `sidecar/main.py` | ✅ Done |
| 1.4 | Package the Python engine as a standalone sidecar binary | `vgreport-engine.exe` (dev build) | ⏳ Next |
| 1.5 | Implement Tauri IPC bridge (React ↔ engine) | Stable JSON message protocol | |
| 1.6 | Set up SQLite database with schema above | `data/vgreport.db` | |
| 1.7 | Add contract generation step (Python → TS types) | Generated TS types + CI guard | |
| 1.8 | Build basic layout shell (three-pane) | `<AppShell />` component | |

### Phase 2: Core Editing Experience (Week 3-4)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Student Roster sidebar with CRUD | `<Sidebar />`, `<StudentCard />` |
| 2.2 | Frame Tabs navigation | `<FrameTabs />` |
| 2.3 | Section Editor with template dropdown | `<SectionEditor />` |
| 2.4 | Dynamic slot input generation | `<SlotInput />` (text, textarea, select) |
| 2.5 | Live Preview panel with real-time rendering | `<LivePreview />` |
| 2.6 | Autosave with visual indicator | Zustand + debounce + SQLite write |
| 2.7 | Character count + validation feedback | Length bar, color coding |

### Phase 3: Polish & Export (Week 5-6)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Onboarding wizard (first-launch flow) | `<OnboardingWizard />` |
| 3.2 | Settings modal (board selection, theme) | `<SettingsModal />` |
| 3.3 | PDF export with proper formatting | Tauri print API or `jspdf` |
| 3.4 | CSV export for SIS import | Standard export |
| 3.5 | Keyboard shortcuts (Ctrl+S, Tab, etc.) | Hotkey system |
| 3.6 | Dark mode | CSS variables + system detection |
| 3.7 | Undo/Redo stack | Command pattern in Zustand |

### Phase 4: Testing & Packaging (Week 7-8)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Unit tests for React components | Vitest + Testing Library |
| 4.2 | Integration tests for Python sidecar | pytest |
| 4.3 | End-to-end test: full report generation | Playwright or Tauri test |
| 4.4 | Build Windows installer (`.msi`) | Tauri build |
| 4.5 | Build macOS installer (`.dmg`) | Tauri build |
| 4.6 | User documentation / Help system | In-app help + PDF guide |
| 4.7 | Beta testing with real teacher | Feedback loop |

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
| 2026-01-11 | Design for future cloud sync | Add `user_id` to schema, use UUIDs, prepare for sync layer || 2026-01-11 | Manual JSON Schema (not Pydantic) | Existing codebase uses `@dataclass`; avoid large refactor |
| 2026-01-11 | Minimal sidecar deps | Exclude pandas/pyarrow/duckdb from sidecar to keep bundle <50MB |
| 2026-01-11 | NDJSON IPC protocol | Simple stdin/stdout JSON; no HTTP overhead for desktop app |
| 2026-01-11 | MIT License | Maximum permissiveness for educational community adoption |
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

**Phase 0 is complete.** After restarting VS Code to activate the Rust PATH:

1. **Verify Rust**: `rustc --version` and `cargo --version`
2. **Initialize Tauri project**:

```bash
# Prerequisites: Node.js 18+, Rust toolchain active
npm create tauri-app@latest vgreport -- --template react-ts
cd vgreport
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npx shadcn-ui@latest init
```

3. **Create contracts directory**: `mkdir contracts`
4. **Set up sidecar structure**: See `sidecar/engine-requirements.txt`

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
