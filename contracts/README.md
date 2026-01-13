---
id: doc.contracts.readme
type: document
title: IPC Contracts
version: 0.1.0
status: draft
tags: [contracts, ipc, vgreport]
refs: []
updated: 2026-01-12
---

# Contracts

This folder contains the JSON Schema contracts for the VGReport UI ↔ Python engine IPC boundary.

## Why

- Prevents drift between the TypeScript UI and the Python sidecar.
- Enables TypeScript type generation for compile-time safety.
- Enables runtime validation (optional) in the sidecar.

## Source of truth

The JSON Schema files in this folder are the source of truth.

Generated TypeScript types live in:
- `vgreport/src/contracts/generated.ts`

## Update workflow

1. Edit schema(s) in `contracts/`.
2. Regenerate TS types:
   - `cd vgreport; npm run contracts:gen`
3. Run validation gate:
   - `python scripts/validate.py`

The validation gate fails if generated types are out of date.
