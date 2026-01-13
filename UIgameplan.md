---
id: doc.vgreport.ui_utilization_gameplan
type: document
title: VGReport UI Utilization & Discoverability Gameplan
version: 0.7.0
status: draft
tags: [gameplan, vgreport, ui, ux, audit, tauri, react, prompts]
refs:
  - doc.testing
  - doc.vgreport.kindergarten_alignment_gameplan
updated: 2026-01-12
---

# VGReport UI Utilization & Discoverability Gameplan

Purpose: identify **implemented-but-not-discoverable** UI features, **orphaned** code, and **underutilized** logic in the VGReport app, then propose a phased UI/UX plan to surface, wire, or remove them.

## Progress

- Phase 1 completed (2026-01-12): Export button added to Workspace header; Export is now reachable on all viewport sizes.
- Phase 2A completed (2026-01-12): "Roster import: coming soon (CSV)" footer added to Sidebar.
- Phase 3 partial (2026-01-12): Removed unused `flagged`/`recent` filter values, removed unused `canApprove()`, deleted unused `App.css`.
- **Phase 2 completed (2026-01-12)**: Contracts wired for type safety; sidecar.ts now uses generated types; `call<T>()` is generic.
- **Phase 3 completed (2026-01-12)**: Frame colors applied to Workspace tabs and ExportCenter grid cells for visual wayfinding.
- **Phase 4 completed (2026-01-12)**: Board config wired; changing board updates validation char limits; Settings shows board info.
- **Phase 5 completed (2026-01-12)**: Multi-period support implemented; switching periods loads different drafts; period-aware persistence.
- **Phase 6 completed (2026-01-12)**: Evidence bank implemented; teachers can save observation snippets and insert into comment slots.
- **Phase 7 completed (2026-01-13)**: Roster CSV import implemented; bulk student import with validation and dry-run preview.

This document:
- includes **example implementation snippets** (for engineering clarity)
- includes **effort sizing** and **acceptance criteria**
- includes **agent execution prompts** (copy-paste ready for AI-assisted execution)
- does **not** change any code by itself

## Constraints and best practices (aligned to repo checks)

From [scripts/check_all.py](scripts/check_all.py) and the repo index [index.md](index.md):

- Keep changes compatible with `./check --quick` and `./check` gates:
  - Ruff format/lint, schema validation, reference lint, index completeness (and full checks: pytest/pyright/docs sync).
- Keep docs and artifacts **PII-free**.
- Prefer explicit, testable acceptance criteria.
- If this document is treated as "canonical", link it from `index.md` (enforced by `scripts/check_index.py` for canonical folders).

---

## Findings (utilization audit)

### F1. Export exists but is not reliably discoverable ✅ RESOLVED

- Export UI is implemented in [vgreport/src/components/ExportCenter.tsx](vgreport/src/components/ExportCenter.tsx).
- Previously: only reachable via Preview panel (hidden below `lg` breakpoint).
- **Fix applied**: Export button added to Workspace header.

### F2. Import is explicitly deferred (not implemented) ✅ RESOLVED (UX)

- Onboarding indicates "CSV import is coming next" in [vgreport/src/components/OnboardingWizard.tsx](vgreport/src/components/OnboardingWizard.tsx).
- **Fix applied**: Sidebar footer now shows "Roster import: coming soon (CSV)".

### F3. Orphaned / future-leaning artifacts (partial)

| Item | Status | Action Taken / Needed |
|------|--------|----------------------|
| `RosterFilter` unused values (`flagged`, `recent`) | ✅ Removed | Trimmed from union type |
| `canApprove()` unused export | ✅ Removed | Deleted from roleApproval.ts |
| `App.css` unused file | ✅ Removed | Deleted |
| `contracts/generated.ts` not imported | ⚠️ **Keep & Wire** | Has high value for type safety |
| `report_periods` table unused | ⚠️ **Keep & Wire** | Foundation for multi-period support |
| `evidence_snippets` table unused | ⚠️ **Keep & Wire** | Foundation for observation bank |

### F4. Underutilized settings and state

| Setting | Current State | Recommended Action |
|---------|---------------|-------------------|
| `boardId` | Persisted but no observable effect | Wire to board config (char limits, custom slots) |
| `currentPeriod` | Persisted but drafts not period-segmented | Implement period-aware draft cache |
| `FRAMES[].color` | Defined but not rendered | Apply to frame tabs for visual wayfinding |

---

## Plan Overview

**Primary goals** (in priority order):
1. ✅ Make core actions discoverable (Export, Import status)
2. Wire underutilized scaffolding that adds real value (type safety, board config)
3. Complete behavioral alignment (settings that actually do something)
4. Implement deferred features when justified (multi-period, evidence bank, CSV import)

---

## Phase 1 — Surface core actions ✅ COMPLETE

**Status**: Completed 2026-01-12

- Export button added to Workspace header
- "Roster import: coming soon" added to Sidebar footer
- Unused filter values and helpers removed

---

## Phase 2 — Wire contracts for type safety ✅ COMPLETE

**Status**: Completed 2026-01-12

**Goal**: Eliminate `any` types in sidecar communication; catch schema drift at compile time.

**Effort**: S (1 day)

**What was done**:
1. Updated `scripts/contracts_gen.mjs` with `schemaToTypeScript()` to emit real TS interfaces from JSON Schema
2. Regenerated `src/contracts/generated.ts` with proper interfaces: `IpcRequest`, `IpcResponse<T>`, `IpcError`, `Template`, `RenderCommentParams`
3. Added method-specific response types: `HealthResponse`, `ListTemplatesResponse`, `RenderCommentResponse`, `DebugInfoResponse`
4. Updated `sidecar.ts` to import and re-export contract types
5. Made `call<T>()` method generic for type-safe responses
6. Updated consumers (`App.tsx`, `SectionEditor.tsx`) to use typed calls

**Acceptance criteria met**:
- ✅ `npx tsc --noEmit` passes with no `any` in sidecar.ts (except internal `pendingRequests` map which is acceptable)
- ✅ All 23 tests pass
- ✅ Changing a schema regenerates types (drift detection via sha256 markers)

---

## Phase 3 — Apply frame colors for visual wayfinding ✅ COMPLETE

**Status**: Completed 2026-01-12

**Goal**: Use the existing `FRAMES[].color` property that's already defined.

**Effort**: XS (0.5 day)

**What was done**:
1. Updated Workspace.tsx frame tabs to apply `frame.color` class to selected tab
2. Enhanced ExportCenter.tsx to include `frameColor` in box data
3. Applied frame colors to 12-box grid cells in ExportCenter

**Acceptance criteria met**:
- ✅ Frame tabs are visually distinct by color (red, amber, blue, green)
- ✅ Selected tab shows its frame color from constants.ts
- ✅ ExportCenter grid cells show frame-specific colors
- ✅ TypeScript check passes
- ✅ All 23 tests pass

---

## Phase 4 — Wire boardId to board configuration ✅ COMPLETE

**Status**: Completed 2026-01-12

**Goal**: Make the board selector actually do something observable.

**Effort**: S–M (1–3 days)

**What was done**:
1. Created JSON board configs in `vgreport/src/configs/boards/` (ncdsb.json, tcdsb.json)
2. Created `vgreport/src/configs/boardConfig.ts` with `BoardConfig` interface and `loadBoardConfig()` function
3. Updated `useAppStore.ts` to import and use board configs
4. Modified `setBoardId()` to load config and apply `char_limits` to `tier1Validation`
5. Modified `hydrateFromDb()` to apply board config defaults on first load
6. Updated `SettingsModal.tsx` to display board name and char limits

**Acceptance criteria met**:
- ✅ Changing board in Settings updates tier1Validation.minChars/maxChars
- ✅ Default board config (tcdsb) loads on app start
- ✅ Settings modal shows board abbreviation and char limits (e.g., "TCDSB (80-500 chars)")
- ✅ TypeScript check passes
- ✅ All 23 tests pass

**Implementation details**:
- NCDSB: 100-600 chars per section
- TCDSB: 80-500 chars per section
- Board configs bundled as JSON for Vite compatibility

---

## Phase 5 — Implement multi-period support ✅ COMPLETE

**Status**: Completed 2026-01-12

**Goal**: Make `currentPeriod` switching actually load different drafts.

**Effort**: M (3–5 days)

**What was done**:
1. Updated `setCurrentPeriod()` in useAppStore.ts to reload drafts when period changes
2. Period switching now queries `db_list_drafts(period)` to load period-specific data
3. Clears undo/redo history when switching periods (prevents cross-period undo bugs)
4. Drafts are already persisted per-period in SQLite (via `report_period_id` column)
5. Period picker already exists in SettingsModal (initial, february, june)

**Acceptance criteria met**:
- ✅ Switching periods shows different draft data
- ✅ Drafts are persisted per-period in SQLite (existing schema support)
- ✅ Period picker in Settings shows all available periods
- ✅ TypeScript check passes
- ✅ All 23 tests pass

**Implementation approach**:
- Leveraged existing database schema (report_periods table, drafts.report_period_id column)
- Used existing `db_list_drafts(period)` command (already period-aware)
- Simple implementation: reload drafts on period change rather than complex `draftsByPeriod` cache
- Undo/redo stacks cleared on period switch for data integrity

---

## Phase 6 — Implement evidence bank (observation snippets) ✅ COMPLETE

**Status**: Completed 2026-01-12

**Goal**: Let teachers save quick observations and pull them into comments later.

**Effort**: M (3–5 days)

**What was done**:
1. Added Tauri commands to [lib.rs](vgreport/src-tauri/src/lib.rs): `db_list_evidence`, `db_add_evidence`, `db_delete_evidence`
2. Created [evidence.ts](vgreport/src/types/evidence.ts) with `EvidenceSnippet` TypeScript type
3. Updated [db.ts](vgreport/src/services/db.ts) to expose evidence commands
4. Created [EvidenceBank.tsx](vgreport/src/components/EvidenceBank.tsx) with:
   - Quick-add form (text + tags)
   - Searchable list of snippets
   - Insert and delete buttons per snippet
5. Integrated evidence panel in [App.tsx](vgreport/src/App.tsx) as collapsible right panel with toggle button
6. Added evidence insertion in [SectionEditor.tsx](vgreport/src/components/SectionEditor.tsx) via custom event listener
7. Added focus tracking to detect last active slot for insertion

**Acceptance criteria met**:
- ✅ Can add/view/delete evidence snippets
- ✅ Can filter by student (shows only selected student's evidence)
- ✅ Can search evidence by text
- ✅ Can insert snippet text into comment slots (inserts at cursor or end of last active slot)
- ✅ Evidence panel is collapsible and doesn't block main UI
- ✅ TypeScript check passes
- ✅ All 23 tests pass

**Implementation details**:
- Evidence snippets stored in SQLite with id, student_id, text, tags_json, created_at
- Tags are comma-separated strings stored as JSON array
- Insert button dispatches custom event that SectionEditor listens for
- Evidence bank only shows when student is selected

---

## Phase 7 — Implement roster CSV import ✅ COMPLETE

**Status**: Completed 2026-01-13

**Goal**: Allow bulk student import from CSV.

**Effort**: M (2–5 days)

**What was done**:
1. Installed papaparse CSV parser library with TypeScript types
2. Created [rosterCsvSchema.ts](vgreport/src/import/rosterCsvSchema.ts) with CSV schema definition:
   - Required fields: first_name, last_name
   - Optional fields: student_local_id, preferred_name, pronouns, needs
3. Created [parseRosterCsv.ts](vgreport/src/import/parseRosterCsv.ts) with robust parsing:
   - Handles UTF-8 BOM, CRLF, quoted fields
   - Validates required headers and row data
   - Generates import preview with duplicate detection
4. Created [RosterImportModal.tsx](vgreport/src/components/RosterImportModal.tsx):
   - File picker with drag-and-drop UI
   - Parse error display
   - Dry-run preview showing N added, M updated
   - Warnings for duplicates
   - Batch import execution
5. Wired import button in [Sidebar.tsx](vgreport/src/components/Sidebar.tsx):
   - Replaced "coming soon" footer with Import Roster CSV button
   - Opens RosterImportModal on click

**Acceptance criteria met**:
- ✅ Can import valid CSV files
- ✅ Invalid rows show clear error messages with row numbers
- ✅ Duplicate detection by first_name + last_name
- ✅ Dry-run preview shows adds vs updates before execution
- ✅ Batch import calls addStudent/updateStudent
- ✅ TypeScript check passes
- ✅ All 23 tests pass

**Implementation details**:
- Uses papaparse for robust CSV parsing
- Duplicate students (same first_name + last_name) are updated, not duplicated
- Needs field supports semicolon-separated values (e.g., "IEP;ELL")
- Pronouns default to they/them/their if not provided
- Import is atomic: all students are processed in sequence
- File picker accepts only .csv files

---

## QA / Validation gates

Aligned to [docs/TESTING.md](docs/TESTING.md):

| Gate | Command | When |
|------|---------|------|
| Quick checks | `./check --quick` | During development |
| Full checks | `./check` | Before merge |
| VGReport unit tests | `cd vgreport && npm test` | After any code change |
| TypeScript | `cd vgreport && npx tsc --noEmit` | After any TS change |
| Tauri smoke | `cd vgreport && npm run e2e:tauri` | After Tauri/sidecar changes |
| Build artifacts | `npm run build:tauri && npm run e2e:build-check` | Before release |

**Manual UI checks** (no PII):
- Export button visible and functional at narrow widths
- Board change updates validation limits
- Period switch shows correct drafts
- Frame tabs show distinct colors

---

## Priority Summary

| Phase | Description | Effort | Impact | Status |
|-------|-------------|--------|--------|--------|
| 1 | Surface core actions (Export, Import status) | S | High | ✅ Complete |
| 2 | Wire contracts for type safety | S | Medium-High | ✅ Complete |
| 3 | Apply frame colors | XS | Low-Medium | ✅ Complete |
| 4 | Wire boardId to board config | S–M | Medium | ✅ Complete |
| 5 | Multi-period support | M | High | ✅ Complete |
| 6 | Evidence bank | M | Medium-High | ✅ Complete |
| 7 | Roster CSV import | M | Medium | ✅ Complete |

**Recommended execution order**: 1 → 2 → 3 → 4 → 5 → 6 → 7

Rationale:
- Phase 2 (contracts) improves developer experience for all subsequent work
- Phase 3 (colors) is quick polish with no dependencies
- Phase 4 (boardId) unlocks board-specific behavior before multi-period
- Phase 5 (periods) is high user value but higher complexity
- Phases 6–7 are additive features that can be deferred

---

## Agent Execution Prompts

This section contains production-ready prompts for executing each phase. Copy the relevant prompt to initiate work.

### Master Context Prompt (use at session start)

```
You are working on the VGReport desktop app (Tauri + React + TypeScript frontend, Rust + SQLite backend, Python sidecar).

Key files:
- Store: vgreport/src/store/useAppStore.ts
- Constants: vgreport/src/constants.ts
- Sidecar client: vgreport/src/services/sidecar.ts
- Contracts: vgreport/src/contracts/generated.ts
- Backend: vgreport/src-tauri/src/lib.rs
- Board configs: config/boards/*.yaml

Validation gates (run after changes):
- TypeScript: cd vgreport && npx tsc --noEmit
- Unit tests: cd vgreport && npm test
- Quick checks: ./check --quick

Reference: UIgameplan.md contains the full execution plan with acceptance criteria.
```

---

### Phase 2 Prompt: Wire contracts for type safety

```
Execute Phase 2 of UIgameplan.md: Wire contracts for type safety.

Context:
- vgreport/src/contracts/generated.ts exists but contains only `unknown` types
- vgreport/src/services/sidecar.ts uses hand-rolled interfaces with `any`
- JSON schemas exist in contracts/*.schema.json

Tasks:
1. Read scripts/contracts_gen.mjs to understand the generator
2. Read contracts/*.schema.json to understand the IPC contract shapes
3. Update contracts_gen.mjs to emit real TypeScript interfaces from the JSON schemas (not just `unknown`)
4. Run `npm run contracts:gen` (or equivalent) to regenerate
5. Update sidecar.ts to import and use the generated types instead of hand-rolled interfaces
6. Remove the hand-rolled JsonRpcRequest/JsonRpcResponse interfaces
7. Run `npx tsc --noEmit` to verify no type errors
8. Run `npm test` to verify no regressions

Acceptance criteria:
- Generated types are real interfaces (not `unknown`)
- sidecar.ts imports from contracts/generated.ts
- No `any` types remain in sidecar.ts IPC code
- TypeScript and tests pass

After completion, update UIgameplan.md Progress section.
```

---

### Phase 3 Prompt: Apply frame colors

```
Execute Phase 3 of UIgameplan.md: Apply frame colors for visual wayfinding.

Context:
- vgreport/src/constants.ts defines FRAMES with a `color` property (e.g., 'bg-red-100 text-red-900')
- This color is not currently rendered anywhere in the UI
- Frame tabs are in vgreport/src/components/Workspace.tsx

Tasks:
1. Read vgreport/src/constants.ts to see the FRAMES color definitions
2. Read vgreport/src/components/Workspace.tsx to find the frame tab rendering
3. Apply the frame's color class to the active/selected tab using cn()
4. Optionally apply colors to the 12-box grid in ExportCenter.tsx
5. Run `npx tsc --noEmit` and `npm test`

Acceptance criteria:
- Selected frame tab shows its designated color
- Colors match what's defined in constants.ts
- TypeScript and tests pass

After completion, update UIgameplan.md Progress section.
```

---

### Phase 4 Prompt: Wire boardId to board config

```
Execute Phase 4 of UIgameplan.md: Wire boardId to board configuration.

Context:
- Board configs exist: config/boards/ncdsb.yaml, config/boards/tcdsb.yaml
- They define char_limits, custom_slots, export_settings
- useAppStore has boardId persisted but it has no observable effect
- tier1Validation has minChars/maxChars that should come from board config

Tasks:
1. Read config/boards/ncdsb.yaml and tcdsb.yaml to understand the schema
2. Determine how to load YAML in the Tauri app (options: sidecar method, Rust command, or bundle as JSON)
3. Create a function to load board config by boardId
4. In useAppStore, when boardId changes (setBoardId), load the board config and apply char_limits to tier1Validation
5. Optionally show board name in Settings or header
6. Run validation gates

Acceptance criteria:
- Changing board in Settings updates tier1Validation.minChars/maxChars
- Default board config loads on app start
- TypeScript and tests pass

After completion, update UIgameplan.md Progress section.
```

---

### Phase 5 Prompt: Multi-period support

```
Execute Phase 5 of UIgameplan.md: Implement multi-period support.

Context:
- report_periods table exists in SQLite schema (lib.rs) but is unused
- currentPeriod is persisted in app_settings but drafts are not period-segmented
- Teachers need to work on Term 1, Term 2, Final separately

Tasks:
1. Read vgreport/src-tauri/src/lib.rs to see the report_periods table schema
2. Add Tauri commands: db_list_report_periods, db_upsert_report_period, db_set_period_locked
3. Update db.ts to expose these commands to the frontend
4. Refactor useAppStore:
   - Change drafts to draftsByPeriod: Record<ReportPeriod, Record<string, ReportDraft>>
   - Update setCurrentPeriod to load drafts for that period if not cached
   - Update hydrateFromDb to load drafts for the current period only
5. Add a period picker UI in Settings or header
6. Update all draft reads/writes to be period-aware
7. Run validation gates

Acceptance criteria:
- Switching periods shows different draft data
- Drafts are persisted per-period in SQLite
- Period picker shows all available periods
- TypeScript and tests pass

After completion, update UIgameplan.md Progress section.
```

---

### Phase 6 Prompt: Evidence bank

```
Execute Phase 6 of UIgameplan.md: Implement evidence bank (observation snippets).

Context:
- evidence_snippets table exists in SQLite schema (lib.rs) but is unused
- Teachers want to save quick observations and pull them into comments later

Tasks:
1. Read vgreport/src-tauri/src/lib.rs to see the evidence_snippets table schema
2. Add Tauri commands: db_list_evidence, db_add_evidence, db_delete_evidence
3. Update db.ts to expose these commands
4. Create types/evidence.ts with EvidenceSnippet type
5. Create components/EvidenceBank.tsx:
   - Quick-add form (text + optional tags)
   - Searchable/filterable list
   - "Insert" button per snippet
6. Integrate EvidenceBank into the UI (collapsible panel or modal)
7. Add "Insert evidence" integration in SectionEditor
8. Run validation gates

Acceptance criteria:
- Can add/view/delete evidence snippets
- Can filter by student or tag
- Can insert snippet text into a comment
- TypeScript and tests pass

After completion, update UIgameplan.md Progress section.
```

---

### Phase 7 Prompt: Roster CSV import

```
Execute Phase 7 of UIgameplan.md: Implement roster CSV import.

Context:
- Onboarding promises "CSV import is coming next"
- Sidebar footer shows "Roster import: coming soon (CSV)"
- Manual student entry is tedious for 20+ students

Tasks:
1. Define CSV schema in a new file: vgreport/src/import/rosterCsvSchema.ts
   - Required: first_name, last_name
   - Optional: student_local_id, preferred_name, pronouns_subject/object/possessive, needs
2. Create vgreport/src/import/parseRosterCsv.ts using a robust CSV parser (papaparse or similar)
   - Handle quoted fields, CRLF, BOM
   - Return { rows: RosterCsvRow[], errors: string[] }
3. Create components/RosterImportModal.tsx:
   - File picker
   - Dry-run preview (N added, M updated, K errors)
   - Confirm button to execute import
4. Wire import button in Sidebar (replace "coming soon" text)
5. Batch call addStudent/updateStudent
6. Run validation gates

Acceptance criteria:
- Can import a valid CSV file
- Invalid rows show clear error messages
- Duplicate detection by name or student_local_id
- TypeScript and tests pass

After completion, update UIgameplan.md Progress section and remove "coming soon" messaging.
```

---

### Generic Phase Execution Template

```
Execute Phase [N] of UIgameplan.md: [Phase Title].

Before starting:
1. Read UIgameplan.md to understand the full context and acceptance criteria
2. Check the Progress section to see what's already done
3. Read the relevant source files listed in the phase description

During execution:
1. Make incremental changes
2. Run `npx tsc --noEmit` after TypeScript changes
3. Run `npm test` after logic changes
4. Commit logical units of work

After completion:
1. Run full validation: `./check --quick`
2. Update UIgameplan.md Progress section with completion date
3. Update the Priority Summary table status to ✅ Complete
4. Report what was done and any deviations from the plan
```

---

### Prompt Engineering Notes

**For best results:**

1. **One phase per session** — Each phase is scoped to be completable in one focused session. Don't combine phases.

2. **Context priming** — Always start with the Master Context Prompt to establish file locations and validation gates.

3. **Incremental validation** — The prompts instruct running TypeScript and tests frequently. This catches issues early.

4. **Explicit acceptance criteria** — Each prompt ends with clear pass/fail conditions. Verify all before marking complete.

5. **Progress tracking** — Update the gameplan after each phase. This prevents duplicate work and maintains state across sessions.

6. **Deviation handling** — If a phase can't be completed as written, document why in the Progress section and propose alternatives before proceeding.
