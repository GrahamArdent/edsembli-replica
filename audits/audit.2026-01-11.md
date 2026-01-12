---
id: doc.audit.2026_01_11
type: document
title: Repository Audit (2026-01-11)
version: 0.1.0
status: draft
tags: [audit, governance, traceability]
refs: []
updated: 2026-01-11
---

# Repository Audit (2026-01-11)

## Snapshot

- Date: 2026-01-11
- Repo revision: ba754ceb7f1370c8835259323eeef0e7f98373d
- Scope: design-first framework for Ontario Kindergarten CoL narrative comments (no implementation, no student data)

## Canonical entry points

- Canonical Index: [index.md](../index.md)
- Canonical docs: [docs/framework.md](../docs/framework.md)

## Structure audit

**Separation of concerns looks healthy**:

- Canonical narrative/spec: [index.md](../index.md)
- Schemas + tooling: [schemas/README.md](../schemas/README.md), [scripts/README.md](../scripts/README.md)
- Controlled vocabularies: [taxonomy/README.md](../taxonomy/README.md)
- Reusable libraries: [templates/library.md](../templates/library.md), [evidence/README.md](../evidence/README.md)
- References: [references/links.md](../references/links.md)
- Process knowledge: [knowledge/processes/index.md](../knowledge/processes/index.md)
- Derived datasets (no PII): [datasets/traceability/README.md](../datasets/traceability/README.md)
- Research inputs (non-canonical): [sources/Finding Assembly Report Card Software Information.md](../sources/Finding%20Assembly%20Report%20Card%20Software%20Information.md)

## Content inventory (high level)

- Frames: 4
- Indicators: 13
- Comment templates: 36
- Evidence patterns: 15
- JSON Schemas: 10
- Process SOPs: 3

## Automation and drift prevention

- Pre-commit: installed and running (hooks include formatting fixers + canonical validation/lint/coverage)
- CI: GitHub Actions workflow present in `.github/workflows/ci.yml`

Additional hardening added:

- Secrets scanning: `detect-secrets` (pre-commit baseline) and `gitleaks` (CI)
- Dependency locking: `requirements.in` + `requirements.lock.txt` verified in CI
- Derived dataset contract: `datasets/traceability/matrix.schema.json` validated by `scripts/validate_datasets.py`
- Type checking: `pyright` in CI and pre-commit
- Query ergonomics: `scripts/edsembli_cli.py` (DuckDB + template search)

## Validation results (latest run)

- `python scripts/validate.py`: PASS
- `python scripts/lint.py`: PASS
- `python scripts/coverage.py`: PASS (13/13 indicators covered)
- `python scripts/generate_matrix.py`: PASS (generates `datasets/traceability/matrix.csv` and `matrix.parquet`)
- `python scripts/validate_datasets.py`: PASS (traceability dataset contract)
- `pyright`: PASS
- `detect-secrets`: baseline present (`.secrets.baseline`)

## Traceability matrix audit

- Contract/spec: [datasets/traceability/README.md](../datasets/traceability/README.md)
- Generator: [scripts/generate_matrix.py](../scripts/generate_matrix.py)
- Outputs:
  - [datasets/traceability/matrix.csv](../datasets/traceability/matrix.csv)
  - matrix.parquet (optional local artifact; not checked in)

Notes:
- Rows represent template→indicator trace links, optionally joined to an evidence pattern and refs.
- Evidence pattern linkage is heuristic (best-effort match by frame+indicator).

## Governance / safety audit

- No-PII boundary documented: [docs/PRIVACY.md](../docs/PRIVACY.md)
- Security reporting guidance: [docs/SECURITY.md](../docs/SECURITY.md)
- Release/version policy: [docs/RELEASE.md](../docs/RELEASE.md)
- Validation/testing stance: [docs/TESTING.md](../docs/TESTING.md)
- Override boundary defined: [guidance/override-policy.md](../guidance/override-policy.md)

## Risks and watch-outs

- Generated files risk: ensure `references/links.md` and `datasets/traceability/matrix.*` are treated as derived artifacts and regenerated rather than edited.
- Matrix evidence linkage: heuristic matching may pick a non-ideal evidence pattern when multiple patterns cover the same indicator. If this becomes sensitive, add explicit template→evidence references.

## Remaining gaps (as of this audit)

None blocking for the current design scope.

Optional future enhancements:
- Extend dataset contract checks to validate *semantic* constraints (e.g., ID regex patterns, allowed ref namespaces).
- Extend linting to validate internal Markdown links (path existence) if link drift becomes an issue.

## How to reproduce this audit

```bash
python scripts/validate.py
python scripts/lint.py
python scripts/coverage.py
python scripts/generate_links.py
python scripts/generate_matrix.py
```
