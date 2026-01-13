---
id: doc.vgreport.tauri_e2e_testing
type: document
title: VGReport – Tauri-Oriented E2E Testing
version: 0.1.0
status: draft
tags: [technical, testing]
refs: []
updated: 2026-01-12
---

# VGReport – Tauri-Oriented E2E Testing

## Why this exists

Browser-only E2E tests are useful, but they don’t catch Tauri-specific integration failures (Rust build/runtime issues, plugin permissions, sidecar spawning, packaging differences, WebView quirks).

So we keep a layered strategy:

- Fast UI tests (Vitest + jsdom) for most behaviors.
- Sidecar smoke (`health`, `list_templates`) to validate the shipped engine protocol.
- Rust tests (`cargo test`) for SQLite/command logic.
- A **Tauri-oriented smoke E2E** to verify the desktop app can actually boot in a real Tauri runtime.

## Current E2E approach (minimal + reliable)

The first E2E layer is intentionally a **smoke test**:

- launches `tauri dev`
- waits until the configured dev server URL is reachable (`http://localhost:1420`)
- fails if `tauri dev` exits early
- then terminates the process tree (so the test finishes)

This is implemented by:
- [vgreport/scripts/e2e_tauri_smoke.mjs](vgreport/scripts/e2e_tauri_smoke.mjs)

## Run it

From the [vgreport/](vgreport/) folder:

- `npm run e2e:tauri`

Optional env vars:

- `VGREPORT_E2E_TIMEOUT_MS=60000` (default 60s)
- `VGREPORT_DEV_URL=http://localhost:1420`

## What’s next (if we want true UI automation)

If we later need “click buttons in the real desktop window” automation, we’ll likely add a separate harness using OS-level automation (Windows UI Automation / Appium / WinAppDriver-style tooling) or a WebDriver-like bridge for the WebView.

That layer is heavier and more brittle, so it should be reserved for a few critical journeys (launch → add student → edit section → preview updates → export).
