---
id: doc.integration.sis_formats
type: document
title: SIS Integration Formats
version: 0.1.2
status: stable
tags: [integration, sis, export, edsembli]
refs:
  - ref.ontario.kindergarten.program.2016
updated: 2026-01-12
---

# SIS Integration Formats

This document defines export formats for integrating Ontario Catholic Kindergarten Communication of Learning (CoL) templates and assembled comments with Student Information Systems (SIS), particularly Edsembli.

## Overview

The framework supports two primary export workflows:

1. **Template Bank Export**: Export the entire template library for bulk import into SIS comment banks
2. **Assembled Comment Export**: Export filled, student-specific comments ready for SIS entry

Both workflows produce SIS-compatible formats while preserving metadata for traceability.

In addition, VGReport (the local desktop app) supports a **Kindergarten-specific 12-box workflow** (4 Frames × 3 Sections). For maximum SIS compatibility, VGReport defines two “golden” Kindergarten exports:

1. **Clipboard-per-box**: copy/paste each box into SIS fields (highest compatibility)
2. **12-box CSV**: a stable, Excel-friendly interchange format (backup + bulk workflows)

---

## Template Bank Export

### Purpose

Export all templates in a format suitable for bulk import into SIS comment banks. This allows educators to:
- Populate SIS with framework-aligned comment options
- Enable dropdown/auto-complete selection during reporting
- Maintain consistent language across the school/board

### CSV Format (Primary)

**File:** `template_bank.csv`

**Columns:**

| Column | Type | Required | Description | Example |
|--------|------|----------|-------------|---------|
| `id` | string | Yes | Unique template identifier | `template.comment.belonging.key_learning.01` |
| `frame` | string | Yes | Pedagogical frame | `frame.belonging` |
| `section` | string | Yes | Comment section type | `key_learning`, `growth`, `next_steps` |
| `tone` | string | Yes | Language style | `parent_friendly` |
| `text` | string | Yes | English template with slots | `{child} demonstrates...` |
| `text_fr` | string | No | French template (if available) | `{child} démontre...` |
| `indicators` | string | Yes | Pipe-separated indicator IDs | `indicator.belonging.identity|indicator.belonging.relationships` |
| `version` | string | Yes | Template version | `0.1.0` |
| `status` | string | Yes | Lifecycle status | `draft`, `stable`, `deprecated` |
| `char_count` | integer | Yes | Character count (excluding slots) | `145` |
| `readability_flesch` | float | No | Flesch Reading Ease score | `72.5` |

**Encoding:** UTF-8 with BOM (for Excel compatibility)

**Line Endings:** CRLF (Windows)

**Delimiter:** Comma (`,`)

**Quoting:** RFC 4180 (quote fields containing commas, quotes, or newlines)

**Sample Row:**

```csv
id,frame,section,tone,text,text_fr,indicators,version,status,char_count,readability_flesch
template.comment.belonging.key_learning.01,frame.belonging,key_learning,parent_friendly,"{child} demonstrates a strong sense of belonging in our classroom community. {pronoun_subject} actively participates in group activities and shows respect for peers.",TODO,indicator.belonging.identity|indicator.belonging.relationships,0.1.0,stable,145,68.2
```

### JSON Format (Alternative)

**File:** `template_bank.json`

**Structure:**

```json
{
  "export_metadata": {
    "export_date": "2026-01-11T10:30:00Z",
    "framework_version": "0.1.0",
    "total_templates": 36,
    "filters_applied": {
      "status": ["stable"],
      "frame": null
    }
  },
  "templates": [
    {
      "id": "template.comment.belonging.key_learning.01",
      "type": "comment_template",
      "frame": "frame.belonging",
      "section": "key_learning",
      "tone": "parent_friendly",
      "slots": ["child", "pronoun_subject"],
      "text": "{child} demonstrates a strong sense of belonging in our classroom community. {pronoun_subject} actively participates in group activities and shows respect for peers.",
      "text_fr": "TODO",
      "indicators": [
        "indicator.belonging.identity",
        "indicator.belonging.relationships"
      ],
      "refs": ["ref.ontario.kindergarten.program.2016"],
      "status": "stable",
      "version": "0.1.0",
      "metadata": {
        "char_count": 145,
        "readability_flesch": 68.2,
        "readability_grade": 7.1
      }
    }
  ]
}
```

**Advantages:**
- Preserves nested structure (arrays, objects)
- No escaping issues with commas/quotes
- Supports rich metadata

**Use Case:** API integrations, programmatic imports

---

## Assembled Comment Export

### Purpose

Export student-specific comments after slot filling and assembly. These are final, ready-to-paste comments for SIS entry.

### Plain Text Format (Primary)

**File:** `{student_id}_comment.txt`

**Format:**

```
[Key Learning]
Emma demonstrates a strong sense of belonging in our classroom community. She actively participates in group activities and shows respect for peers.

[Growth]
Emma has shown significant growth in self-regulation this term. She now independently uses calm-down strategies when feeling frustrated, compared to earlier in the year when she required adult prompting.

[Next Steps]
To continue developing problem-solving skills, we encourage Emma to try multiple solutions before asking for help. At home, you can support this by asking "What else could you try?" when she encounters challenges.
```

**Characteristics:**
- Section headers in square brackets
- Blank line between sections
- No template metadata (IDs, slots, etc.)
- Character limit enforced: 400-1500 total, 100-600 per section
- UTF-8 encoding

### JSON Format (Batch Export)

**File:** `student_comments_batch.json`

**Structure:**

```json
{
  "export_metadata": {
    "export_date": "2026-01-11T10:30:00Z",
    "class_id": "K-2026-A",
    "teacher_name": "Mrs. Smith",
    "reporting_period": "Fall 2026",
    "total_students": 24
  },
  "comments": [
    {
      "student_id": "STU-12345",
      "student_name": "Emma Johnson",
      "comment_sections": {
        "key_learning": "Emma demonstrates a strong sense of belonging...",
        "growth": "Emma has shown significant growth in self-regulation...",
        "next_steps": "To continue developing problem-solving skills..."
      },
      "full_comment": "[Key Learning]\nEmma demonstrates...",
      "template_ids_used": [
        "template.comment.belonging.key_learning.01",
        "template.comment.selfregulation.growth.02",
        "template.comment.problemsolving.next_steps.01"
      ],
      "metadata": {
        "total_length": 487,
        "indicator_count": 3,
        "flesch_reading_ease": 71.2,
        "assembled_at": "2026-01-11T10:30:15Z"
      }
    }
  ]
}
```

**Use Case:** Bulk export for class, API upload to SIS

---

## VGReport Kindergarten 12-Box Exports (Golden Outputs)

These exports are designed for the VGReport Kindergarten workflow where comments are authored as **12 independent fields** rather than a single 3-section assembled narrative.

### A) Clipboard-per-box (Primary)

**Purpose:** Maximize compatibility by supporting the lowest-common-denominator workflow: paste text into SIS “live form” fields.

**Characteristics:**
- One clipboard payload per box (Frame × Section)
- Text is copied as plain text
- Newlines are normalized to CRLF (`\r\n`) for Windows-friendly pasting
- No metadata is included in the pasted text

**Recommended UI behaviors (VGReport):**
- Provide a copy button on each box
- Optionally provide “Copy all 12 boxes” which copies a clearly delimited block with headings so the user can paste sequentially

**Example payload (single box):**
```
Emma demonstrates a strong sense of belonging in our classroom community. She participates in group activities and shows respect for peers.
```

### B) 12-box CSV (Secondary; Excel-friendly)

**Purpose:** Provide a stable interchange format compatible with Excel and downstream tooling, even when SIS import behavior is unclear.

**Encoding:** UTF-8 with BOM (Excel compatibility)

**Line Endings:** CRLF (Windows)

**Delimiter:** Comma (`,`)

**Quoting:** Always quote every field (most robust when comments include commas, quotes, or newlines)

**Column order (stable):**

Student identifiers:
- `student_local_id` (string) — required
- `student_last_name` (string) — recommended
- `student_first_name` (string) — recommended
- `report_period_id` (string) — required (board/app configured; commonly `initial`, `february`, `june`)

Kindergarten boxes (12 fields; required for “export-ready”):
- `belonging_key_learning`
- `belonging_growth`
- `belonging_next_steps`
- `self_regulation_key_learning`
- `self_regulation_growth`
- `self_regulation_next_steps`
- `literacy_math_key_learning`
- `literacy_math_growth`
- `literacy_math_next_steps`
- `problem_solving_key_learning`
- `problem_solving_growth`
- `problem_solving_next_steps`

**Notes:**
- Frame slugs map to canonical taxonomy keys: `belonging` → `frame.belonging`, `self_regulation` → `frame.self_regulation`, `literacy_math` → `frame.literacy_math`, `problem_solving` → `frame.problem_solving`.
- Section slugs map to canonical section keys: `key_learning`, `growth`, `next_steps`.

**Sample header:**
```csv
"student_local_id","student_last_name","student_first_name","report_period_id","belonging_key_learning","belonging_growth","belonging_next_steps","self_regulation_key_learning","self_regulation_growth","self_regulation_next_steps","literacy_math_key_learning","literacy_math_growth","literacy_math_next_steps","problem_solving_key_learning","problem_solving_growth","problem_solving_next_steps"
```

---

## SIS-Specific Considerations

### Edsembli

**Import Method:** CSV upload via Admin > Comment Banks

**Requirements:**
- CSV must have header row
- Maximum field length: 1000 characters (per field)
- Supports UTF-8 encoding
- Recommends CRLF line endings

**Field Mapping:**

| Framework Column | Edsembli Column | Notes |
|------------------|-----------------|-------|
| `id` | `Comment ID` | Optional; Edsembli auto-generates if blank |
| `text` | `Comment Text (English)` | Required |
| `text_fr` | `Comment Text (French)` | Optional |
| `section` | `Category` | Map to custom categories |
| `frame` | `Tags` | Pipe-separated |

**Character Limits:**
- Comment text: 1000 chars (framework default: 300)
- Full report: 4000 chars (framework default: 1500)

**Customization:**
- Use board config (`config/boards/*.yaml`) to adjust limits
- If an Edsembli-specific preset exists (e.g., `config/boards/edsembli.yaml`), it should define recommended limits and export defaults

### PowerSchool / Aspen / Other SIS

**Future Support:** Phase 5 Sprint 5.2 will add board-specific presets.

**Generic CSV Export:** Current export format is compatible with most SIS accepting CSV import.

---

## Export Commands (CLI)

### Template Bank Export

```bash
# Export all templates to CSV
edsembli export --format csv --output template_bank.csv

# Export stable templates only (exclude drafts/deprecated)
edsembli export --format csv --status stable --output stable_templates.csv

# Export specific frame
edsembli export --format csv --frame frame.belonging --output belonging_templates.csv

# Export as JSON
edsembli export --format json --output template_bank.json
```

**Options:**
- `--format`: `csv` (default) or `json`
- `--output`: Output file path
- `--status`: Filter by status (`draft`, `stable`, `deprecated`)
- `--frame`: Filter by frame ID
- `--section`: Filter by section (`key_learning`, `growth`, `next_steps`)

### Assembled Comment Export

```bash
# Export single student comment
edsembli export-comment --child-file student_data.json --output emma_comment.txt

# Export batch (all students in JSON file)
edsembli export-comment --batch student_batch.json --output-dir comments/

# Export with template selection
edsembli export-comment --child-file student_data.json \
  --templates templates_selected.yaml \
  --output emma_comment.txt
```

**Child Data Format (`student_data.json`):**

```json
{
  "student_id": "STU-12345",
  "child": "Emma",
  "pronoun_subject": "She",
  "pronoun_object": "her",
  "pronoun_possessive": "her",
  "evidence": "building with blocks",
  "strength": "spatial reasoning",
  "change": "using more complex patterns",
  "previous": "simple stacking",
  "goal": "create 3D structures"
}
```

**Template Selection Format (`templates_selected.yaml`):**

```yaml
template_ids:
  key_learning:
    - template.comment.belonging.key_learning.01
  growth:
    - template.comment.selfregulation.growth.02
  next_steps:
    - template.comment.problemsolving.next_steps.01
```

---

## Validation & Quality Gates

### Pre-Export Validation

Before exporting, the system validates:

1. **Template Schema Compliance**
   - All required fields present
   - Slot syntax valid
   - Indicator references exist

2. **Character Limits**
   - Per-section limits respected (100-600 chars)
   - Total comment within board limits (400-1500 chars default)

3. **Readability**
   - Flesch Reading Ease: 60-80 (target)
   - Flesch-Kincaid Grade: 6-8 (target)
   - Warnings logged, not blocking

4. **Bilingual Completeness**
   - If `status: stable`, `text_fr` must exist
   - Warnings for missing French translations

### Post-Export Checks

After exporting:

1. **File Integrity**
   - UTF-8 encoding verified
   - CSV row count matches template count
   - JSON structure validates against schema

2. **Import Readiness**
   - Sample SIS import tested (manual)
   - Character limits compatible with target SIS
   - Field mappings documented

---

## Board Customization

Different school boards may have different SIS limits. Use board config files to override defaults.

**Example:** `config/boards/tcdsb.yaml`

```yaml
board_id: tcdsb
board_name: Toronto Catholic District School Board
sis_platform: edsembli
sis_version: "2024.1"

character_limits:
  per_section_min: 80
  per_section_max: 500
  total_min: 350
  total_max: 1200

export_settings:
  csv_delimiter: ","
  csv_encoding: utf-8-sig  # UTF-8 with BOM
  include_metadata: true
  include_french: true

required_sections:
  - key_learning
  - growth
  - next_steps
```

**Usage:**

```bash
edsembli export --board tcdsb --output tcdsb_templates.csv
```

This applies TCDSB-specific limits and formatting.

---

## Security & Privacy

### PII Handling

**Template Bank Export:**
- Templates contain NO PII (only slots like `{child}`)
- Safe to share across schools/boards

**Assembled Comment Export:**
- Contains student names, pronouns, specific evidence
- **CRITICAL:** Treat as confidential student records
- Encrypt files in transit (use SFTP, not email)
- Delete from local system after SIS upload

### Audit Trail

All exports log:
- Timestamp
- User (if applicable)
- Filters applied
- Output file path
- Template/student count

**Log Location:** `logs/exports.log`

**Example Entry:**

```
2026-01-11T10:30:00Z | USER:teacher@school.ca | ACTION:export | FORMAT:csv | STATUS:stable | FRAME:all | OUTPUT:template_bank.csv | COUNT:36
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| CSV won't open in Excel | Encoding mismatch | Use `--format csv` with UTF-8 BOM |
| Characters cut off in SIS | Exceeds field limit | Use board config to enforce lower limits |
| French text shows as `???` | Wrong encoding | Ensure UTF-8 encoding in SIS import settings |
| Missing templates in export | Status filter too restrictive | Remove `--status` filter or include drafts |

### Validation Errors

If export fails validation:

```bash
# View detailed errors
edsembli export --format csv --output templates.csv --verbose

# Fix templates
edsembli review templates/comment_templates.yaml

# Re-export after fixes
edsembli export --format csv --output templates.csv
```

---

## Future Enhancements

### Phase 5 Sprint 5.2
- Board-specific presets (NCDSB, TCDSB, etc.)
- XML export format (PowerSchool compatibility)
- Direct SIS API integration (if available)

### Phase 6
- Bilingual export with verified French translations
- Translation memory export for CAT tools

---

## References

- [Comment Assembly Rules](../guidance/comment-assembly.md)
- [Slot Guidance](../../taxonomy/slot_guidance.yaml)
- [Board Customization Guidance](../guidance/board-customization.md)

---

*Document Version: 0.1.0*
*Last Updated: 2026-01-11*
