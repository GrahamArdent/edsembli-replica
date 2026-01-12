# Sidecar Attempts Log (VGReport)

Last updated: 2026-01-12

Purpose: keep a durable record of sidecar-related debugging attempts so we don’t repeat the same work.

---

## Current Symptom (as of last report)

- In-app debug overlay:
  - `App mounted, initializing sidecar...`
  - `Sidecar mode: bundled exe`
  - `Sidecar initialized.`
  - `Loaded 0 templates.`
- UI shows `Browse Templates (0)`.

## Ground Truth Checks (Important)

- Running the built sidecar exe directly returns templates successfully:
  - Sidecar logs: `Loaded 36 templates from embedded data`
  - JSON-RPC response includes `{"result":{"templates":[...]}}`

This implies:
- Templates exist and the sidecar can serve them.
- The “0 templates” in UI is likely a client parsing/shape mismatch, a different binary being launched, or request/response not reaching the expected code path.

---

## Attempts / Changes (Chronological)

### 1) UI + State Wiring
- **Goal**: Build the app UI and connect it to data.
- **Action**: Implemented sidebar, workspace editor, preview, template browsing UI; wired to store.
- **Result**: UI works; template list depends on sidecar responses.
- **Status**: Completed.

### 2) Sidecar JSON-RPC (stdin/stdout) + Log Streaming
- **Goal**: Spawn Python engine and communicate via JSON-RPC.
- **Action**: Implemented TS client to spawn sidecar, write stdin, parse stdout JSON, stream stderr logs into an in-app debug console.
- **Result**: Sidecar initializes and logs appear.
- **Status**: Completed.

### 3) React “White Screen” + Infinite Loop Fixes
- **Goal**: Stop the UI from crashing/looping.
- **Action**: Fixed missing import; corrected hook usage causing infinite loop.
- **Result**: App renders reliably.
- **Status**: Completed.

### 4) Port 1420 Conflicts (Zombie Processes)
- **Goal**: Make `tauri dev` start reliably.
- **Action**: Used `netstat -ano | findstr :1420` and `taskkill /PID ... /F` repeatedly.
- **Result**: Works when processes are killed.
- **Status**: Ongoing operational issue; not a code fix.

### 5) Sidecar Crash: `logger` undefined
- **Goal**: Stop engine from crashing.
- **Action**: Fixed Python logging initialization.
- **Result**: Sidecar runs.
- **Status**: Completed.

### 6) Tauri Capabilities / Permissions
- **Goal**: Allow spawning sidecar and writing stdin.
- **Action**: Updated Tauri capabilities to allow spawn + stdin writes; temporary permission for python-dev command when needed.
- **Result**: Sidecar can be spawned and written to.
- **Status**: Completed (python-dev permission is optional/temporary).

### 7) Templates Not Loading (0 templates)
- **Goal**: Get templates into UI.
- **Early hypothesis**: sidecar couldn’t find `templates/comment_templates.yaml` due to runtime paths.
- **Actions**:
  - Added detailed debug logging for `sys.frozen` / `sys._MEIPASS` and search paths.
  - Adjusted PyInstaller data bundling (`--add-data`) and spec datas.
  - Found `--windowed/--noconsole` breaks stdin/stdout (stdin becomes `None`), so switched to console bootloader.
- **Result**: File-based template discovery remained brittle.
- **Status**: Superseded by embedded template approach.

### 8) Breakthrough: Embedded Templates (Bypass Filesystem/Bundling)
- **Goal**: Make template loading deterministic in dev and frozen exe.
- **Action**: Created `sidecar/embedded_templates.py` with `EMBEDDED_TEMPLATES` and loaded templates from that list.
- **Result**: Sidecar logs `Loaded 36 templates from embedded data`.
- **Status**: Completed and should be the stable long-term solution unless we intentionally revert.

### 9) StrictMode Double-Init / Log Spam
- **Goal**: Prevent duplicate sidecar init and duplicated log handlers.
- **Action**: Guarded initialization with `useRef`, added unsubscribe cleanup for log subscription.
- **Result**: Reduced duplicate logs/handlers.
- **Status**: Completed.

### 10) “Recommended Mode”: Use Bundled Sidecar Exe by Default
- **Goal**: Make dev and prod behave the same.
- **Action**: In `vgreport/src/services/sidecar.ts`, default spawn uses `Command.sidecar('vgreport-engine')`; python-direct is an opt-in escape hatch via env flag.
- **Result**: App reports `Sidecar mode: bundled exe`.
- **Status**: Completed.

### 11) Fix: stdout JSON shape mismatch (Defensive Parsing)
- **Goal**: Avoid `Loaded 0 templates` when response is not wrapped in `result`.
- **Action**: In `vgreport/src/services/sidecar.ts`, if parsed JSON lacks `result`, resolve the whole object.
- **Expected**: `sidecar.call('list_templates')` returns an object with `templates`.
- **Observed**: User still sees `Loaded 0 templates`.
- **Status**: Implemented; needs verification via overlay response-shape logs.

### 12) Added Instrumentation in App.tsx for Response Shape
- **Goal**: Print the keys + JSON preview of the `list_templates` response.
- **Action**: Added two debug overlay lines:
  - `list_templates response keys: ...`
  - `list_templates response preview: ...`
- **Observed**: User reports “nothing changed” (these lines not visible).
- **Status**: Implemented but not observed; indicates app may be running an older frontend bundle or the new code isn’t being loaded/rebuilt.

---

## Likely Remaining Root Causes (Next Investigation)

1) **Frontend hot reload not applying / running stale build**
   - Evidence: App.tsx debug lines added but not appearing.

2) **Different sidecar binary launched than the one tested manually**
   - Evidence: manual exe returns 36 templates, app still gets 0.

3) **Request/response is not the one we think**
   - Possible: `list_templates` call failing silently, timing out, being caught, or returning a different shape.

---

## Next Data Needed (To avoid guessing)

- Paste the in-app overlay lines *after* `Sidecar initialized.` (should include the new `list_templates response ...` lines).
- Paste any Tauri/DevTools console errors.
- If possible, confirm the running dev server refreshed (hard refresh) or restart `npm run tauri dev` after the code change.

---

## Root Cause Found (2026-01-12)

- Tauri dev was launching an *older* sidecar located at `vgreport/src-tauri/vgreport-engine-x86_64-pc-windows-msvc.exe`.
  - That binary returned `{"templates":[]}` and did not recognize newer methods like `debug_info`.
- The newer sidecar was being rebuilt/copied to `vgreport/src-tauri/binaries/…`, but Tauri was not using that path for dev.

### Fix

- Updated `scripts/build_sidecar.ps1` to copy the built exe to **both**:
  - `vgreport/src-tauri/vgreport-engine-x86_64-pc-windows-msvc.exe`
  - `vgreport/src-tauri/binaries/vgreport-engine-x86_64-pc-windows-msvc.exe`

This ensures dev runs the latest sidecar and stops the “app gets 0 templates while manual run gets 36” mismatch.
