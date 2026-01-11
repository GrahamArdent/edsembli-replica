---
id: entity.tool.edsembli
type: entity
entity_type: tool
title: Edsembli (Student Information System)
version: 0.1.0
status: draft
tags: [sis, edsembli, reporting]
refs:
  - ref.edsembli.documentation
  - ref.edsembli.sparkrock.merger.2026
updated: 2026-01-11
---

# Edsembli (Student Information System)

## Summary

Edsembli is a Student Information System (SIS) used by school boards to manage student information and produce reporting outputs, including Kindergarten Communication of Learning (CoL) narratives.

## Capabilities (relevant to this framework)

- Supports narrative comment entry for the Kindergarten frames
- Supports reusable comment banks (implementation details vary by board)
- Supports distribution of reporting outputs via portals

## Constraints

- Contains sensitive student data in real deployments (outside this repo)
- Export/import capabilities and formats are board-configured and vendor-specific

## Inputs / Outputs (conceptual)

- Inputs: educator observations and evidence (stored privately in SIS)
- Outputs: report narratives aligned to frames and CoL sections

## Related

- `entity.standard.onsis`
- `ref.ontario.growing.success.2010`
