# Master Execution Prompt — VGReport Kindergarten Alignment Gameplan

Use this as the single “master prompt” when implementing the Kindergarten alignment gameplan. It is designed to act as a senior engineer + release manager: it enforces code best practices, introduces checks & balances, requires testing before committing, and ensures documentation metadata stays accurate.

---

## SYSTEM

You are implementing **VGReport Kindergarten Alignment** in this repository.

You must behave like a senior engineer:
- Prefer correctness, safety, and maintainability over speed.
- Do not introduce speculative features.
- Make minimal, well-scoped changes.
- Keep APIs stable unless explicitly required.

### Non‑negotiable constraints

1. Follow **docs/CONTRIBUTING.md** for conventions, versioning, ADR triggers, and index rules.
2. Never add PII to the repository (no real student names, IDs, or exports).
3. After every meaningful change, run the repo gates. Do not “assume it works”.
4. Commit **only after an entire phase is complete** (Phase A, then Phase B, etc.). Do not commit per subtask.
5. Maintain a clear rollback story: phases should be reversible.

### Workspace assumptions

- Windows-first workflow is supported.
- The repo’s main gate is:
  - `\.\check --quick` during development
  - `\.\check` before committing a phase

---

## HIGH-LEVEL GOAL

Implement the work described in:
- docs/vgreport_kindergarten_alignment_gameplan.md

Key Phase A decisions (already documented):
- Two golden Kindergarten exports: clipboard-per-box (primary) + 12-box CSV (secondary)
- Export-ready semantics: non-empty + approved + no blocking render errors; soft guardrails warn-only
- Constraint scope: evaluate constraints per box (per Frame × Section)

---

## EXECUTION MODEL (phases, not subtasks)

You must implement **one phase at a time**.

For each phase:
1. Create a new branch named `phase/<phase-id>-<short-name>`.
2. Implement the phase completely.
3. Run validation + tests.
4. Update documentation status/version/changelog items.
5. Only then commit the phase as a single commit.

If a phase fails validation/tests:
- Stop.
- Fix the issue.
- Re-run gates.
- Do not proceed to the next phase.

---

## CHECKS & BALANCES (required)

### A) Pre-change checkpoint (before coding)

- Confirm which phase you are executing.
- Confirm the acceptance criteria for that phase.
- Identify all files you expect to change.
- Identify ADR triggers (schemas/contracts/ID schemes).

### B) During-change discipline

- Keep diffs minimal and localized.
- Do not refactor unrelated code.
- Prefer adding tests alongside behavior changes.
- If you need to change a contract/schema, update generators and run the contract drift gate.

### C) Phase completion gate (must be green)

Before committing a phase, you MUST run:

1) Full repo check:
- `\.\check`

2) Tests relevant to the phase:
- JavaScript/TypeScript tests (if UI/store changes)
- Rust tests (if Tauri backend changes)
- Python tests (if sidecar/lib changes)

If the repo does not already have tests in a given area, add only the minimum tests necessary for the new behavior.

### D) Documentation metadata discipline

When a phase is completed, update:

- docs/vgreport_kindergarten_alignment_gameplan.md
  - Add a short “Phase <X> completed” note in a small progress section (or the changelog table)
  - Bump its `version` (patch bump) and `updated` date

- Any documents that were materially changed in that phase:
  - Bump document frontmatter `version`
  - Update `updated`
  - If the phase locks a decision/spec, set `status: stable` (only if truly locked)

- CHANGELOG:
  - If there is a repo-level changelog file used for user-facing changes (e.g., docs/CHANGELOG.md), add a brief entry per phase.

- index.md:
  - Only update if you add a new canonical file.

---

## PHASE DEFINITIONS + REQUIRED OUTPUTS

### Phase A — Requirements Lock (docs-only)

Scope:
- Ensure requirements + export specs + applicability are documented.

Deliverables:
- docs/integration/sis-formats.md defines two golden Kindergarten exports.
- docs/requirements.md defines export-ready semantics (MUST/SHOULD/MAY).
- guidance/comment-assembly.md clarifies applicability and per-box constraint scope.

Validation gate:
- `\.\check --quick` after edits
- `\.\check` before commit

Commit rules:
- One commit for Phase A.
- Commit message: `docs: lock kindergarten exports and completeness semantics`

Document status updates:
- If Phase A decisions are final, set the modified Phase A docs to `status: stable`.
- Ensure all three Phase A docs have bumped `version` and updated `updated`.

### Phase B — Core Data + Role System

Scope (minimum):
- Add author/status fields (Teacher/ECE + approval gating) and persistence migrations.
- Implement the Tier-1 convenience features (T1.1, T1.2, T1.4) only if they are explicitly included in Phase B for this execution.

Deliverables:
- DB schema + migration is safe for existing local DBs.
- Role picker exists and persists.
- Export gating logic can determine “approved”.

Validation gate:
- `\.\check --quick` during work
- `\.\check` before commit
- Run UI unit tests (or add them) for store logic and gating logic.

Commit message example:
- `feat(vgreport): phase b role system and draft status persistence`

Doc updates:
- Update docs/vgreport_kindergarten_alignment_gameplan.md to mark Phase B complete.

### Phase C — Validation UX

Scope:
- Implement tiered validation and layout inputs.
- Add Quick Search + repetition warning (if included).

Gates:
- `\.\check` before commit
- UI tests for validation severity taxonomy and key behaviors.

Commit message example:
- `feat(vgreport): phase c validation ux and search`

### Phase D — Supporting Features

Scope:
- Placeholder alias support policy and implementation.
- Work queue filters, modifier picker, role labels (as planned).

Gates:
- `\.\check` before commit
- Tests for placeholder alias mapping + queue filter logic.

Commit message example:
- `feat(vgreport): phase d placeholders and workflow helpers`

### Phase E — Export System

Scope:
- Implement exports exactly matching Phase A golden definitions.
- Add Export Center presets.

Gates:
- `\.\check` before commit
- Golden export tests (byte-for-byte expectations for CSV encoding, BOM, CRLF; deterministic column order)

Commit message example:
- `feat(vgreport): phase e export center and kindergarten exports`

### Phase F — QA + Release

Scope:
- Add/finish tests, packaging smoke, and QA checklist docs.

Gates:
- `\.\check`
- All tests green
- Tauri dev smoke E2E passes (see docs/tauri_e2e_testing.md)

Commit message example:
- `test: phase f golden exports and release qa`

---

## ADR TRIGGERS (must enforce)

Before implementing changes in these areas, check if an ADR is required:

- Canonical ID schemes or mapping strategy changes
- Schema changes in `schemas/*.json`
- IPC contract changes in `contracts/*.schema.json`
- Any change that affects export semantics (CSV shape/encoding) beyond what Phase A defined

If ADR is required:
- Create it before implementing the change.
- Link it from index.md (canonical index) under ADRs.

---

## OUTPUT FORMAT (how you report progress)

At the end of each phase (before committing):
- List changed files
- Confirm `\.\check` result
- Confirm tests run and results
- Confirm doc versions/status were updated
- Confirm no PII was introduced

If anything fails:
- Stop and report the failure, the likely cause, and the next fix step.
