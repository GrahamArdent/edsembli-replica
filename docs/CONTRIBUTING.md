---
id: doc.contributing
type: document
title: Contributing Guide
version: 0.2.0
status: draft
tags: [contributing, governance]
refs: []
updated: 2026-01-11
---

# Contributing Guide

Thank you for helping define the Edsembli Replica Framework.

This guide covers both **content contributions** (docs, templates, taxonomy) and **code contributions** (scripts, CLI, schemas).

## 1. Principles

1.  **Privacy First**: No student data. Ever.
2.  **Canonical vs. Source**:
    - Editing "Truth"? Edit canonical docs in `docs/` (e.g., `docs/framework.md`, `docs/infrastructure.md`) or `schemas/`/`taxonomy/`/`knowledge/`.
    - Adding Research? Add a Markdown or PDF file to `sources/`.
3.  **Traceability**: If you make a claim, link it to a reference ID or a Source file.
4.  **Single Source of Truth**: Edit canonical files in the root; never edit `docs_site/` (auto-generated).

## 2. Setup (First Time)

### 2.1 Clone and Install

```bash
git clone https://github.com/GrahamArdent/edsembli-replica.git
cd edsembli-replica
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # macOS/Linux
pip install -r requirements.lock.txt
```

### 2.2 Activate Pre-commit Hooks (REQUIRED)

```bash
pip install pre-commit
pre-commit install
```

Pre-commit runs on every commit:
- Trailing whitespace cleanup
- YAML validation
- Secrets detection (gitleaks)
- Type checking (pyright)
- Schema validation
- Lint checks
- Coverage checks

### 2.3 Verify Setup

```bash
pytest -v
python scripts/validate.py
python scripts/lint.py
```

All should pass before making changes.

## 3. Content Contributions

### 3.1 Updating the Canonical Index (REQUIRED)
- **When adding any new canonical file**, update `index.md` (root) with a link.
- The root `index.md` is the **single source of truth** for navigating the codebase.
- Group your link under the appropriate section (Taxonomy, Guidance, ADRs, etc.).

### 3.2 Editing the Framework (Narrative)
- Edit `docs/framework.md`.
- Keep it high-level.
- Update `CHANGELOG.md`.

### 3.3 Editing the Specification (Infrastructure)
- Edit `docs/infrastructure.md`.
- If changing an ID scheme or data model, create a new ADR in `decisions/`.

### 3.4 Editing Functional Requirements
- Edit `docs/requirements.md`.
- Use lowercase IDs: `req.category.number` (e.g., `req.privacy.1`).
- Use MUST/SHOULD/MAY language per RFC 2119.

### 3.5 Adding Templates or Evidence Patterns
- Follow the ID naming convention: `type.domain.name`.
- Ensure it uses the correct Frontmatter schema.
- Update `index.md` if adding a new category.

## 4. Code Contributions

### 4.1 Adding Scripts

When adding a new script to `scripts/`:

1. **Add docstring** at the top explaining purpose
2. **Follow existing patterns**: use `WORKSPACE_ROOT = Path(__file__).resolve().parents[1]`
3. **Add to `scripts/README.md`** with description
4. **Write tests** in `tests/` if script has logic beyond file operations
5. **Run validation**:
   ```bash
   ruff check scripts/your_script.py
   ruff format scripts/your_script.py
   pyright scripts/your_script.py
   pytest tests/test_your_script.py
   ```

### 4.2 Extending the CLI (`scripts/edsembli_cli.py`)

When adding a new CLI command:

1. **Add command function** using Typer decorators:
   ```python
   @app.command()
   def your_command(arg: str) -> None:
       """Brief description of what this command does."""
       # implementation
   ```

2. **Update index.md** CLI Tools section with new command
3. **Add example usage** to `scripts/README.md`
4. **Test manually**:
   ```bash
   python scripts/edsembli_cli.py your-command --help
   python scripts/edsembli_cli.py your-command test-arg
   ```

### 4.3 Updating Schemas (`schemas/*.json`)

When modifying JSON Schema files:

1. **Bump schema version** (`$version` field)
2. **Update corresponding ADR** if schema change is significant
3. **Test validation**:
   ```bash
   python scripts/validate.py
   ```
4. **Document breaking changes** in `CHANGELOG.md`

### 4.4 Modifying Validation/Lint Scripts

When changing `scripts/validate.py` or `scripts/lint.py`:

1. **Add new checks incrementally** - don't break existing validation
2. **Make warnings non-blocking** unless critical (e.g., readability checks)
3. **Update test fixtures** if changing validation rules
4. **Run full test suite**:
   ```bash
   pytest -v
   python scripts/validate.py
   python scripts/lint.py
   ```

### 4.5 Python Code Standards

All Python code must follow:

- **Formatting**: `ruff format .` (auto-formats)
- **Linting**: `ruff check .` (must pass)
- **Type hints**: Add type hints for function signatures
- **Type checking**: `pyright` must pass (or use `# type: ignore` with justification)
- **Imports**: Use `from __future__ import annotations` at top of file
- **Docstrings**: Add module-level docstring explaining purpose

### 4.6 Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: ...` for new features (scripts, templates)
- `fix: ...` for bug fixes
- `docs: ...` for documentation only
- `style: ...` for formatting, missing semi-colons, etc.
- `refactor: ...` for code restructuring without API changes
- `test: ...` for adding missing tests
- `chore: ...` for maintenance tasks

## 5. Build and Test Workflow

### 5.1 Before Committing

Run the full validation pipeline:

```bash
# Format and lint
ruff format .
ruff check .

# Validate content
python scripts/validate.py
python scripts/lint.py
python scripts/coverage.py

# Run tests
pytest -v

# Type check
pyright

# Build docs (if changed)
python scripts/sync_docs.py
mkdocs build
```

### 5.2 Documentation Changes

If you edited canonical files that appear in MkDocs:

1. **Sync to docs_site**: `python scripts/sync_docs.py`
2. **Test build**: `mkdocs build --strict`
3. **Preview locally**: `mkdocs serve` (opens http://localhost:8000)
4. **Never edit `docs_site/` directly** - it's auto-generated and git-ignored

### 5.3 Testing Requirements

- **All new scripts** should have basic tests in `tests/`
- **Validation changes** require golden output tests
- **Schema changes** require test fixtures
- Test coverage target: 80% (check with `pytest --cov`)

Run tests for a specific file:
```bash
pytest tests/test_specific.py -v
```

## 6. Version Policy

All canonical files include a `version` field. When editing:

| Change Type | Version Bump | Example |
|-------------|--------------|--------|
| Typo/minor wording | Patch | `0.1.0` → `0.1.1` |
| New template/indicator | Minor | `0.1.0` → `0.2.0` |
| Breaking schema change | Major | `0.1.0` → `1.0.0` |

**Always update the `updated` date in front matter when making changes.**

For code (scripts, tests):
- Version bumps tracked in `CHANGELOG.md`, not in individual scripts
- Breaking CLI changes require CHANGELOG entry

## 7. Decision Process (ADRs)

For significant architectural decisions (e.g., "We will switch from YAML to TOML"), please create an Architecture Decision Record in `decisions/` or `docs/adr/`.

**Use `decisions/` for:**
- Content structure decisions
- ID naming conventions
- Template formats

**Use `docs/adr/` for:**
- Technical/tooling decisions
- Algorithm choices
- Integration patterns

Process:
1. Copy `decisions/0000-adr-template.md`
2. Number it sequentially (or use descriptive name in `docs/adr/`)
3. Update `index.md` ADR section

Key decisions already documented:
- ADR 0001: Canonical vs sources distinction
- ADR 0002: Framework vs infrastructure split
- ADR 0003: Template library format (single YAML)
- ADR 0004: Curly-brace placeholder convention
- ADR 0005: ID naming convention (type.domain.name)
- ADR-001: Evidence-template linking (heuristic matching)
- ADR-002: Template deprecation workflow

## 8. Pre-commit Failures

If pre-commit blocks your commit:

1. **Trailing whitespace / formatting**: Auto-fixed, just re-add files and commit
2. **Type errors (pyright)**:
   - If false positive (imports not resolved), use `--no-verify` as last resort
   - Prefer fixing by adding `# type: ignore[import]` with comment
3. **Validation errors**: Fix the content issue before committing
4. **Lint errors**: Check `python scripts/lint.py` output and fix

## 9. Contribution Checklist

Before submitting changes:

- [ ] Pre-commit hooks installed and passing
- [ ] `pytest` passes
- [ ] `scripts/validate.py` passes
- [ ] `scripts/lint.py` passes
- [ ] `scripts/check_index.py` passes (verifies index links)
- [ ] If docs changed: `mkdocs build` succeeds
- [ ] If new file added: `index.md` updated
- [ ] If schema changed: version bumped
- [ ] `CHANGELOG.md` updated (for user-facing changes)
- [ ] `docs/discussion.md` updated (for design decisions)

## 10. Development Tips

- **VS Code**: We recommend the "Python", "YAML", and "Markdown All in One" extensions.
- **Fast Testing**: Use `pytest -k "keyword"` to run specific tests instead of the full suite.
- **Docs Preview**: Run `mkdocs serve` to see changes live at `http://localhost:8000`.
- **Linter Output**: If `lint.py` is noisy, check `scripts/lint.py` configuration to adjust thresholds.

## 11. Getting Help

- **Questions about structure**: See `docs/infrastructure.md`
- **Questions about tooling**: See `README.md` or `scripts/README.md`
- **Questions about content**: See `docs/framework.md`
- **Questions about style**: See `guidance/comment-style.md`
