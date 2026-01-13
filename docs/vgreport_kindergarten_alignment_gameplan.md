---
id: doc.vgreport.kindergarten_alignment_gameplan
type: document
title: VGReport Kindergarten Alignment Gameplan (Edsembli-Oriented Input)
version: 0.2.6
status: draft
tags: [gameplan, vgreport, kindergarten, alignment, edsembli, user-roles]
refs:
  - doc.vgreport.frontend_design
  - doc.vgreport.frontend_gameplan
  - doc.integration.sis_formats
  - doc.research.edsembli_report_card_requirements_vs_vgreport
  - doc.research.edsembli_specifics_and_numbers
updated: 2026-01-12
---

# VGReport Kindergarten Alignment Gameplan (Edsembli-Oriented Input)

Purpose: plan the work to implement the **recommended Kindergarten-only alignment changes** captured in [docs/edsembli_report_card_requirements_vs_vgreport.md](docs/edsembli_report_card_requirements_vs_vgreport.md), while staying within a “comment authoring + export” scope (not a full SIS/report-card generator).

This is a **design + execution plan**. It does **not** implement anything.

## Progress

- Phase A completed (2026-01-12): requirements lock (golden exports + export-ready semantics + per-box constraints).
- Phase B completed (2026-01-12): role system + approval workflow persisted in local SQLite.
- Phase C completed (2026-01-12): Ctrl+K quick student search + Tier-1 validation heuristics (warn-only) including repetition warning.
- Phase D completed (2026-01-12): placeholder aliases + roster work-queue filters + modifier picker + configurable role labels.
- Phase E completed (2026-01-12): Export Center + golden exports (per-box clipboard + 12-box CSV).
- Phase F completed (2026-01-12): QA checklist + export golden tests + Tauri smoke E2E.

## Scope

In scope:
- The 12 Kindergarten inputs as first-class fields: **4 Frames × (Key Learning, Growth, Next Steps)**
- Better live validation aligned to “Live Form” / box-fit expectations
- **User Role system** (Teacher / ECE) with approval workflow — simpler than separate notes model
- Template placeholders aligned to common practice
- Export formats that map cleanly to SIS entry patterns

Out of scope (explicitly):
- OEN, attendance, signatures, grades, learning skills
- Parent portal functionality
- Full audit-log/compliance replication

## Baseline documents

- Design: [docs/frontend.md](docs/frontend.md)
- Existing VGReport execution plan: [docs/frontend_gameplan.md](docs/frontend_gameplan.md)
- Export formats: [docs/integration/sis-formats.md](docs/integration/sis-formats.md)
- Edsembli-alignment research:
  - [docs/edsembli_report_card_requirements_vs_vgreport.md](docs/edsembli_report_card_requirements_vs_vgreport.md)
  - [docs/edsembli_specifics_and_numbers.md](docs/edsembli_specifics_and_numbers.md)
- Source notes:
  - [sources/edsembli/Edsembli Report Card Software Details.md](sources/edsembli/Edsembli%20Report%20Card%20Software%20Details.md)
  - [sources/edsembli/Edsembli API Access and Data Options.md](sources/edsembli/Edsembli%20API%20Access%20and%20Data%20Options.md)

---

## Current repo touchpoints (discovered)

These are the concrete files that appear to own the behaviors this gameplan touches.

### VGReport (UI)

- [vgreport/src/store/useAppStore.ts](vgreport/src/store/useAppStore.ts)
  - Owns draft shape: `ReportDraft.comments[frame][section]` (already 12 cells)
- [vgreport/src/services/db.ts](vgreport/src/services/db.ts)
  - Tauri DB methods + `DraftRow` wire format
- [vgreport/src/components/SectionEditor.tsx](vgreport/src/components/SectionEditor.tsx)
  - Slot capture + calls `render_comment`
- [vgreport/src/components/Preview.tsx](vgreport/src/components/Preview.tsx)
  - Current export implementation (CSV + Print/PDF)
- [vgreport/src/constants.ts](vgreport/src/constants.ts)
  - Canonical frame + section lists used across UI
- [vgreport/src/types/index.ts](vgreport/src/types/index.ts)
  - `FrameId`, `SectionId`, `CommentDraft`, `ReportDraft`

### VGReport (Tauri backend / SQLite)

- [vgreport/src-tauri/src/lib.rs](vgreport/src-tauri/src/lib.rs)
  - SQLite schema includes `drafts` with `(student_id, report_period_id, frame, section)` unique key
  - This already models the 12 cells structurally, but does not store “completion state” or supporting ECE notes

### Sidecar engine (template rendering + validation)

- [sidecar/main.py](sidecar/main.py)
  - IPC methods: `health`, `list_templates`, `get_template`, `render_comment`, `debug_info`
- [lib/assembly.py](lib/assembly.py)
  - Slot-fill + basic per-section length warnings
- [taxonomy/slot_guidance.yaml](taxonomy/slot_guidance.yaml)
  - Canonical slot validation rules (referenced by assembly)
- [sidecar/embedded_templates.py](sidecar/embedded_templates.py)
  - Auto-generated from `templates/comment_templates.yaml`

### Contracts

- [contracts/ipc-request.schema.json](contracts/ipc-request.schema.json)
- [contracts/ipc-response.schema.json](contracts/ipc-response.schema.json)
- [contracts/render-comment-params.schema.json](contracts/render-comment-params.schema.json)

---

## Review notes: gaps, blockers, and recommendations (2026-01-12)

This section captures gaps/blockers found by comparing repo reality to the plan.

### R1. Canonical IDs vs VGReport IDs are currently mismatched (blocker)

What we have today:
- Canonical taxonomy uses:
  - Frames: `frame.belonging`, `frame.self_regulation`, `frame.literacy_math`, `frame.problem_solving` (see [taxonomy/frames.yaml](taxonomy/frames.yaml))
  - Sections: `key_learning`, `growth`, `next_steps` (see [taxonomy/col-sections.yaml](taxonomy/col-sections.yaml))
- VGReport UI uses:
  - Frames: `belonging_and_contributing`, `self_regulation_and_well_being`, `demonstrating_literacy_and_mathematics_behaviors`, `problem_solving_and_innovating`
  - Sections: `key_learning`, `growth_in_learning`, `next_steps_in_learning`

Why it matters:
- Canonical board configs and schemas can’t be consumed directly by VGReport without a mapping layer.
- Exports and validation rules will drift unless the mapping is explicit.

Recommendation:
- Add an explicit ID mapping/normalization decision in Phase K0 (see K0.3) and treat it as a prerequisite for box-fit config and exports.

### R2. “12-box Kindergarten” vs “3-section assembled comment” docs are drifting (gap)

The canonical guidance in [guidance/comment-assembly.md](guidance/comment-assembly.md) defines a 3-section assembled comment (`key_learning`, `growth`, `next_steps`).

VGReport’s Kindergarten UX is a 12-box workflow (4 frames × 3 sections).

Recommendation:
- Decide explicitly whether canonical assembly constraints apply per-frame, across all 12 boxes, or only to CLI/template-bank workflows.
- Treat this as a prerequisite for “soft guardrails”, box-fit, and export specs.

### R3. SIS export target is under-specified (blocker)

We need two distinct “golden outputs” to avoid building the wrong thing:
1. **Clipboard-per-box** export (paste into a live form)
2. **CSV 12-box** export (bulk operations)

Each golden output should specify: exact columns/order, encoding (BOM yes/no), line endings, escaping rules, and field naming (canonical vs VGReport).

### R4. Board config consumption ownership is unclear (gap)

Today:
- Canonical board schema does not model box dimensions/fonts.
- VGReport’s IDs don’t match canonical schema keys.

Recommendation:
- Decide in K0 whether box-fit inputs are VGReport-only settings (fast path) or a canonical schema extension (reusable path), and document the intended integration path.

### R5. ADR + versioning triggers should be explicit (gap)

Per [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md), significant schema/contract changes should be treated as decision-worthy and versioned.

Recommendation:
- When touching placeholder aliasing or board config schema for layout, add an explicit “ADR required?” check in the plan.

## Phase K0 — Clarify requirements and success metrics

### K0.1 Define “required” vs “recommended” Kindergarten completeness

Deliverable:
- A short addendum section in [docs/requirements.md](docs/requirements.md) (later) expressing MUST/SHOULD/MAY for:
  - 12-field completeness
  - “soft guardrails” heuristics (3-sentence guidance, observation/growth/next-step coverage)
  - box-fit validation rules

Likely files to change (docs-only):
- [docs/requirements.md](docs/requirements.md)
- [guidance/comment-assembly.md](guidance/comment-assembly.md) (if we decide to formalize heuristic targets here)

Gaps/blockers:
- The source notes are secondary summaries; we need to confirm whether “minimum three sentences” is policy, board norm, or just typical practice.

Acceptance criteria:
- A reviewer can answer: “What does the app block vs merely warn about?”

### K0.2 Decide what “Edsembli-aligned export” means for Kindergarten

Decision to record:
- Is our export target:
  - template-bank import (comment banks),
  - assembled comments per student, or
  - both?

Gaps/blockers:
- Kindergarten entry shape in Edsembli is not yet verified (field names/columns, per-frame fields, etc.).

Acceptance criteria:
- One chosen “golden” export shape is documented (CSV columns / JSON shape / clipboard layout).

Likely files to change (docs-only):
- [docs/integration/sis-formats.md](docs/integration/sis-formats.md)
- [docs/vgreport_kindergarten_alignment_gameplan.md](docs/vgreport_kindergarten_alignment_gameplan.md) (this doc)

### K0.3 Decide canonical identifier strategy (frames + sections)

Decision to record:
- Do we change VGReport IDs to match canonical taxonomy, or introduce a mapping layer?

Minimum deliverable (docs-only):
- A mapping table (VGReport FrameId/SectionId → canonical frame/section keys) that becomes the reference for exports and config.

Proposed mapping (docs-only; implement later):

Frame IDs:

| VGReport `FrameId` | Canonical frame key | Canonical label |
|---|---|---|
| `belonging_and_contributing` | `frame.belonging` | Belonging and Contributing |
| `self_regulation_and_well_being` | `frame.self_regulation` | Self-Regulation and Well-Being |
| `demonstrating_literacy_and_mathematics_behaviors` | `frame.literacy_math` | Demonstrating Literacy and Mathematics Behaviours |
| `problem_solving_and_innovating` | `frame.problem_solving` | Problem Solving and Innovating |

Section IDs:

| VGReport `SectionId` | Canonical section key | Canonical label |
|---|---|---|
| `key_learning` | `key_learning` | Key Learning |
| `growth_in_learning` | `growth` | Growth in Learning |
| `next_steps_in_learning` | `next_steps` | Next Steps in Learning |

Notes:
- This mapping intentionally treats VGReport’s “*_in_learning” keys as UI-friendly labels while keeping canonical keys aligned with [taxonomy/col-sections.yaml](taxonomy/col-sections.yaml).
- If we later decide to rename VGReport keys to canonical keys, this table becomes the migration plan.

Likely files to change (docs-only):
- [docs/vgreport_kindergarten_alignment_gameplan.md](docs/vgreport_kindergarten_alignment_gameplan.md) (this doc)

Acceptance criteria:
- A reviewer can answer: “When we say ‘Growth’, which key do we mean everywhere?”

### K0.4 Resolve “12-box” constraints vs canonical assembly constraints

Decision to record:
- Are the constraints in [guidance/comment-assembly.md](guidance/comment-assembly.md) meant to apply per-frame, across all 12 boxes, or only to non-VGReport workflows?

Likely files to change (docs-only):
- [docs/requirements.md](docs/requirements.md) (if we formalize MUST/SHOULD/MAY for VGReport)
- [guidance/comment-assembly.md](guidance/comment-assembly.md) (if we extend canonical assembly rules to 12 boxes)

Acceptance criteria:
- We have one consistent statement of targets (length/fit/readability) for the Kindergarten UX we’re building.

---

## Phase K1 — Make the 12 inputs first-class (data + contracts + UI)

### K1.1 Data model and persistence (VGReport app)

Work items (planned):
- Ensure the persistence layer models drafts at **frame + section** granularity (12 cells), not only per-student.
- Add an explicit “completion state” per cell (empty/draft/final), independent of length/fit.

Notes from current code:
- The current SQLite + store design already stores drafts at `(student, period, frame, section)` granularity.
- The missing piece is explicit “completion state” (and/or a deterministic completeness algorithm).

Likely files to change (implementation later):
- [vgreport/src/types/index.ts](vgreport/src/types/index.ts) (add completion state to `CommentDraft`, or store it separately)
- [vgreport/src/store/useAppStore.ts](vgreport/src/store/useAppStore.ts) (compute/store completion; UI selectors for the 12-cell grid)
- [vgreport/src/services/db.ts](vgreport/src/services/db.ts) (`DraftRow` needs to include completion state if persisted)
- [vgreport/src-tauri/src/lib.rs](vgreport/src-tauri/src/lib.rs) (DB schema + commands if we persist completion state)
- [vgreport/src/components/Workspace.tsx](vgreport/src/components/Workspace.tsx) (surface a 12-cell completion grid and work queue)
- [vgreport/src/components/Sidebar.tsx](vgreport/src/components/Sidebar.tsx) (optional: show per-student completion)

Gaps/blockers:
- Need to confirm current SQLite schema (actual tables/columns) vs what is described in design docs.
- If we add completion state and/or ECE notes to SQLite, we need a migration strategy for existing local databases.

Acceptance criteria:
- App can show a student’s 12-cell completion grid and compute completion accurately.
- Completion state semantics are defined (what counts as empty/draft/final), including upgrade behavior.

### K1.2 IPC contracts (UI ↔ engine)

Work items (planned):
- If any new engine methods are needed (e.g., box-fit simulation, richer validation), update JSON Schemas in `contracts/` and regenerate TS types.

Likely files to change (implementation later):
- [contracts/ipc-request.schema.json](contracts/ipc-request.schema.json) (add new method names)
- [contracts/ipc-response.schema.json](contracts/ipc-response.schema.json) (if we constrain response shapes)
- [contracts/ipc-error.schema.json](contracts/ipc-error.schema.json) (if adding new error codes)
- [sidecar/main.py](sidecar/main.py) (implement method handlers)
- [vgreport/src/services/sidecar.ts](vgreport/src/services/sidecar.ts) (client wrapper)
- [vgreport/src/contracts/generated.ts](vgreport/src/contracts/generated.ts) (generated; updated via `npm run contracts:gen`)

Gaps/blockers:
- True “box-fit” may require a rendering engine (PDF/Canvas measurement). That likely impacts where the logic lives (UI vs engine).

Acceptance criteria:
- Contracts are versioned, generated types remain in sync, and validation gate passes.

---

## Phase K2 — Live validation: from char-count to “box fit”

### K2.1 Define box-fit strategy (tiered)

Proposed tiering:
- Tier 1 (fast): heuristic warnings (char count, line breaks, sentence count)
- Tier 2 (better): approximate layout measurement using configured font + box dimensions
- Tier 3 (best): render-to-PDF (or equivalent) and measure overflow

Gaps/blockers:
- We do not yet have canonical board-level box dimensions and fonts for the actual printed form.
- Without an official template, Tier 3 is blocked.

Additional blocker discovered:
- The canonical board config schema [schemas/board_config.schema.json](schemas/board_config.schema.json) currently models character limits and export settings, but does not include font/box-dimensions required for true box-fit.

Recommendation:
- Treat “box-fit config schema” as ADR-worthy if done canonically; otherwise document VGReport-local settings as an intentional interim step.

Likely files to change (implementation later):
- [vgreport/src/components/Preview.tsx](vgreport/src/components/Preview.tsx) (replace/augment char count with fit indicator)
- [vgreport/src/components/SectionEditor.tsx](vgreport/src/components/SectionEditor.tsx) (surface “fit” and soft-guardrail warnings per cell)
- [docs/integration/sis-formats.md](docs/integration/sis-formats.md) (document what we mean by “box fit” and how it’s measured)
- Potential schema/config work if we choose to represent box dimensions canonically:
  - [schemas/board_config.schema.json](schemas/board_config.schema.json)
  - [config/boards/tcdsb.yaml](config/boards/tcdsb.yaml)
  - [config/boards/ncdsb.yaml](config/boards/ncdsb.yaml)

Acceptance criteria:
- User gets immediate feedback that correlates with actual “will this fit?” behavior.

### K2.2 Board-configurable layout inputs

Work items (planned):
- Decide where these live:
  - board config (`config/boards/*.yaml`) (preferred for framework-side), vs
  - VGReport settings (app-side)
- Represent: font style, font size (12pt default), width/height per box.

Gaps/blockers:
- Need a mapping between “board config schema” and what VGReport consumes.

Likely files to change (implementation later):
- [vgreport/src/components/SettingsModal.tsx](vgreport/src/components/SettingsModal.tsx) (if layout is app-configured)
- [vgreport/src/store/useAppStore.ts](vgreport/src/store/useAppStore.ts) (persist layout settings)
- [vgreport/src-tauri/src/lib.rs](vgreport/src-tauri/src/lib.rs) (if layout settings stored in `app_settings`)
- [sidecar/main.py](sidecar/main.py) (if board config is sourced from Python side)

Acceptance criteria:
- Switching board preset changes fit expectations deterministically.

---

## Phase K3 — User Role + Approval Workflow (simplified ECE collaboration)

> **Design decision (2026-01-12):** Replaced "separate ECE notes model" with a simpler "User Role + Approval" approach.
> Rationale: This app runs locally (single machine). A role picker + approval status is simpler than maintaining parallel data models, and it matches real kindergarten workflow where ECEs often draft comments that teachers review.

### K3.1 User Role system

Work items (planned):
- Add a **role picker** on app launch or in Settings: "Who's using VGReport?" → Teacher / ECE (or board-configurable label)
- Store current role in app settings (persisted across sessions)
- Add `author` field to draft records: `'teacher' | 'ece'`
- Add `status` field to draft records: `'draft' | 'approved'`

Workflow:
1. **ECE writes:** Selects "ECE" role, fills slots → saved as `author: 'ece', status: 'draft'`
2. **Teacher reviews:** Selects "Teacher" role, sees ECE work highlighted with badge, can edit or approve → `status: 'approved'`
3. **Export gate:** Only `status: 'approved'` content exports (or warn if exporting unapproved)

Likely files to change (implementation later):
- [vgreport/src/types/index.ts](vgreport/src/types/index.ts) (add `author: 'teacher' | 'ece'` and `status: 'draft' | 'approved'` to `CommentDraft`)
- [vgreport/src-tauri/src/lib.rs](vgreport/src-tauri/src/lib.rs) (SQLite schema: add `author` and `status` columns to `drafts` table; add `current_role` to `app_settings`)
- [vgreport/src/services/db.ts](vgreport/src/services/db.ts) (`DraftRow` wire format update)
- [vgreport/src/store/useAppStore.ts](vgreport/src/store/useAppStore.ts) (role state, computed selectors for "needs review")
- [vgreport/src/components/App.tsx](vgreport/src/components/App.tsx) (role picker modal on launch or settings)
- [vgreport/src/components/Workspace.tsx](vgreport/src/components/Workspace.tsx) (author badge + approval toggle per cell)
- [vgreport/src/components/Preview.tsx](vgreport/src/components/Preview.tsx) (export gate: warn if unapproved content)

### K3.2 Board-configurable role labels

Work items (planned):
- Allow boards to customize role labels (e.g., "DECE" instead of "ECE", "Classroom Teacher" instead of "Teacher")
- Store in board config or app settings

Likely files to change (implementation later):
- [vgreport/src/components/SettingsModal.tsx](vgreport/src/components/SettingsModal.tsx) (role label customization)
- [schemas/board_config.schema.json](schemas/board_config.schema.json) (optional: add role_labels to schema)

Gaps/blockers:
- Need to decide if role labels are app-local settings or canonical board config (recommend app-local for v1).

Acceptance criteria:
- User can switch roles; drafts track who wrote them.
- Teacher can approve/edit ECE drafts before export.
- Export warns or blocks if unapproved content exists.
---

## Phase K4 — Template placeholders and comment-bank alignment

### K4.1 Placeholder policy alignment

Work items (planned):
- Confirm placeholder vocabulary with existing canonical guidance:
  - [taxonomy/slot_guidance.yaml](taxonomy/slot_guidance.yaml)
- Ensure common placeholders are supported in templates and in VGReport slot UI.

Gaps/blockers:
- The Edsembli notes cite {Name} and {He/She}; the framework may prefer different canonical slot names.

Recommendation:
- Prefer an explicit alias policy (e.g., accept `{Name}` as an alias for `{child}` / `{name}`) over changing canonical template content, to minimize churn.
- Treat alias support as a decision (ADR update/new ADR), because it affects validation and interoperability.

Likely files to change (implementation later):
- [taxonomy/slot_guidance.yaml](taxonomy/slot_guidance.yaml) (option: add alias metadata)
- [lib/assembly.py](lib/assembly.py) (option: accept aliases at render time)
- [vgreport/src/components/SectionEditor.tsx](vgreport/src/components/SectionEditor.tsx) (labels/help text for slot inputs)
- [docs/integration/sis-formats.md](docs/integration/sis-formats.md) (document placeholder mapping rules)

Acceptance criteria:
- Clear mapping exists between “teacher mental model placeholders” and canonical slot types.

---

## Phase K5 — Exports shaped to SIS entry

### K5.1 Define a Kindergarten export that maps to 12 cells

Work items (planned):
- Add (or adjust) an export format in [docs/integration/sis-formats.md](docs/integration/sis-formats.md) that is explicitly:
  - Kindergarten-only
  - 12-cell structured (frame × section)
  - consistent with encoding requirements (UTF-8 BOM, CRLF) where relevant

Gaps/blockers:
- Need to verify whether Edsembli imports accept multi-field “structured Kindergarten” CSV, or whether the workflow is paste-per-box.

Likely files to change (implementation later):
- [vgreport/src/components/Preview.tsx](vgreport/src/components/Preview.tsx) (export shape; BOM/CRLF expectations; “12-box” outputs)
- [docs/integration/sis-formats.md](docs/integration/sis-formats.md) (spec the exact CSV columns / clipboard layout)

Known mismatch to resolve:
- [docs/integration/sis-formats.md](docs/integration/sis-formats.md) states “UTF-8 with BOM” is recommended for Excel/Edsembli workflows; the current VGReport CSV export is not documented as adding BOM.

Acceptance criteria:
- A teacher can export and do minimal manual work to enter the 12 pieces into the SIS.

---

## Phase K6 — Testing, QA, and acceptance

### K6.1 QA checklist (Kindergarten alignment)

Work items (planned):
- Add a QA checklist to VGReport docs describing:
  - completeness behavior (what’s required)
  - fit behavior (what’s warning vs blocking)
  - exports (golden file examples)

Gaps/blockers:
- Need real teacher feedback to validate heuristics.

Likely files to change (implementation later):
- [docs/TESTING.md](docs/TESTING.md) (if we add new test expectations for exports/fit)
---

## Synergy with Frontend Gameplan (UI/UX hardening)

The Kindergarten alignment work overlaps significantly with tasks in [docs/frontend_gameplan.md](docs/frontend_gameplan.md) Phase 3.8 (Hardening) and Phase 4 (Testing). To avoid rework and ensure a cohesive UX, certain tasks should be bundled together.

### S1. Export system (K5 + 3.8.5 + Export Center concept)

**Alignment need:** K5 requires a defined "golden" 12-box export (CSV columns, clipboard-per-box, BOM, escaping).

**Frontend gameplan overlap:** 3.8.5 (Export formatting requirements) addresses CSV columns, escaping, Print/PDF styling.

**Design reference:** [docs/frontend.md](docs/frontend.md) describes an **Export Center with presets** (PDF per student, combined PDF, CSV, clipboard).

Recommendation — bundle into one effort:
- Design the Export Center modal (presets for Kindergarten: CSV 12-box, clipboard-per-box, print/PDF, combined PDF).
- Spec each preset's exact output format in [docs/integration/sis-formats.md](docs/integration/sis-formats.md).
- Implement UTF-8 BOM + CRLF as a toggle (or default for Edsembli preset).
- Implement file naming convention options ("StudentLast, StudentFirst — Term — Frame.csv").
- Write tests for golden exports (K6.1).

### S2. Completion grid + Work Queue (K1 + frontend "Progress + Work Queue" concept)

**Alignment need:** K1 adds explicit completion state per cell (empty/draft/final) and a 12-cell completion grid.

**Design reference:** [docs/frontend.md](docs/frontend.md) Section 4A recommends:
- **Work Queue view** (Incomplete, Flagged, Needs Review, Recently Edited).
- **Per-student completion indicator** (e.g., "9/12 boxes filled").
- **Period/class progress bar** ("22/28 students complete").

Recommendation — bundle into one effort:
- Model completion state (empty/draft/final) per cell.
- Surface a **Student Completion Grid** (4 frames × 3 sections) with visual status.
- Add a **Work Queue filter** (Incomplete, Needs Review) to the sidebar.
- Add a **Class Progress summary** ("12 complete, 8 in progress, 5 not started").
- Update autosave to track completion transitions (3.8.6 Data integrity overlap).

### S3. Validation feedback consistency (K2 + 3.8.1 + accessibility)

**Alignment need:** K2 introduces box-fit and soft-guardrail warnings (length, sentence count, coverage).

**Frontend gameplan overlap:** 3.8.1 (Robust error handling) + 3.8.3 (Accessibility pass).

**Design reference:** [docs/frontend.md](docs/frontend.md) Section 4C recommends:
- Visual hierarchy: blockers (red), warnings (amber), info (grey).
- "Export readiness checklist" (what blocks vs what warns).
- Accessible labels, focus states, keyboard nav.

Recommendation — bundle into one effort:
- Define a **validation severity taxonomy** (error = blocks export; warning = shown but not blocking; info = tip).
- Apply consistent visual language across SectionEditor, Preview, and Export Center.
- Ensure all validation messages have accessible labels + focus rings.
- Document "what blocks vs what warns" in [docs/requirements.md](docs/requirements.md) (K0.1 deliverable).

### S4. User Role + Approval Workflow (K3 + simplified collaboration)

> **Updated (2026-01-12):** Changed from "ECE notes model" to "User Role + Approval" per design decision in K3.

**Alignment need:** K3 adds Teacher/ECE role switching with approval workflow.

**Design reference:** [docs/frontend.md](docs/frontend.md) Section 4B recommends ECE collaboration. Our simplified approach:
- **Role picker** on launch or in settings (Teacher / ECE)
- **Author badge** on drafts showing who wrote each cell
- **Approval toggle** for teacher to approve ECE drafts before export

Recommendation — bundle into one effort:
- Add `author` and `status` fields to draft records.
- Surface author badge + approval toggle in Workspace.
- Add export gate (warn if unapproved content).
- Role labels configurable in Settings (board terminology varies).

### S5. Term continuity + prior-term reference (design-only for now)

**Design reference:** [docs/frontend.md](docs/frontend.md) Section 4B recommends:
- **"Compare to Fall" panel** (side-by-side Fall/Feb/June for current student).
- **Copy from prior term and adjust** workflow.

Recommendation — design now, implement later:
- This is not strictly required for Edsembli alignment but is high-ROI for kindergarten teachers.
- Ensure data model supports `report_period` correctly (already does).
- Defer implementation to a follow-on sprint, but capture wireframe/spec now so it doesn't conflict with K1 schema work.

### S6. Testing + packaging synergy (K6 + 4.1–4.4)

**Alignment need:** K6.1 requires golden-file tests for exports and predictable validation.

**Frontend gameplan overlap:** 4.1 (Unit tests), 4.2 (Sidecar integration tests), 4.3 (E2E tests), 4.4 (Windows installer).

Recommendation — bundle into one effort:
- Write unit tests for completion logic + validation severity.
- Write integration tests for export BOM/CRLF/columns.
- Add a "golden class" fixture (synthetic, no-PII) and run export assertions.
- Include new features in installer smoke test (completion grid renders, export works).

### S7. Keyboard + accessibility pass (3.8.3 + frontend "keyboard-first" concept)

**Design reference:** [docs/frontend.md](docs/frontend.md) recommends:
- `Alt+N/P` next/prev student.
- `Ctrl+K` quick student search.
- True keyboard loop with predictable tab order.
- Proper labels (not placeholder-only inputs).

Recommendation — bundle alongside K1/K2 work:
- As we build the 12-cell grid and validation feedback, include accessible labels + keyboard shortcuts.
- Audit new UI against WCAG 2.1 AA (focus states, color contrast, screen reader labels).

---

## Consolidated implementation order (recommended)

Based on synergies, a suggested phased approach:

| Phase | Alignment tasks | Frontend hardening tasks | Rationale |
|-------|-----------------|--------------------------|-----------|
| **Phase A (Requirements)** | K0.1, K0.2, K0.3, K0.4 | — | Lock specs before building. |
| **Phase B (Core data + role system)** | K1.1, K1.2 (if needed), K1.3 (migration), K3.1 (User Role), T1.1, T1.2, T1.4 | 3.8.6 (Data integrity) | Schema/migrations + role semantics must land before completion + export gating. |
| **Phase C (Validation UX)** | K2.1, K2.2, T1.3, T2.4 | 3.8.1 (Error handling), 3.8.3 (Accessibility) | Consistent validation patterns + keyboard/accessibility. |
| **Phase D (Supporting features)** | K3.2 (role labels), K4.1, T2.1, T2.2 | — | Role terminology + placeholder/alias policy + queue/modifiers. |
| **Phase E (Export system)** | K5.1, T3.3 | 3.8.5 (Export formatting) | Export Center + golden formats. |
| **Phase F (QA + release)** | K6.1 | 4.1, 4.2, 4.3, 4.4 | Tests + installer + user docs. |

---

## High-ROI Teacher Convenience Features (additional recommendations)

This section identifies features from [docs/frontend.md](docs/frontend.md) that are **not strictly required for Edsembli alignment** but would significantly improve teacher convenience and time-saving. These are prioritized by impact vs implementation effort.

### Priority Tier 1: Implement now (high impact, moderate effort)

These features directly reduce teacher time-per-student and should be bundled with Phase B/C work.

#### T1.1 Next/Previous Student navigation

**What:** Add `Alt+N` / `Alt+P` (or arrow buttons) to move between students without leaving the keyboard.

**Why (time-saving):** Teachers write reports in linear order. Mouse-clicking the sidebar for each of 25 students is slow. Linear navigation with keyboard = ~2 seconds saved per student × 25 = ~1 minute per frame × 4 frames = **~4 minutes saved per class**.

**Current state:** Implemented (Phase B).

**Effort:** Low (UI buttons + hotkey handler + store method).

Acceptance criteria:
- `Alt+N` selects next student in roster order; wraps at end.
- `Alt+P` selects previous student; wraps at start.
- Hotkeys do not trigger while typing in a text input.

#### T1.2 "Resume where I left off" on app launch

**What:** Remember the last-selected student and frame, and restore on next launch.

**Why (time-saving):** Teachers close the app mid-session (prep period ends, laptop sleeps). Reopening should put them exactly where they were, not at the empty "Select a student" screen.

**Current state:** Implemented (Phase B).

**Effort:** Low (persist `selectedStudentId` + `selectedFrameId` to SQLite or localStorage; restore on mount).

Acceptance criteria:
- On relaunch, app restores last-selected student + frame.
- If last-selected student no longer exists, app falls back safely.

#### T1.3 Quick student search (`Ctrl+K`)

**What:** Global search modal that fuzzy-matches student names and jumps directly to them.

**Why (time-saving):** With 25+ students, scanning a list is slower than typing "Aid" to jump to "Aiden." Teachers already expect this pattern from other apps.

**Current state:** Implemented (Phase C).

**Effort:** Medium (command palette component + fuzzy search logic).

Acceptance criteria:
- `Ctrl+K` opens search; typing filters students; `Enter` selects.
- Escape closes without changing selection.

#### T1.4 Class progress summary (sidebar header)

**What:** Show "12/25 students complete" or "48/300 boxes filled" at the top of the sidebar.

**Why (time-saving):** Teachers need to know "how much is left?" at a glance without counting manually. Reduces anxiety and helps them estimate remaining work time.

**Current state:** Implemented (Phase B).

**Effort:** Low (computed selector + display in sidebar header).

Acceptance criteria:
- Sidebar shows `X/Y students complete` and updates live.
- “Complete” definition matches Phase A completeness semantics.

### Priority Tier 2: Implement soon (high impact, higher effort)

These features address deeper workflow pain points and should be designed in Phase A but implemented in Phase D or later.

#### T2.1 Work Queue filters

**What:** Sidebar filters: "Incomplete only", "Needs review", "Flagged", "Recently edited".

**Why (time-saving):** Late in the reporting cycle, most students are done. Teachers want to see only who's left, not scroll past 20 green checkmarks. Also supports "IEP students first" or "ELL students first" workflows.

**Current state:** Implemented (Phase D).

**Effort:** Medium (filter state + UI toggles + computed roster).

#### T2.2 Developmental modifier picker

**What:** A small dropdown or button group offering common kindergarten modifiers: "beginning to", "with support", "with prompting", "independently", "consistently".

**Why (time-saving):** These phrases appear in nearly every kindergarten comment. Instead of typing "with support" 50+ times, teacher clicks once. Also ensures consistency.

**Current state:** Implemented (Phase D).

**Effort:** Medium (modifier list + insertion into slot field or template output).

#### T2.3 "Copy to all students" for common observations

**What:** For a filled slot value, offer "Apply to other students" with checkboxes, then personalize per student.

**Why (time-saving):** When 8 students all did the same activity (e.g., "During block play, built a tower"), teachers currently retype or copy-paste for each. A bulk-apply + personalize flow saves significant time.

**Current state:** Not implemented.

**Effort:** High (bulk selection UI + draft creation loop + personalization pass).

#### T2.4 Repetition warning

**What:** Show a subtle indicator when the same rendered text appears across multiple students (e.g., "Used in 5 students").

**Why (time-saving):** Teachers worry about sounding repetitive. A warning lets them intentionally vary phrasing where it matters, without manually comparing 25 reports.

**Current state:** Implemented (Phase C).

**Effort:** Medium (cross-student text comparison + UI indicator).

### Priority Tier 3: Design now, implement later (high value, largest effort)

These require more architectural work or design validation but should be wireframed now.

#### T3.1 Observation capture mode (Evidence Drawer)

**What:** Quick-add timestamped observations per student throughout the term (before report writing). When writing, teacher sees their collected observations and can pull from them.

**Why (time-saving):** Teachers arrive at report time with sticky notes and scattered memories. An evidence drawer reduces "What did I notice about this kid?" to a simple review.

**Current state:** Schema exists (`evidence_snippets` table) but no UI.

**Effort:** High (capture UI + context tags + linkage to writing flow).

#### T3.2 Term continuity view ("Compare to Fall")

**What:** Side-by-side display of Fall / Feb / June comments for the current student.

**Why (time-saving):** Growth language requires knowing prior state. Teachers currently open old PDFs or scroll through notes. A built-in comparison saves lookup time and improves narrative continuity.

**Current state:** Data model supports it; no UI.

**Effort:** High (multi-term display component + navigation).

#### T3.3 Export Center with presets

**What:** A dedicated export modal with saved presets: "CSV for Edsembli", "PDF per student", "Combined PDF", "Clipboard per box".

**Why (time-saving):** Teachers export multiple times (draft review, final submission, backup). Reconfiguring export settings each time is friction. Presets = one click.

**Current state:** Implemented (Phase E) with presets + Export Center modal.
Missing vs original wishlist: Combined PDF preset + richer preset management (multiple saved presets / naming).

**Effort:** High (modal + preset storage + multiple export paths).

### Recommendation: What to implement with Phase B/C

To maximize teacher time-saving without delaying the alignment work, bundle these with the existing phases:

| Phase | Add these convenience features |
|-------|-------------------------------|
| **Phase B** | T1.1 (Next/Prev), T1.2 (Resume session), T1.4 (Class progress) |
| **Phase C** | T1.3 (Quick search), T2.4 (Repetition warning) |
| **Phase D** | T2.1 (Work Queue filters), T2.2 (Modifier picker) |
| **Phase E** | T3.3 (Export Center presets) |

Defer T2.3 (Copy to all), T3.1 (Evidence Drawer), and T3.2 (Term continuity) to a follow-on sprint—they're valuable but not blocking alignment or core UX.

---

## Risks, gaps, and blockers (summary)

- **Unverified Edsembli Kindergarten entry/export shape**: we have requirements prose, but not the exact field mapping.
- **Box-fit fidelity depends on real form templates**: without official printed layout specs, perfect WYSIWYG is blocked.
- **Board variability**: fonts/box sizes differ; requires a config strategy and defaults.
- **Placeholder naming mismatch**: canonical slot naming may diverge from {Name}/{He/She}; needs explicit mapping.
- **Canonical taxonomy vs VGReport ID mismatch**: frames/sections currently use different keys across canonical docs and the UI.
- **Spec drift risk**: canonical assembly rules are 3-section-oriented while the Kindergarten UX is 12 boxes.
- **Missing/unclear board preset for Edsembli-specific limits**: [docs/integration/sis-formats.md](docs/integration/sis-formats.md) references an `edsembli.yaml` preset that does not appear to exist under [config/boards/](config/boards).

---

## Critical review: Phase ordering and dependencies (2026-01-12)

This section identifies issues with the current phase ordering and recommends adjustments.

### Issue 1: Phase A has unresolved decision dependencies

**Problem:** K0.1-K0.4 are all "decisions to record" but have no clear owner or deadline. Without these decisions locked, Phases B-E will build on unstable foundations.

**Recommendation:** Add explicit decision gates:
- K0.1 + K0.2 -> MUST complete before K1.1 (data model needs to know what "complete" means)
- K0.3 -> MUST complete before K5.1 (export needs to know which IDs to use)
- K0.4 -> SHOULD complete before K2.1 (validation needs to know constraint scope)

### Issue 2: User Role (K3) is more foundational than currently positioned

**Problem:** K3 (User Role + Approval) is positioned after K2 (Validation), but author/status fields affect:
- Data model (K1.1)
- Completion semantics (what counts as "complete" if ECE wrote but teacher hasn't approved?)
- Export gating (K5.1)

**Recommendation:** Move K3.1 (User Role system) into Phase B alongside K1.1. The role picker and author/status fields are data model concerns, not validation concerns.

### Issue 3: Convenience features (T1.x) lack acceptance criteria

**Problem:** T1.1-T1.4 are described but have no acceptance criteria or test expectations.

**Recommendation:** Add acceptance criteria to each T1.x item (e.g., "T1.1 passes when: Alt+N moves to next student in sidebar order; wraps at end of list").

### Issue 4: Migration strategy is mentioned but not planned

**Problem:** K1.1 mentions "migration strategy for existing local databases" but no phase or task addresses it.

**Recommendation:** Add K1.3 (SQLite migration) as a required subtask of K1.1, with explicit schema version bumping and upgrade logic.

### Revised phase order (recommended)

| Phase | Tasks | Rationale |
|-------|-------|-----------|
| **Phase A** | K0.1, K0.2, K0.3, K0.4 | Lock decisions. Gate: all four decisions documented before proceeding. |
| **Phase B** | K1.1, K1.2 (if needed), K1.3 (migration), K3.1 (User Role), T1.1, T1.2, T1.4 | Data model + role system + core convenience features. |
| **Phase C** | K2.1, K2.2, T1.3, T2.4 | Validation UX + search + repetition warning. |
| **Phase D** | K3.2 (role labels), K4.1, T2.1, T2.2 | Placeholder aliasing + work queue filters + modifier picker. |
| **Phase E** | K5.1, T3.3 | Export system + presets. |
| **Phase F** | K6.1 | QA, golden tests, installer. |

---

## Next action (smallest first step)

1. **Lock K0.2 first:** Decide the "golden" Kindergarten export target and document its exact shape (columns/fields) in [docs/integration/sis-formats.md](docs/integration/sis-formats.md).
2. **Then K0.3:** Confirm the ID mapping table and commit it.
3. **Then K0.1 + K0.4:** Define completeness semantics and constraint scope.

Only after Phase A is complete should implementation begin.

---

## Execution Prompt (for AI-assisted implementation)

The following prompt is designed to guide an AI coding assistant through implementing this gameplan. It follows senior prompt engineering principles: explicit constraints, phased execution, validation gates, and rollback awareness.

```yaml
# VGReport Kindergarten Alignment Execution Prompt
# Version: 1.0.0
# Compatible with: docs/vgreport_kindergarten_alignment_gameplan.md v0.2.1

system_context: |
  You are implementing the VGReport Kindergarten Alignment Gameplan.
  This is a Tauri + React + TypeScript desktop application with a Python sidecar engine.

  CRITICAL CONSTRAINTS:
  1. Follow docs/CONTRIBUTING.md for all changes (versioning, ADR triggers, commit conventions).
  2. Update index.md when adding new canonical files.
  3. Never store PII in the repository; the app stores PII locally only.
  4. Run validation gates after each phase: `.\check --quick` must pass.
  5. If a phase fails validation, stop and report before proceeding.

phase_gates:
  phase_a:
    name: "Requirements Lock"
    tasks:
      - id: K0.1
        description: "Define completeness semantics (MUST/SHOULD/MAY) in docs/requirements.md"
        validation: "docs/requirements.md contains 'Kindergarten Completeness' section with RFC 2119 language"
        files_to_modify:
          - docs/requirements.md
      - id: K0.2
        description: "Document golden export shape in docs/integration/sis-formats.md"
        validation: "sis-formats.md contains 'VGReport Kindergarten 12-Box Exports (Golden Outputs)' section with exact CSV columns"
        files_to_modify:
          - docs/integration/sis-formats.md
      - id: K0.3
        description: "Confirm ID mapping table (already in gameplan); no code changes"
        validation: "Mapping table reviewed and accepted"
        files_to_modify: []
      - id: K0.4
        description: "Document constraint scope (per-frame vs all 12 boxes)"
        validation: "guidance/comment-assembly.md updated with VGReport applicability"
        files_to_modify:
          - guidance/comment-assembly.md
    gate: "All four decisions documented. Run `\.\check --quick`. Stop if errors."

  phase_b:
    name: "Core Data + Role System"
    depends_on: phase_a
    tasks:
      - id: K1.1
        description: "Add author/status fields to CommentDraft type and store"
        files_to_modify:
          - vgreport/src/types/index.ts
          - vgreport/src/store/useAppStore.ts
      - id: K1.3
        description: "SQLite migration: add author, status columns to drafts table"
        files_to_modify:
          - vgreport/src-tauri/src/lib.rs
          - vgreport/src/services/db.ts
        validation: "Existing drafts load without error after schema change"
      - id: K3.1
        description: "Role picker UI + current_role in app_settings"
        files_to_modify:
          - vgreport/src/components/App.tsx
          - vgreport/src/components/SettingsModal.tsx
          - vgreport/src-tauri/src/lib.rs
      - id: T1.1
        description: "Next/Prev student navigation (Alt+N/P)"
        files_to_modify:
          - vgreport/src/store/useAppStore.ts
          - vgreport/src/components/Workspace.tsx
        acceptance: "Alt+N moves to next student; Alt+P moves to previous; wraps at list boundaries"
      - id: T1.2
        description: "Resume session on launch"
        files_to_modify:
          - vgreport/src/store/useAppStore.ts
          - vgreport/src/App.tsx
        acceptance: "App opens to last-selected student and frame"
      - id: T1.4
        description: "Class progress summary in sidebar header"
        files_to_modify:
          - vgreport/src/components/Sidebar.tsx
        acceptance: "Sidebar shows 'X/Y students complete' based on 12-cell completion"
    gate: "npm run tauri dev launches without error. Manual smoke test: role picker works, navigation works."

  phase_c:
    name: "Validation UX"
    depends_on: phase_b
    tasks:
      - id: K2.1
        description: "Implement tiered validation (char count -> heuristic fit)"
        files_to_modify:
          - vgreport/src/components/SectionEditor.tsx
          - vgreport/src/components/Preview.tsx
      - id: K2.2
        description: "Board-configurable layout inputs (font, box size)"
        files_to_modify:
          - vgreport/src/components/SettingsModal.tsx
          - vgreport/src/store/useAppStore.ts
      - id: T1.3
        description: "Quick student search (Ctrl+K)"
        files_to_modify:
          - vgreport/src/components/CommandPalette.tsx (new)
          - vgreport/src/components/App.tsx
        acceptance: "Ctrl+K opens modal; typing filters students; Enter selects"
      - id: T2.4
        description: "Repetition warning"
        files_to_modify:
          - vgreport/src/store/useAppStore.ts
          - vgreport/src/components/SectionEditor.tsx
        acceptance: "If same rendered text appears in 3+ students, show indicator"
    gate: "Validation feedback visible in UI. Warnings appear correctly."

  phase_d:
    name: "Supporting Features"
    depends_on: phase_c
    tasks:
      - id: K3.2
        description: "Board-configurable role labels"
        files_to_modify:
          - vgreport/src/components/SettingsModal.tsx
      - id: K4.1
        description: "Placeholder alias support"
        files_to_modify:
          - taxonomy/slot_guidance.yaml
          - lib/assembly.py
          - vgreport/src/components/SectionEditor.tsx
      - id: T2.1
        description: "Work Queue filters (Incomplete, Needs Review)"
        files_to_modify:
          - vgreport/src/components/Sidebar.tsx
          - vgreport/src/store/useAppStore.ts
      - id: T2.2
        description: "Developmental modifier picker"
        files_to_modify:
          - vgreport/src/components/SectionEditor.tsx
    gate: "Filters work. Modifier picker inserts text correctly."

  phase_e:
    name: "Export System"
    depends_on: phase_d
    tasks:
      - id: K5.1
        description: "Kindergarten 12-box export (CSV + clipboard)"
        files_to_modify:
          - vgreport/src/components/Preview.tsx
          - docs/integration/sis-formats.md
        validation: "Export matches golden output defined in K0.2"
      - id: T3.3
        description: "Export Center with presets"
        files_to_modify:
          - vgreport/src/components/ExportCenter.tsx (new)
          - vgreport/src/components/Preview.tsx
    gate: "Export produces correct CSV. Presets save and load."

  phase_f:
    name: "QA + Release"
    depends_on: phase_e
    tasks:
      - id: K6.1
        description: "Golden tests for exports + validation"
        files_to_modify:
          - vgreport/src/components/Sidebar.test.tsx
          - vgreport/src/store/useAppStore.test.ts
          - tests/test_export_golden.py (new)
    gate: "pytest passes. npm test passes. Installer builds."

execution_rules:
  - Complete one phase before starting the next.
  - Run `.\check --quick` after each task.
  - If validation fails, fix before proceeding.
  - Commit after each task with conventional commit message.
  - Update CHANGELOG.md for user-facing changes.
  - If a task requires an ADR (per CONTRIBUTING.md), create it before implementing.

rollback_strategy:
  - Each phase should be a separate branch.
  - If a phase fails QA, revert to the previous phase's branch.
  - Never force-push to main.

success_criteria:
  - All phases complete with green gates.
  - App launches and allows full Kindergarten workflow.
  - Export matches golden outputs.
  - Teachers can switch roles; ECE drafts require approval.
  - Convenience features (navigation, search, progress) work.
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-11 | Initial draft |
| 0.1.1 | 2026-01-12 | Added review notes, ID mapping tables, synergy analysis |
| 0.1.2 | 2026-01-12 | Added High-ROI Teacher Convenience Features section |
| 0.2.0 | 2026-01-12 | Replaced K3 "ECE notes model" with simpler "User Role + Approval" approach; added critical review; added execution prompt |
| 0.2.1 | 2026-01-12 | Aligned consolidated phase order with revised order; removed stale "ECE notes" phrasing; added acceptance criteria for Tier 1 convenience items; aligned execution prompt gate command |
| 0.2.2 | 2026-01-12 | Phase B implementation: role picker (Teacher/ECE), per-box author/status persistence + migration, approval toggle UI, minimal unit tests, and contracts type generation |
