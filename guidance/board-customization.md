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

See also: [Override and Customization Policy](override-policy.md)

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

---

## Board Configuration Presets

### Overview

The framework provides a **board configuration system** that allows you to define board-specific settings in a structured YAML file. This ensures consistency across exports and validates against your SIS constraints.

### Available Presets

The repository includes example presets in `config/boards/`:

1. **NCDSB** (`config/boards/ncdsb.yaml`)
   - Northeast Catholic District School Board
   - Bilingual (English/French)
   - Edsembli SIS
   - Character limits: 400-1500 total, 100-600 per section
   - Includes faith-based custom slots

2. **TCDSB** (`config/boards/tcdsb.yaml`)
   - Toronto Catholic District School Board
   - English-language
   - Edsembli SIS
   - Character limits: 350-1200 total, 80-500 per section (more restrictive)
   - Includes program-specific custom slots

### Using a Board Preset

When exporting templates or comments, specify the board configuration:

```bash
# Export templates with NCDSB limits
edsembli export --board ncdsb --output ncdsb_templates.csv

# Export comment with TCDSB limits
edsembli export-comment --board tcdsb --child-file student.json --output comment.txt
```

The export commands will:
- Load the board configuration from `config/boards/{board_id}.yaml`
- Apply character limits during validation
- Use board-specific export settings (CSV encoding, delimiters, etc.)
- Warn if templates exceed board limits

### Creating a Custom Board Configuration

To create a configuration for your board:

1. **Copy an example preset**:
   ```bash
   cp config/boards/ncdsb.yaml config/boards/myboard.yaml
   ```

2. **Edit the YAML file** with your board's settings:
   ```yaml
   ---
   id: config.board.myboard
   type: board_config
   board_name: My School Board
   board_abbrev: MSB
   sis_platform: edsembli  # or powerschool, aspen, etc.
   locale: en
   
   char_limits:
     per_section_min: 100
     per_section_max: 600
     total_min: 400
     total_max: 1500
   
   required_sections:
     - key_learning
     - growth
     - next_steps
   
   export_settings:
     csv_encoding: utf-8-sig
     include_french: false
   ```

3. **Validate the configuration**:
   ```bash
   python scripts/validate.py
   ```

4. **Test with exports**:
   ```bash
   edsembli export --board myboard --output test.csv
   ```

### Board Configuration Schema

All board configurations must validate against `schemas/board_config.schema.json`. Key fields:

- **`char_limits`**: Min/max characters per section and total
- **`required_sections`**: Which sections must be present
- **`optional_sections`**: Additional sections (e.g., `faith_connections`)
- **`custom_slots`**: Board-specific template slots (e.g., `{cge_expectation}`)
- **`export_settings`**: CSV encoding, delimiter, metadata options
- **`readability_targets`**: Flesch Reading Ease and grade level ranges
- **`terminology`**: Board-specific term preferences

See the [Board Configuration Schema](../schemas/board_config.schema.json) for full documentation.

### Faith-Based Customization (Catholic Boards)

Catholic boards can use custom slots for faith-based language:

```yaml
custom_slots:
  faith_reference:
    type: text
    description: "Reference to Catholic Graduate Expectations"
    required: false
    default: ""
  
  cge_expectation:
    type: text
    description: "Specific CGE being developed (e.g., 'a reflective and creative thinker')"
    required: false
```

These slots can be used in templates:

```
{child} demonstrates care for others, {faith_reference}. This reflects 
the Catholic Graduate Expectation of being a caring family member.
```

---

## Customization Process

1. **Fork or branch** the main repository
2. **Create a board config** in `config/boards/yourboard.yaml`
3. **Document changes** in a local `customizations.md` file
4. **Validate** using the same scripts (`validate.py`, `lint.py`)
5. **Test exports** with `--board yourboard` flag
6. **Track upstream**: Periodically merge updates from main repo

## Support
For board-specific implementation support, contact your curriculum consultant or SIS administrator.
