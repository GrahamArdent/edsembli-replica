---
id: doc.privacy
type: document
title: Privacy & No-PII Checklist
version: 0.1.0
status: draft
tags: [privacy, governance, safety]
refs: []
updated: 2026-01-11
---

# Privacy & No-PII Checklist

This repository is designed to remain safe to share. It must not contain PII or student-identifying information.

## What must never be committed

- Student names, initials, student numbers, birthdates, addresses, photos, videos, audio
- Teacher/staff names if they could identify a specific classroom/student context
- Parent/guardian information of any kind
- Screenshots or exports from Edsembli (or any SIS) that contain real data
- Unique incident narratives that could re-identify a student when combined with time/place/context

## Allowed content (safe patterns)

- Structural templates with slot placeholders (example: `{child}`, `{evidence}`)
- Aggregated, non-identifying examples that cannot be linked to a real child
- Controlled vocabularies (frames, indicators, tags) and citations
- General workflow guidance that describes how to do work without embedding real artifacts

## Safe example rules

When writing example text:
- Use slot placeholders instead of names: `{child}`, `{pronoun_subject}`, `{pronoun_possessive}`
- Avoid dates tied to real events (use `YYYY-MM-DD` or clearly fictional dates)
- Avoid naming schools, classrooms, neighbourhoods, or specific staff
- Prefer describing categories over specifics (e.g., “during block play” rather than “during the January 12 STEM fair”)

## Review checklist (pre-merge)

- Search for common PII markers:
  - Names, initials, student numbers, phone numbers, addresses
  - Realistic email formats (`@`), postal codes, birthdays
  - Board-specific portal URLs that embed identifiers
- Confirm all examples use `{slot}` placeholders
- Confirm new references are links/metadata only (no copyrighted full-text dumps)
- Confirm files under `sources/` remain reference-only and do not become “truth” without extraction

## If you accidentally committed PII

1. Stop sharing the repository immediately.
2. Remove the content and rotate any exposed credentials.
3. Rewrite history if necessary (git filter-repo / BFG) and notify collaborators.
4. Document the incident and prevention step(s) in an ADR or the changelog.

## Related

- See discussion notes in `discussion.md` for the design rationale.
