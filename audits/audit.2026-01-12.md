---
id: audit.2026-01-12
type: audit
title: VGReport Frontend Phases vs Implementation Gaps
status: draft
version: 0.1.0
updated: 2026-01-12
refs: []
tags:
  - audit
  - vgreport
  - design-drift
---

# VGReport Frontend Phases vs Implementation Gaps (2026-01-12)

## 1) Scope

This audit maps the previously identified **design-vs-implementation gaps** to the phased plan in [docs/frontend.md](../docs/frontend.md).

It answers:
- Which remaining gaps are explicitly covered by the plan?
- Which gaps are outside the frontend phases (docs/governance drift)?

## 2) Remaining gaps (from prior audit)

### A. Missing `/contracts/` + schema→TypeScript generation
- **Design intent**: JSON Schema is the source of truth for UI ↔ engine IPC contracts; TS types generated from schema; CI guard.
- **Repo reality**: No `contracts/` directory exists yet.

### B. Sidecar “health” startup handshake
- **Design intent**: Frontend spawns sidecar then calls `health` and blocks UI (with error message) if no response in ~5s.
- **Repo reality**:
  - Sidecar implements `health` in `sidecar/main.py`.
  - Frontend init currently does not call `health` (it calls `debug_info` + `list_templates`).

### C. Documentation drift (design-only language, duplicated planning docs)
- **Design intent**: Canonical docs reflect actual repo state.
- **Repo reality**: Some drift remains (notably “design-only” scope language vs implemented VGReport, and planning doc overlap between ROADMAP/GAMEPLAN).

## 3) Mapping gaps to `docs/frontend.md` phases

### Covered by frontend phases

- **A. `/contracts/` + schema→TS generation**
  - Covered explicitly by:
    - Section 3C “Type Synchronization (Python ↔ UI)” and contract policy.
    - Phase 1.7 “Add contract generation step (Python → TS types)”.
  - Net: **Yes — the phases explicitly cover this gap**, but it’s still unimplemented in repo.

- **B. Health handshake**
  - Covered explicitly by:
    - Section 3D “Startup Handshake” and `health` method.
    - Phase 1.5 “Implement Tauri IPC bridge (React ↔ engine)”.
  - Net: **Yes — the phases cover this gap**, but current `SidecarClient.init()` doesn’t enforce it yet.

- **Packaging / sidecar correctness (adjacent gap)**
  - Covered by:
    - Phase 1.4 “Package the Python engine as a standalone sidecar binary”.
  - Net: this is already largely in place in repo; remaining issues here are mostly process/dev-experience oriented.

### Not covered by frontend phases (separate governance/doc work)

- **C. Documentation drift / planning doc reconciliation**
  - This is not a “frontend build phase” issue.
  - It should be handled as:
    - a docs reconciliation task (update canonical docs to match reality), and/or
    - an explicit decision log entry in `docs/discussion.md`.

## 4) Additional drift surfaced while mapping

- `docs/frontend.md` Phase 1.1 references a `/frontend/` scaffold.
  - Repo uses `vgreport/` as the app workspace.
  - This is a doc-path drift, not a functional gap.

## 5) Conclusion

- The **frontend phase plan does cover the key technical gaps** that block a “100% aligned” claim:
  - `/contracts/` + schema→TS generation
  - startup `health` handshake enforcement
- The remaining **non-technical alignment gaps** (doc drift, ROADMAP vs GAMEPLAN overlap) are not addressed by frontend phases and should be reconciled in the canonical documentation.
