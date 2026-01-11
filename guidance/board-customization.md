---
id: doc.guidance.board_customization
type: document
title: Board Customization Guide
version: 0.1.0
status: draft
tags: [guidance, customization, board]
refs:
  - ref.ontario.kindergarten.program.2016
  - ref.ontario.growing.success.2010
updated: 2026-01-11
---

# Board Customization Guide

## Purpose
This guide helps school boards adapt the framework templates to their local context while maintaining compliance with provincial standards.

## What Can Be Customized

### 1. Terminology
Some boards use specific terminology. You may adapt:
- "Kindergarten" vs "FDK" vs "Full-Day Kindergarten"
- "Learning Story" vs "Communication of Learning"
- Board-specific program names

**Do NOT change:**
- Frame names (these are provincially defined)
- Indicator language (tied to curriculum)

### 2. Faith-Based Extensions (Catholic Boards)
Catholic boards may add:
- References to Catholic Graduate Expectations
- Connections to "Fully Alive" curriculum
- Faith-based language in Next Steps

**Example extension:**
```
{child} demonstrates care for others, reflecting our Catholic teaching 
of treating everyone as a child of God.
```

### 3. Length Constraints
Boards may have different character limits in their SIS. Common limits:
- Edsembli: ~2000 characters per section
- PowerSchool: varies by configuration
- Maplewood: varies by configuration

Adjust templates to fit your board's technical constraints.

### 4. Home-School Connections
Some boards emphasize specific home strategies. You may localize:
- References to local community resources
- Culturally-responsive suggestions
- Language support strategies

## What Should NOT Be Customized

1. **Privacy boundaries**: No PII under any circumstances
2. **Strengths-based language**: Required by Growing Success
3. **Frame alignment**: Templates must align to correct frames
4. **Indicator traceability**: Every template must trace to specific indicators

## Customization Process

1. **Fork or branch** the main repository
2. **Document changes** in a local `customizations.md` file
3. **Validate** using the same scripts (`validate.py`, `lint.py`)
4. **Track upstream**: Periodically merge updates from main repo

## Support
For board-specific implementation support, contact your curriculum consultant or SIS administrator.
