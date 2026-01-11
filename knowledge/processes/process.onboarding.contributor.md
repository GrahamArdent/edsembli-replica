---
id: process.onboarding.contributor
type: process
title: Contributor Onboarding
version: 0.1.0
status: draft
tags: [workflow, onboarding, contributor]
refs: []
updated: 2026-01-11
---

# SOP: Contributor Onboarding

## 1. Objective
To onboard new contributors so they can effectively add content to the framework.

## 2. Prerequisites
- Git installed locally
- Python 3.12+ installed
- VS Code or similar editor
- GitHub account with repo access

## 3. Setup Steps

### 3.1 Clone Repository
```bash
git clone https://github.com/GrahamArdent/edsembli-replica.git
cd edsembli-replica
```

### 3.2 Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # macOS/Linux
```

### 3.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.4 Install Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### 3.5 Verify Setup
```bash
python scripts/validate.py
python scripts/lint.py
python scripts/coverage.py
```

All three should pass with "OK" status.

## 4. Required Reading

Before contributing, review these documents in order:

1. [README.md](../../README.md) - Project overview
2. [framework.md](../../framework.md) - Conceptual foundation
3. [infrastructure.md](../../infrastructure.md) - Technical specification
4. [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines
5. [PRIVACY.md](../../PRIVACY.md) - No-PII rules
6. [guidance/comment-style.md](../../guidance/comment-style.md) - Style guide

## 5. First Contribution

Recommended first task: Add a new evidence pattern.

1. Copy an existing pattern from `evidence/`
2. Modify for a new classroom scenario
3. Run validation scripts
4. Submit PR with descriptive title

## 6. Getting Help

- Check `discussion.md` for design decisions
- Review `decisions/` folder for ADRs
- Ask in team channel for clarification
