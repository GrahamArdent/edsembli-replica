---
id: doc.vgreport.frontend_gameplan
type: document
title: VGReport – Frontend Implementation Gameplan
version: 0.5.0
status: draft
tags: [technical, governance]
refs: []
updated: 2026-01-12
---

# VGReport – Frontend Implementation Gameplan

This document tracks execution work for the VGReport desktop app frontend and its UI↔engine integration.

It is paired with the design spec:
- `docs/frontend.md` (design)

## Phase 0: Prerequisites (Week 0)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 0.1 | Install Rust toolchain (Rustup) | `rustc` + `cargo` available in terminal | ✅ Done |
| 0.2 | WebView2 detection + install plan | Evergreen WebView2 policy documented | ✅ Done |
| 0.3 | Choose engine shipping approach | PyInstaller sidecar; minimal deps in `sidecar/engine-requirements.txt` | ✅ Done |
| 0.4 | Lock contract generation approach | Manual JSON Schema → TypeScript | ✅ Done |
| 0.5 | Define IPC protocol specification | Protocol documented in design doc | ✅ Done |
| 0.6 | Create LICENSE file | MIT License in repo root | ✅ Done |

### Phase 0 Exit Criteria

Before starting Phase 1, ALL of the following must be true:

- [x] `rustc --version` works in a new terminal
- [x] `cargo --version` works in a new terminal
- [x] `LICENSE` exists in repo root (MIT)
- [x] `sidecar/engine-requirements.txt` exists
- [x] IPC protocol documented
- [x] JSON Schema contract approach documented

## Phase 1: Foundation (Week 1-2)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 1.1 | Initialize Tauri + Vite + React + TypeScript project | `vgreport/` scaffold | ✅ Done |
| 1.2 | Configure Tailwind CSS + Shadcn/UI | Base styling system | ✅ Done |
| 1.3 | Create Python sidecar wrapper for existing `lib/` logic | `sidecar/main.py` | ✅ Done |
| 1.4 | Package the Python engine as a standalone sidecar binary | `vgreport-engine.exe` (dev build) | ✅ Done |
| 1.5 | Implement Tauri IPC bridge (React ↔ engine) | Stable JSON message protocol + health handshake | ✅ Done |
| 1.6 | Set up SQLite database with schema | Local DB persisted in app data dir + CRUD commands | ✅ Done |
| 1.7 | Add contract generation step (JSON Schema → TS types) | `/contracts` + generated TS types + drift gate | ✅ Done |
| 1.8 | Build basic layout shell (three-pane) | `<Sidebar />` + `<Workspace />` + `<Preview />` | ✅ Done |

## Phase 2: Core Editing Experience (Week 3-4)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 2.1 | Student Roster sidebar with CRUD | `<Sidebar />` (add/edit/delete) | ✅ Done |
| 2.2 | Frame Tabs navigation | Implemented in `<Workspace />` | ✅ Done |
| 2.3 | Section Editor with template dropdown | `<SectionEditor />` + `<TemplateSelector />` | ✅ Done |
| 2.4 | Dynamic slot input generation | Slot-driven textarea fields in `<SectionEditor />` | ✅ Done |
| 2.5 | Live Preview panel with real-time rendering | `<Preview />` | ✅ Done |
| 2.6 | Autosave with visual indicator | Zustand + debounce + SQLite writes + save status UI | ✅ Done |
| 2.7 | Character count + validation feedback | Char count + validation display | ✅ Done |

## Phase 3: Polish & Export (Week 5-6)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 3.1 | Onboarding wizard (first-launch flow) | `<OnboardingWizard />` | ✅ Done |
| 3.2 | Settings modal (board selection, theme) | `<SettingsModal />` | ✅ Done |
| 3.3 | PDF export with proper formatting | Print/PDF via browser print window | ✅ Done |
| 3.4 | CSV export for SIS import | CSV (student + class) in `<Preview />` | ✅ Done |
| 3.5 | Keyboard shortcuts (Ctrl+S, Ctrl+Z/Y, Ctrl+,) | Hotkey system in `<App />` | ✅ Done |
| 3.6 | Dark mode | Theme setting + system detection | ✅ Done |
| 3.7 | Undo/Redo stack | Undo/redo in Zustand + UI buttons | ✅ Done |

## Phase 3.8: Hardening (Quality + Edge Cases)

These are not “new features”, but they are the typical remaining work after an MVP exists.

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 3.8.1 | Robust error handling | User-friendly errors for sidecar/db failures; no silent failures | ⏳ Next |
| 3.8.2 | Offline/locked-down environment behavior | Clear messaging when clipboard/print blocked; safe fallbacks | ⏳ Next |
| 3.8.3 | Accessibility pass | Keyboard nav, focus states, labels, dialog semantics | ⏳ Next |
| 3.8.4 | Performance + memory sanity | No runaway logs/timers; bounded in-memory history; stable long sessions | ⏳ Next |
| 3.8.5 | Export formatting requirements | Validate CSV columns + escaping; improve Print/PDF styling/layout | ⏳ Next |
| 3.8.6 | Data integrity guarantees | Ensure autosave flushes on quit/period change; verify draft keying | ⏳ Next |

## Phase 4: Testing & Packaging (Week 7-8)

| Task | Description | Deliverable | Status |
|------|-------------|-------------|--------|
| 4.1 | Unit tests for React components | Vitest + Testing Library | ✅ Started |
| 4.2 | Integration tests for sidecar | `npm run sidecar:smoke` + (later) pytest | ✅ Started |
| 4.3 | End-to-end test: full report generation | Tauri/WebView-oriented e2e + rationale doc (`docs/tauri_e2e_testing.md`) | ✅ Started |
| 4.4 | Build Windows installer (`.msi`) | `tauri build` output | ⏳ Next |
| 4.5 | Build macOS installer (`.dmg`) | `tauri build` output | ⏳ Later |
| 4.6 | User documentation / Help system | In-app help + guide | ⏳ Next |
| 4.7 | Beta testing with real teacher | Feedback loop | ⏳ Later |

## Next Immediate Action (repo reality)

1. Stabilize the dev workflow (treat success as: command keeps running + app window stays open):
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build_sidecar.ps1`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/tauri_dev.ps1`
2. Move into Phase 4 (Testing & Packaging):
   - Add minimal React unit tests (Vitest) for core flows (roster CRUD, template selection, autosave)
   - Add a smoke integration check for sidecar (health + list_templates)
