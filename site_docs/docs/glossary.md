---
id: doc.taxonomy.glossary
type: document
title: Glossary & Controlled Vocabulary
version: 0.1.0
status: draft
tags: [glossary, taxonomy]
refs: []
updated: 2026-01-11
---

# Glossary & Controlled Vocabulary

> Canonical definitions for the domains and entities in this framework.
> Stable ID: `doc.taxonomy.glossary`

## Core Concepts

### Frame
One of the four developmental areas in the Ontario Kindergarten Program:

| Frame | Canonical ID |
|-------|-------------|
| Belonging & Contributing | `frame.belonging` |
| Self-Regulation & Well-Being | `frame.self_regulation` |
| Demonstrating Literacy & Mathematics Behaviours | `frame.literacy_math` |
| Problem Solving & Innovating | `frame.problem_solving` |

### Indicator / Expectation
A specific observable learning outcome or behaviour described within a Frame. (Note: "Expectation" is the formal Ministry term; "Indicator" often refers to the specific observable signal).

### Evidence Pattern
A reusable, non-PII description of a learning scenario (archetype). It bridges the gap between abstract curriculum expectations and concrete student moments without recording actual student data.

### Comment Template
A structured text pattern used to generate the "Communication of Learning" report card comments (Key Learning, Growth, Next Steps). It typically contains "Slots".

### Slot
A placeholder in a template (e.g., `{strength}`, `{next_step}`, `{learning_context}`) meant to be filled by the educator in a private system.

### Traceability Matrix
The dataset that links a **Frame** → **Indicator** → **Evidence Pattern** → **Comment Template** → **Reference**.

## System Entities

### Entity
Any discrete "thing" the framework needs to know about: a School Board, a Tool (Edsembli), a Policy Document, or a Workflow.

### Canonical
The authoritative version of a document or dataset in this repository. If it contradicts a "Source", the Canonical file wins.

### Source
Raw research, background material, or reference documents kept in `sources/`. Not authoritative.
