---
id: doc.security
type: document
title: Security Policy
version: 0.1.0
status: draft
tags: [security, governance]
refs: []
updated: 2026-01-11
---

# Security Policy

This repository contains *design artifacts only* (schemas, templates, documentation) and must not contain student-identifying information.

## Reporting a security issue

If you believe you have found a security issue in this repository (e.g., a workflow secret exposure, unsafe automation, or a process gap that could cause PII leakage):

1. Do not open a public issue with sensitive details.
2. Notify the repository owner/maintainer directly.
3. Include steps to reproduce and the file paths involved.

## Data handling boundary

- Do not add PII or student work samples.
- If accidental PII is found, remove it immediately and rotate any impacted credentials (if applicable).

## Scope

- Code execution is limited to local validation utilities and CI checks.
- This repo is not an operational SIS/reporting system and must not be used to store student data.
