---
id: doc.readme
type: document
title: Edsembli Replica (Design Framework)
version: 0.1.0
status: draft
tags: [readme, overview]
refs: []
updated: 2026-01-11
---

# Edsembli Replica (Design Framework)

This repository is a design-first framework for Ontario Kindergarten Communication of Learning (CoL) narrative comments (no implementation, no student data).

## Start here

- Canonical index: [index.md](index.md)
- Framework narrative: [docs/framework.md](docs/framework.md)
- Infrastructure/spec: [docs/infrastructure.md](docs/infrastructure.md)
- Preserved research inputs: [sources/](sources/)

## Governance (quick links)

- Security policy: [docs/SECURITY.md](docs/SECURITY.md)
- Release and versioning: [docs/RELEASE.md](docs/RELEASE.md)
- Testing and validation: [docs/TESTING.md](docs/TESTING.md)

## Safety

- No PII/student-identifying information belongs in this repo.

## Status

- Design only. Implementation work (if any) should follow the conventions in [docs/infrastructure.md](docs/infrastructure.md).

## Tooling quickstart

- Locked installs (recommended): `pip install -r requirements.lock.txt`
- Update the lockfile: `pip-compile --no-header requirements.in --output-file requirements.lock.txt`
- Build documentation site: `python scripts/sync_docs.py && mkdocs build`
- Serve docs locally: `mkdocs serve`
- Run the full local pipeline:
	- `ruff check .`
	- `ruff format --check .`
	- `pytest -v`
	- `python scripts/validate.py`
	- `python scripts/lint.py`
	- `python scripts/coverage.py`
	- `python scripts/generate_matrix.py`
	- `python scripts/validate_datasets.py`
	- `pyright`
	- `python scripts/stage_docs.py`
	- `mkdocs build --strict`
