---
id: doc.infrastructure
type: document
title: Infrastructure Design for the Framework
version: 0.1.0
status: draft
tags: [infrastructure, spec, schemas, governance]
refs:
  - ref.ontario.kindergarten.program.2016
  - ref.ontario.growing.success.2010
updated: 2026-01-11
---

# Infrastructure Design for the Framework (Canonical Index, Schemas, and Tooling)

> Scope: design only. No implementation.

## 0) Objectives / Non-Objectives

### Objectives
- Provide a **canonical file index** and conventions so the framework is maintainable and queryable.
- Define **machine-readable schemas** to support search, traceability, and structured generation (report comments, evidence summaries, etc.).
- Recommend a **toolchain** (Python + optional Next.js UI + agent workflow tools like LangGraph) to operationalize the framework.
- Decide where a **matrix/traceability** model is used and how it is stored.

### Non-objectives
- Building pipelines, apps, agents, or integrations (Edsembli/board systems) now.
- Storing any PII/student data in this repo.

---

## 1) Canonical File Index (Repository Layout)

**Canonical principle:** each concept has one authoritative (“canonical”) file; derived views are generated elsewhere.

Proposed layout (paths are conceptual; keep inside your repo):

- `docs/framework.md`
  - Narrative reference (what the framework *is*, key concepts, constraints, citations).
- `docs/infrastructure.md` *(this file)*
  - How the framework is made functional (schemas, tooling, workflows, governance).
- `index.md` *(recommended canonical index landing page)*
  - Human-friendly directory of all canonical artifacts and their purpose.
- `docs/discussion.md`
  - Captures review findings, decisions, and rationale for future refactors.
- `docs/ROADMAP.md`
  - Phased plan for moving from design artifacts to validation tooling.
- `README.md`, `docs/CHANGELOG.md`, `docs/CONTRIBUTING.md`
  - Project overview, versioned changes, and contribution process.
- `docs/requirements.md`
  - Functional requirements for tooling/workflow (distinct from `requirements.txt`).
- `docs/PRIVACY.md`
  - Operational checklist to enforce the no-PII boundary.
- `guidance/`
  - `guidance/comment-style.md` (comment tone/structure guidance)
- `sources/` *(reference inputs; not canonical)*
  - Saved background research and other inputs used to inform canonical decisions.
- `examples/` *(illustrative; non-PII)*
  - Sample evidence patterns and comment templates (structure-focused, not a complete library).
- `schemas/`
  - `schemas/README.md` (how to use/validate schemas)
  - `schemas/document.frontmatter.schema.json`
  - `schemas/entity.frontmatter.schema.json`
  - `schemas/bibliography.schema.json`
  - `schemas/frames.schema.json`
  - `schemas/indicators.schema.json`
  - `schemas/col_sections.schema.json`
  - `schemas/comment_templates.schema.json`
- `contracts/`
  - JSON Schema contracts for the VGReport UI ↔ Python sidecar IPC boundary.
  - Types are generated into `vgreport/src/contracts/generated.ts` and drift-gated by `scripts/validate.py`.
- `scripts/`
  - `scripts/README.md` (how to run local checks)
  - `scripts/validate.py` (schema + front matter validation)
  - `scripts/lint.py` (reference and placeholder linting)
  - `scripts/generate_matrix.py` (traceability matrix generator)
- `taxonomy/`
  - `taxonomy/frames.yaml` (Ontario K four frames)
  - `taxonomy/indicators.yaml` (expanded indicator taxonomy)
  - `taxonomy/col-sections.yaml` (Key Learning / Growth / Next Steps)
  - `taxonomy/tags.yaml` (controlled vocabulary)
  - `taxonomy/roles.yaml` (teacher, ECE, admin, parent, etc.)
- `references/`
  - `references/bibliography.yaml` (canonical citation records; stable IDs)
  - `references/links.md` (human-readable link list; derived from YAML)
- `knowledge/`
  - `knowledge/entities/` (one file per entity: tool/policy/board/process/etc.)
  - `knowledge/processes/` (workflows, SOPs, report-writing patterns)
  - `knowledge/templates/` (comment patterns, CoL structure scaffolds)
- `templates/`
  - `templates/README.md` (template library overview)
  - `templates/comment_templates.yaml` (canonical comment templates)
- `datasets/` *(optional; no PII)*
  - `datasets/traceability/` (matrix exports, test fixtures, toy data)
- `notes/` *(optional)*
  - Scratchpads; not canonical.
- `app/` *(optional Next.js UI)*
  - Read-only browsing + structured editing; pulls from canonical files.

> If you want “canonical files for reference” beyond `framework.md`, the canonical set is: **index.md**, **references/bibliography.yaml**, **taxonomy/**, and **knowledge/entities/**.

---

## 2) Content Conventions (Make Markdown Queryable)

### 2.1 Front matter everywhere canonical
Use YAML front matter at the top of canonical markdown and entity files.

Non-canonical notes and `sources/` material do not need front matter (and often should not be treated as authoritative).

Minimal fields:
- `id`: stable, slug-like (e.g., `doc.framework`, `entity.edsembli.sis`)
- `type`: `document | entity | process | template | reference-set`
- `title`
- `version`
- `status`: `draft | stable | deprecated`
- `tags`: controlled vocabulary
- `refs`: list of citation IDs (`ref.*`) that support this file

### 2.2 Stable IDs and cross-links
- Prefer linking by IDs (`ref.ontario.kindergarten.program.2016`) rather than raw URLs.
- Raw URLs live in `references/bibliography.yaml`.

### 2.3 ID Naming Convention

All canonical artifacts use a **`type.domain.name`** pattern for IDs.

| Type Prefix | Used For | Example |
|---|---|---|
| `doc.*` | Canonical documents | `doc.framework`, `doc.infrastructure` |
| `ref.*` | Bibliography/citation entries | `ref.ontario.kindergarten.program.2016` |
| `entity.*` | Tools, Boards, Policies | `entity.tool.edsembli`, `entity.board.ncdsb` |
| `frame.*` | The four Kindergarten Frames | `frame.belonging`, `frame.self_regulation` |
| `indicator.*` | Specific expectations/indicators | `indicator.belonging.relationships` |
| `evidence.*` | Evidence patterns (archetypes) | `evidence.pattern.block_play` |
| `template.*` | Comment bank templates | `template.comment.keyl_belonging` |
| `req.*` | Functional requirements | `req.privacy.1` |


**Rules:**
1.  IDs are lowercase, using underscores for multi-word names (`key_learning`, not `keyLearning`).
2.  IDs should be stable; changing an ID is a breaking change requiring an ADR.
3.  When referencing, always use the full ID (e.g., `ref.ontario.kindergarten.program.2016`).

### 2.4 "No PII" boundary
- Repository must remain safe to share; keep student/teacher names and identifiers out.
- If later needed, store sensitive artifacts in a separate private system with access controls.

---

## 3) Data Model / Schemas (Multiple, Purpose-Specific)

You will likely want **multiple schemas** because you have multiple use-cases:
- human reading (Markdown)
- validation (JSON Schema / Pydantic)
- retrieval (vector + metadata)
- traceability (matrix)
- structured generation (templates + slots)

Below are proposed schemas at a design level.

---

### 3.1 Schema A — Document Front Matter (YAML in Markdown)

**Intent:** make Markdown documents indexable/validatable.

Example (conceptual):
```yaml
id: doc.infrastructure
type: document
title: Infrastructure Design for the Framework
version: 0.1.0
status: draft
tags: [infrastructure, schemas, tooling]
refs: [ref.ontario.kindergarten.program.2016, ref.edsembli.manual.sis]
updated: 2026-01-11
```

Validation options:
- **JSON Schema** (good for CI validation)
- **Pydantic models** (good inside Python tooling)

---

### 3.2 Schema B — Reference / Citation Record (YAML)

**Intent:** canonical citations, durable IDs, de-duped links.

Fields:
- `id` (e.g., `ref.ontario.kindergarten.program.2016`)
- `title`
- `publisher`
- `url`
- `accessed`
- `notes`
- `license` / `rights` (important for downstream use)

Why: enables consistent citation in generated outputs and prevents link rot chaos.

---

### 3.3 Schema C — Entity (Tool/Policy/Board/Concept)

**Intent:** one structured record per “thing” so agents/UI can reason consistently.

Fields:
- `id`: `entity.*`
- `entity_type`: `tool | policy | org | curriculum | workflow | dataset`
- `name`
- `summary`
- `capabilities`: list
- `constraints`: list (privacy, platform, licensing)
- `inputs` / `outputs` (high-level)
- `refs`: citation IDs
- `related`: list of other entity IDs

---

### 3.4 Schema D — Evidence / Observation (Non-PII, Pattern-Level)

**Intent:** represent pedagogical documentation *as a structure*, not actual student data.

Fields:
- `id`: `evidence.pattern.*`
- `frame`: one of the 4 frames
- `context`: classroom situation archetype
- `observable_indicators`: bullet list
- `teacher_moves`: bullet list
- `elicitation_prompts`: bullet list
- `assessment_notes_template`: text with slots (no names)
- `refs`

This lets you build reusable “evidence patterns” without storing real observations.

---

### 3.5 Schema E — Comment Bank Template (Structured Generation)

**Intent:** structured snippets aligned to “Key Learning / Growth / Next Steps”.

Fields:
- `id`: `template.comment.*`
- `frame`
- `section`: `key_learning | growth | next_steps`
- `tone`: `parent_friendly | formal | concise`
- `reading_level` (optional)
- `slots`: e.g., `{strength}`, `{evidence}`, `{next_step}`
- `constraints`: max length, banned phrases
- `examples` (synthetic, non-PII)

This supports safe templating and consistent style.

---

### 3.6 Schema F — Traceability Matrix (Yes, Use a Matrix)

**Recommendation:** use a **traceability matrix** to connect:
- Frame → (Expectation/Indicator) → Evidence Pattern → Comment Template → References

Why a matrix:
- It’s the simplest artifact for audits and coverage analysis (“do we have evidence patterns for every frame indicator?”).
- It supports both humans (table view) and machines (joinable dataset).

Storage options:
- Canonical: `datasets/traceability/matrix.parquet` or `matrix.csv`
- Human view: derived `datasets/traceability/matrix.md`

Matrix columns (conceptual):
- `frame_id`
- `indicator_id` (from `taxonomy/frames.yaml` or a dedicated indicators file)
- `evidence_pattern_id`
- `comment_template_id`
- `ref_ids` (array)
- `notes`

Schema should allow arrays and versioning.

---

## 4) Storage / Indexing Architecture (No Implementation, Design Only)

You’ll likely want **three complementary representations**:

1) **File system (Git) as source of truth**
   - Markdown + YAML = canonical, reviewable, versioned.

2) **Vector index for semantic retrieval**
   - Chunk markdown sections + embed + store metadata (ids/tags/refs).
   - Used for “find relevant sections/templates” queries.

3) **Graph or relational layer for explicit links**
   - Graph: entity relationships, citations, traceability edges.
   - Relational: matrices, coverage queries, reports.

### Suggested minimal architecture
- Canonical content in Git
- Build step (offline) creates:
  - `sqlite/duckdb` db for structured tables (references, matrix)
  - vector store for embeddings
  - (optional) graph export (GraphML/Neo4j CSV)

---

## 5) Tooling Research (What to Use)

### 5.1 Python core (recommended)
- **pydantic**: schema validation + typed models for front matter/entities
- **ruamel.yaml**: safe round-trip YAML editing (preserves formatting)
- **markdown-it-py** or **mistune**: parse Markdown into AST for chunking
- **pandas**: matrix operations, coverage analysis
- **pyarrow + parquet**: efficient dataset storage for matrix/exports
- **duckdb**: lightweight analytics over parquet/csv without heavy infra
- **sqlite + sqlalchemy**: if you prefer a simple relational store
- **networkx**: optional graph construction/analysis (coverage, centrality)
- **pytest**: regression tests for schemas and “golden” outputs
- **pre-commit**: enforce formatting + schema checks locally
- **jsonschema**: validate JSON Schema in CI if you go that route

### 5.2 Vector stores (pick one based on ops constraints)
- **Chroma**: simplest local dev, good DX
- **FAISS**: fast local vector search, minimal dependencies
- **pgvector (Postgres)**: best if you already run Postgres; good durability
- **Azure AI Search**: if you’re already on Azure and want managed search

Selection heuristic:
- Prototype: Chroma/FAISS
- Production + multi-user: pgvector or managed search

### 5.3 UI / “Next” (Next.js) options
If you want a usable interface (browse + edit + search):
- **Next.js (App Router)** + **MDX** for rendering canonical docs
- **contentlayer** or **next-mdx-remote** for ingesting Markdown with front matter
- **zod** for runtime validation in the UI layer
- Editor: **TipTap** or **Monaco** (if you want “structured Markdown editing”)
- Auth (if needed): **NextAuth** / Azure AD (Entra ID)
- Search UI: calls your Python service or a search backend

A common split:
- Next.js = presentation + lightweight APIs
- Python = indexing/validation/build pipeline

### 5.4 Agent/workflow orchestration (LangGraph vs alternatives)

**LangGraph (recommended if you want controllable agent workflows)**
- Strengths: explicit state machine, predictable loops, tool routing, good for “ingest → validate → classify → link → summarize”.
- Best for: multi-step pipelines where you need determinism and auditability.

**LlamaIndex**
- Strengths: retrieval pipelines, document loaders, indexing patterns.
- Best for: quick RAG setups, citations, metadata filters.

**LangChain**
- Strengths: broad ecosystem, many integrations.
- Tradeoff: can get complex/implicit; LangGraph helps impose structure.

**Recommendation:**
- Use **LangGraph** to define workflows (state + tools).
- Use **LlamaIndex** (optional) for indexing/retrieval primitives if it speeds you up.
- Keep business logic in plain Python modules so you can swap frameworks.

### 5.5 “Matrix tooling”
- Use **pandas + duckdb** for coverage queries and generating derived views.
- Store canonical matrix in **parquet** (preferred) or **CSV** (simpler).
- Generate Markdown table views for humans.

---

## 6) Workflows (Designed, Not Built)

### 6.1 Ingest / Normalize (documents → canonical)
- Inputs: markdown docs, PDFs (links only), notes.
- Steps (conceptual):
  1. Extract text sections (no copyrighted full-text ingestion unless permitted).
  2. Add/validate front matter.
  3. Deduplicate references into `references/bibliography.yaml`.
  4. Split into entities/processes/templates where appropriate.

### 6.2 Index build (canonical → searchable)
- Chunk Markdown by headings
- Attach metadata: `doc_id`, `section_path`, `tags`, `refs`
- Embed chunks
- Write to vector store + structured DB tables

### 6.3 Retrieval + Generation (query → grounded output)
- Retrieve:
  - semantic chunks (vector)
  - explicit links (matrix + graph)
- Generate:
  - structured outputs (comment templates, summaries) with citation IDs
- Validate:
  - schema checks (Pydantic/JSON Schema)
  - style constraints (length, banned terms)

### 6.4 Evaluation / Regression
- Maintain a small set of test queries + expected citations/sections.
- Run in CI to detect “framework drift”.

---

## 7) Governance, Safety, and Compliance

- **Privacy:** no student-level data in this repo; design patterns only.
- **Citations:** always retain `ref_ids` for generated artifacts.
- **Licensing:** store only what you have rights to store; prefer links + summaries.
- **Auditability:** matrix + schemas provide explainability for why a template exists and what supports it.
- **Change control:** version schemas; breaking changes require migration notes.

### 7.1 Practical governance rules (lightweight)

- **Canonical vs source:** the only “truth” is what is stated in canonical docs/datasets; `sources/` is reference input.
- **Single source of truth:** for any concept (frame definition, indicator, template), decide the one canonical file that owns it.
- **Deprecation:** keep deprecated artifacts, mark them `status: deprecated`, and point to the replacement.
- **Versioning:** increment `version` when meaning changes; update `updated` date on canonical docs.
- **Traceability discipline:** if something matters (policy claim, requirement), link it to a `ref.*` ID and (later) to a matrix row.
- **No PII boundary:** do not store real observations, names, IDs, or student-level media here.

---

## 8) Suggested Next Canonical Additions (Design Notes)

If/when you expand canonical files, prioritize:
- `index.md` (human entry point)
- `references/bibliography.yaml` (citation authority)
- `taxonomy/frames.yaml` (controlled vocabulary)
- `schemas/*.schema.json` (validation contract)
- `datasets/traceability/matrix.parquet` (coverage backbone)

> No code or new files are created here beyond this design document unless requested.

---

## Appendix A) Glossary

> The detailed glossary is now maintained in a dedicated file: `glossary.md`.
> The following is a quick reference only. For full definitions, see [glossary.md](glossary.md).

- **Canonical**: authoritative, maintained artifact.
- **Source**: raw material in `sources/`, not authoritative.
- **Frame**: one of the four Ontario K frames.
- **Indicator**: a specific expectation within a Frame.
- **Evidence pattern**: a reusable, non-PII learning scenario archetype.
- **Comment template**: a structured snippet with slots.
- **Traceability matrix**: a table linking Frames → Indicators → Evidence → Templates → References.

---
