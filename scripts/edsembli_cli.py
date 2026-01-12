from __future__ import annotations

import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import duckdb
import typer
from rich.console import Console
from rich.table import Table
from ruamel.yaml import YAML

# Add lib to path for agent imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.agents.validation import ValidationAgent
from lib.pipeline.assemble import AssemblyRequest, CommentAssembler

try:
    import textstat  # type: ignore[import-untyped]

    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

app = typer.Typer(add_completion=False, help="Lightweight query tools for this design repo")
console = Console()

ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = YAML(typ="safe")


def _load_templates() -> list[dict]:
    path = ROOT / "templates" / "comment_templates.yaml"
    with path.open("r", encoding="utf-8") as handle:
        data = YAML_LOADER.load(handle) or {}
    templates = data.get("templates", [])
    return [t for t in templates if isinstance(t, dict)]


def _load_board_config(board_id: str) -> dict | None:
    """Load board configuration from config/boards/{board_id}.yaml.

    Board config files have YAML frontmatter followed by YAML configuration data.
    """
    config_path = ROOT / "config" / "boards" / f"{board_id}.yaml"
    if not config_path.exists():
        console.print(f"[yellow]Board config not found: {config_path}[/yellow]")
        return None

    try:
        with config_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Remove frontmatter (everything between first two --- markers)
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_content = parts[2].strip()
        else:
            yaml_content = content.strip()

        config = YAML_LOADER.load(yaml_content) or {}
        return config
    except Exception as e:
        console.print(f"[red]Error loading board config {board_id}: {e}[/red]")
        return None


@app.command("template-search")
def template_search(
    query: str = typer.Argument(..., help="Substring to match against id/text"),
    frame: str | None = typer.Option(None, "--frame", help="Filter by frame id"),
    indicator: str | None = typer.Option(None, "--indicator", help="Filter by indicator id"),
    limit: int = typer.Option(20, "--limit", min=1, max=200),
) -> None:
    templates = _load_templates()
    q = query.lower()

    matches: list[dict] = []
    for t in templates:
        if frame and t.get("frame") != frame:
            continue
        if indicator and indicator not in (t.get("indicators") or []):
            continue

        hay = "\n".join([str(t.get("id", "")), str(t.get("text", ""))]).lower()
        if q in hay:
            matches.append(t)

    table = Table(title=f"Templates matching '{query}'")
    table.add_column("id", overflow="fold")
    table.add_column("frame")
    table.add_column("section")
    table.add_column("indicators", overflow="fold")

    for t in matches[:limit]:
        table.add_row(
            str(t.get("id", "")),
            str(t.get("frame", "")),
            str(t.get("section", "")),
            ", ".join(t.get("indicators") or []),
        )

    console.print(table)
    if len(matches) > limit:
        console.print(f"Showing {limit}/{len(matches)} matches")


@app.command("matrix-sql")
def matrix_sql(
    sql: str = typer.Argument(..., help="SQL to run. The matrix is available as table 'matrix'."),
    prefer_parquet: bool = typer.Option(True, "--prefer-parquet/--prefer-csv"),
    limit: int = typer.Option(50, "--limit", min=1, max=500),
) -> None:
    data_dir = ROOT / "datasets" / "traceability"
    parquet_path = data_dir / "matrix.parquet"
    csv_path = data_dir / "matrix.csv"

    con = duckdb.connect(database=":memory:")
    if prefer_parquet and parquet_path.exists():
        con.execute(f"CREATE VIEW matrix AS SELECT * FROM read_parquet('{parquet_path}')")
    else:
        # ref_ids is JSON in the CSV; keep as text for ad-hoc queries
        con.execute(f"CREATE VIEW matrix AS SELECT * FROM read_csv_auto('{csv_path}', HEADER=TRUE)")

    q = sql.strip().rstrip(";")
    if "limit" not in q.lower():
        q = f"{q} LIMIT {limit}"

    try:
        rel = con.execute(q)
    except Exception as exc:
        raise typer.BadParameter(str(exc)) from exc

    rows = rel.fetchall()
    cols = [d[0] for d in rel.description]

    table = Table(title="Matrix query")
    for c in cols:
        table.add_column(str(c), overflow="fold")

    for row in rows:
        table.add_row(*[json.dumps(v) if isinstance(v, (list, dict)) else str(v) for v in row])

    console.print(table)


@app.command("evidence-matrix")
def evidence_matrix(
    template_id: str | None = typer.Option(None, "--template", help="Filter to specific template ID"),
    min_score: int = typer.Option(5, "--min-score", help="Minimum relevance score to display"),
) -> None:
    """Show heuristic evidence-template matches with relevance scores.

    Uses algorithm from ADR-001:
    - Frame match: +3
    - Indicator match: +5
    - Preferred evidence bonus: +10
    """
    templates = _load_templates()
    evidence_patterns = _load_evidence()

    if template_id:
        templates = [t for t in templates if t.get("id") == template_id]
        if not templates:
            console.print(f"[red]Template {template_id} not found[/red]")
            raise typer.Exit(1)

    table = Table(title="Evidence-Template Heuristic Matches")
    table.add_column("Template ID", overflow="fold")
    table.add_column("Evidence Pattern", overflow="fold")
    table.add_column("Score", justify="right")
    table.add_column("Reason", overflow="fold")

    total_matches = 0
    for tmpl in templates:
        matches = _match_evidence(tmpl, evidence_patterns, min_score)
        for ev_id, score, reason in matches:
            table.add_row(str(tmpl.get("id", "")), ev_id, str(score), reason)
            total_matches += 1

    console.print(table)
    console.print(f"\nTotal matches (score ≥ {min_score}): {total_matches}")


@app.command("templates")
def templates_command(
    show_deprecated: bool = typer.Option(False, "--show-deprecated", help="Show only deprecated templates"),
) -> None:
    """List templates with their deprecation status."""
    templates = _load_templates()

    if show_deprecated:
        templates = [t for t in templates if t.get("status") == "deprecated"]

    table = Table(title="Templates" if not show_deprecated else "Deprecated Templates")
    table.add_column("ID", overflow="fold")
    table.add_column("Frame")
    table.add_column("Section")
    table.add_column("Status")
    if show_deprecated:
        table.add_column("Replaced By", overflow="fold")

    for t in templates:
        tid = str(t.get("id", ""))
        frame = str(t.get("frame", ""))
        section = str(t.get("section", ""))
        status = str(t.get("status", "draft"))

        if show_deprecated:
            deprecated_by = str(t.get("deprecated_by", "N/A"))
            table.add_row(tid, frame, section, status, deprecated_by)
        else:
            table.add_row(tid, frame, section, status)

    console.print(table)
    console.print(f"\nTotal: {len(templates)} templates")


def _load_evidence() -> list[dict]:
    """Load evidence patterns from markdown files."""
    evidence_dir = ROOT / "evidence"
    patterns = []

    for md_file in evidence_dir.glob("evidence.pattern.*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            # Extract YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = YAML_LOADER.load(parts[1])
                    if isinstance(frontmatter, dict):
                        patterns.append(frontmatter)
        except Exception:
            continue

    return patterns


def _match_evidence(template: dict, evidence_pool: list[dict], min_score: int = 5) -> list[tuple[str, int, str]]:
    """Match evidence patterns to template using ADR-001 algorithm.

    Returns: List of (evidence_id, score, reason) tuples sorted by score descending.
    """
    tmpl_frame = template.get("frame")
    tmpl_indicators = template.get("indicators", [])
    tmpl_preferred = template.get("preferred_evidence", [])

    matches = []
    for ev in evidence_pool:
        ev_id = ev.get("id", "")
        ev_frame = ev.get("frame")
        ev_indicators = ev.get("indicators", [])

        score = 0
        reasons = []

        # Frame match: +3
        if ev_frame and ev_frame == tmpl_frame:
            score += 3
            reasons.append("frame")

        # Indicator match: +5 per matching indicator
        indicator_matches = [ind for ind in ev_indicators if ind in tmpl_indicators]
        if indicator_matches:
            score += 5 * len(indicator_matches)
            reasons.append(f"{len(indicator_matches)} indicator(s)")

        # Preferred evidence bonus: +10
        if ev_id in tmpl_preferred:
            score += 10
            reasons.append("preferred")

        if score >= min_score:
            reason_text = ", ".join(reasons) if reasons else "no match"
            matches.append((ev_id, score, reason_text))

    # Sort by score descending
    return sorted(matches, key=lambda x: -x[1])


@app.command("review")
def review_template(
    draft_file: Path,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show full validation details"),
) -> None:
    """Review a draft template with automated validation.

    Validates schema, privacy, slots, indicators, and readability.
    Provides pass/fail/needs_revision status with actionable feedback.

    Args:
        draft_file: Path to draft template YAML file (required positional argument)
        verbose: Show full validation details (optional flag)
    """
    console.print(f"\n[bold]Reviewing template:[/bold] {draft_file}", style="blue")

    # Load the draft template
    try:
        with draft_file.open("r", encoding="utf-8") as f:
            drafts = YAML_LOADER.load(f)
            if isinstance(drafts, list):
                draft = drafts[0]  # Take first template if list
            else:
                draft = drafts
    except Exception as e:
        console.print(f"[red]Error loading file:[/red] {e}")
        raise typer.Exit(1) from e

    # Run validation
    agent = ValidationAgent()
    result = agent.validate(draft)

    # Display results
    console.print()
    status_colors = {"pass": "green", "needs_revision": "yellow", "fail": "red"}
    status_color = status_colors.get(result.overall_status, "white")
    console.print(f"[bold {status_color}]Status: {result.overall_status.upper()}[/bold {status_color}]")
    console.print()

    # Show checks summary
    table = Table(title="Validation Checks")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")

    checks = [
        ("Schema Compliance", result.schema_valid),
        ("Privacy & Safety", result.privacy_safe),
        ("Slot Consistency", result.slots_consistent),
        ("Indicator Alignment", result.indicators_valid),
    ]

    for check_name, passed in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        color = "green" if passed else "red"
        table.add_row(check_name, f"[{color}]{status}[/{color}]")

    console.print(table)
    console.print()

    # Show readability scores
    if result.readability_score is not None and result.readability_grade is not None:
        console.print("[bold]Readability:[/bold]")
        console.print(f"  Flesch Reading Ease: {result.readability_score:.1f}")
        console.print(f"  Flesch-Kincaid Grade: {result.readability_grade:.1f}")
        target_met = 60 <= result.readability_score <= 80 and 6 <= result.readability_grade <= 8
        if target_met:
            console.print("  [green]✓ Meets readability targets[/green]")
        else:
            console.print("  [yellow]⚠ Outside readability targets (Flesch 60-80, Grade 6-8)[/yellow]")
        console.print()

    # Show errors
    if result.errors:
        console.print("[bold red]Errors:[/bold red]")
        for error in result.errors:
            console.print(f"  • {error}", style="red")
        console.print()

    # Show warnings
    if result.warnings:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for warning in result.warnings:
            console.print(f"  • {warning}", style="yellow")
        console.print()

    # Show suggestions
    if result.suggestions:
        console.print("[bold cyan]Suggestions:[/bold cyan]")
        for suggestion in result.suggestions:
            console.print(f"  • {suggestion}", style="cyan")
        console.print()

    # Show full template if verbose
    if verbose:
        console.print("[bold]Draft Template:[/bold]")
        console.print(json.dumps(draft, indent=2))
        console.print()

    # Exit code based on status
    if result.overall_status == "fail":
        console.print("[red]❌ Template failed validation. Fix errors and try again.[/red]")
        raise typer.Exit(1)
    elif result.overall_status == "needs_revision":
        console.print("[yellow]⚠ Template needs revision. Address warnings before finalizing.[/yellow]")
        raise typer.Exit(0)
    else:
        console.print("[green]✅ Template passed validation![/green]")
        raise typer.Exit(0)


@app.command("export")
def export_templates(
    format: Annotated[str, typer.Option("--format", help="Export format: csv, json, or translation-csv")] = "csv",
    output: Annotated[Path | None, typer.Option("--output", help="Output file path")] = None,
    status: Annotated[str | None, typer.Option("--status", help="Filter by status (draft, stable, deprecated)")] = None,
    frame: Annotated[str | None, typer.Option("--frame", help="Filter by frame ID")] = None,
    section: Annotated[
        str | None, typer.Option("--section", help="Filter by section (key_learning, growth, next_steps)")
    ] = None,
    board: Annotated[str | None, typer.Option("--board", help="Board ID (e.g., ncdsb, tcdsb)")] = None,
) -> None:
    """Export template bank to CSV, JSON, or translation-ready CSV for SIS import."""
    templates = _load_templates()

    # Load board config if specified
    board_config = None
    if board:
        board_config = _load_board_config(board)
        if board_config:
            console.print(f"[blue]Using board config: {board_config.get('board_name', board)}[/blue]")

    # Apply filters
    filtered: list[dict] = []
    for t in templates:
        if status and t.get("status") != status:
            continue
        if frame and t.get("frame") != frame:
            continue
        if section and t.get("section") != section:
            continue
        filtered.append(t)

    if not filtered:
        console.print("[yellow]No templates match the specified filters.[/yellow]")
        raise typer.Exit(1)

    # Validate against board limits if config provided
    if board_config and "char_limits" in board_config:
        limits = board_config["char_limits"]
        warnings = []
        for t in filtered:
            text = t.get("text", "")
            # Calculate char count excluding slots
            char_count = len(text)
            for slot in t.get("slots", []):
                slot_pattern = f"{{{slot}}}"
                char_count -= text.count(slot_pattern) * len(slot_pattern)

            if char_count > limits.get("per_section_max", float("inf")):
                warnings.append(
                    f"Template {t.get('id')} exceeds board limit: {char_count} > {limits['per_section_max']}"
                )

        if warnings:
            console.print("[yellow]⚠ Board limit warnings:[/yellow]")
            for w in warnings[:5]:  # Show first 5
                console.print(f"  {w}")
            if len(warnings) > 5:
                console.print(f"  ... and {len(warnings) - 5} more warnings")

    # Determine output path
    if output is None:
        if format == "translation-csv":
            output = ROOT / "translations.csv"
        else:
            output = ROOT / f"template_bank.{format}"
    else:
        output = Path(output).resolve()

    # Export
    if format == "csv":
        _export_csv(filtered, output)
    elif format == "json":
        _export_json(filtered, output, status, frame, section)
    elif format == "translation-csv":
        _export_translation_csv(filtered, output)
    else:
        console.print(f"[red]Unsupported format: {format}. Use 'csv', 'json', or 'translation-csv'.[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Exported {len(filtered)} templates to {output}")


def _export_csv(templates: list[dict], output: Path) -> None:
    """Export templates to CSV format."""
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "id",
            "frame",
            "section",
            "tone",
            "text",
            "text_fr",
            "indicators",
            "version",
            "status",
            "char_count",
            "readability_flesch",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for t in templates:
            # Calculate character count (excluding slots)
            text = t.get("text", "")
            char_count = len(text)
            for slot in t.get("slots", []):
                slot_pattern = f"{{{slot}}}"
                char_count -= text.count(slot_pattern) * len(slot_pattern)

            # Calculate readability
            readability_flesch = None
            try:
                if HAS_TEXTSTAT:
                    readability_flesch = textstat.flesch_reading_ease(text)
            except Exception:
                pass  # Optional metric

            writer.writerow(
                {
                    "id": t.get("id", ""),
                    "frame": t.get("frame", ""),
                    "section": t.get("section", ""),
                    "tone": t.get("tone", ""),
                    "text": t.get("text", ""),
                    "text_fr": t.get("text_fr", "TODO"),
                    "indicators": "|".join(t.get("indicators", [])),
                    "version": t.get("version", "0.1.0"),
                    "status": t.get("status", "draft"),
                    "char_count": char_count,
                    "readability_flesch": f"{readability_flesch:.1f}" if readability_flesch else "",
                }
            )


def _export_json(
    templates: list[dict], output: Path, status: str | None, frame: str | None, section: str | None
) -> None:
    """Export templates to JSON format."""
    output.parent.mkdir(parents=True, exist_ok=True)

    export_data = {
        "export_metadata": {
            "export_date": datetime.now(UTC).isoformat(),
            "framework_version": "0.1.0",
            "total_templates": len(templates),
            "filters_applied": {"status": [status] if status else None, "frame": frame, "section": section},
        },
        "templates": [],
    }

    for t in templates:
        # Calculate metadata
        text = t.get("text", "")
        char_count = len(text)
        for slot in t.get("slots", []):
            slot_pattern = f"{{{slot}}}"
            char_count -= text.count(slot_pattern) * len(slot_pattern)

        readability_flesch = None
        readability_grade = None
        try:
            if HAS_TEXTSTAT:
                readability_flesch = textstat.flesch_reading_ease(text)
                readability_grade = textstat.flesch_kincaid_grade(text)
        except Exception:
            pass

        template_export = {
            "id": t.get("id"),
            "type": t.get("type", "comment_template"),
            "frame": t.get("frame"),
            "section": t.get("section"),
            "tone": t.get("tone"),
            "slots": t.get("slots", []),
            "text": t.get("text"),
            "text_fr": t.get("text_fr", "TODO"),
            "indicators": t.get("indicators", []),
            "refs": t.get("refs", []),
            "status": t.get("status", "draft"),
            "version": t.get("version", "0.1.0"),
            "metadata": {
                "char_count": char_count,
                "readability_flesch": round(readability_flesch, 1) if readability_flesch else None,
                "readability_grade": round(readability_grade, 1) if readability_grade else None,
            },
        }
        export_data["templates"].append(template_export)

    with output.open("w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def _export_translation_csv(templates: list[dict], output: Path) -> None:
    """Export templates to translation-ready CSV format.

    This format is designed for translators to fill in the text_fr column.
    Columns: id, frame, section, slots, text (English), text_fr (empty for translator to fill).
    """
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["id", "frame", "section", "slots", "text", "text_fr"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for t in templates:
            writer.writerow(
                {
                    "id": t.get("id", ""),
                    "frame": t.get("frame", ""),
                    "section": t.get("section", ""),
                    "slots": "|".join(t.get("slots", [])),
                    "text": t.get("text", "").strip(),
                    "text_fr": "",  # Empty for translator to fill
                }
            )


@app.command("import-translations")
def import_translations(
    file: Annotated[Path, typer.Argument(help="CSV file with completed translations")],
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview changes without modifying files")] = False,
) -> None:
    """Import French translations from CSV and update template library.

    CSV must have columns: id, text_fr
    Validates that slot placeholders match between English and French text.
    """
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise typer.Exit(1)

    # Load translations from CSV
    translations: dict[str, str] = {}
    try:
        with file.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                template_id = row.get("id", "").strip()
                text_fr = row.get("text_fr", "").strip()
                if template_id and text_fr:
                    translations[template_id] = text_fr
    except Exception as e:
        console.print(f"[red]Error reading CSV: {e}[/red]")
        raise typer.Exit(1) from None

    if not translations:
        console.print("[yellow]No translations found in CSV.[/yellow]")
        raise typer.Exit(1)

    console.print(f"[blue]Found {len(translations)} translations in CSV[/blue]")

    # Load current templates
    templates = _load_templates()
    templates_by_id = {t.get("id"): t for t in templates}

    # Validate and prepare updates
    updates: list[tuple[str, str, str]] = []  # (template_id, old_text_fr, new_text_fr)
    errors: list[str] = []

    for template_id, text_fr in translations.items():
        if template_id not in templates_by_id:
            errors.append(f"Template not found: {template_id}")
            continue

        template = templates_by_id[template_id]
        slots_en = template.get("slots", [])

        # Validate slot consistency
        missing_slots = []
        extra_slots = []
        for slot in slots_en:
            if f"{{{slot}}}" not in text_fr:
                missing_slots.append(slot)

        # Check for slots in French that aren't in English
        import re

        slots_fr = re.findall(r"\{([^}]+)\}", text_fr)
        for slot in slots_fr:
            if slot not in slots_en:
                extra_slots.append(slot)

        if missing_slots or extra_slots:
            error_parts = []
            if missing_slots:
                error_parts.append(f"missing slots: {', '.join(missing_slots)}")
            if extra_slots:
                error_parts.append(f"extra slots: {', '.join(extra_slots)}")
            errors.append(f"{template_id}: {' | '.join(error_parts)}")
            continue

        # Record update
        old_text_fr = template.get("text_fr", "TODO")
        updates.append((template_id, old_text_fr, text_fr))

    # Show results
    if errors:
        console.print("[bold red]Validation Errors:[/bold red]")
        for error in errors:
            console.print(f"  • {error}", style="red")

    if not updates:
        console.print("[yellow]No valid translations to import.[/yellow]")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] {len(updates)} translations validated successfully")

    if dry_run:
        console.print("\n[bold cyan]Preview of changes (--dry-run):[/bold cyan]")
        for template_id, old, new in updates[:5]:  # Show first 5
            console.print(f"\n[blue]{template_id}[/blue]")
            console.print(f"  Old: {old[:80]}...")
            console.print(f"  New: {new[:80]}...")
        if len(updates) > 5:
            console.print(f"\n... and {len(updates) - 5} more translations")
        console.print("\n[yellow]Run without --dry-run to apply changes.[/yellow]")
        return

    # Apply updates to YAML file
    template_file = ROOT / "templates" / "comment_templates.yaml"

    try:
        with template_file.open("r", encoding="utf-8") as f:
            content = f.read()

        # Update each template's text_fr field
        for template_id, _old_text_fr, new_text_fr in updates:
            # Find the template block and update text_fr
            # This is a simple regex replacement - assumes text_fr is on its own line
            # Pattern: find "id: template_id" block, then replace "text_fr: ..." line
            pattern = rf"(- id: {re.escape(template_id)}.*?text_fr:)([^\n]*)"
            replacement = rf'\1 "{new_text_fr}"'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Write back
        with template_file.open("w", encoding="utf-8") as f:
            f.write(content)

        console.print(f"[green]✓[/green] Updated {len(updates)} templates in {template_file}")

    except Exception as e:
        console.print(f"[red]Error updating template file: {e}[/red]")
        raise typer.Exit(1) from None


@app.command("export-comment")
def export_comment(
    child_file: Annotated[Path, typer.Option("--child-file", help="JSON file with student slot data")],
    templates_file: Annotated[
        Path | None, typer.Option("--templates", help="YAML file with selected template IDs")
    ] = None,
    output: Annotated[Path | None, typer.Option("--output", help="Output file path (.txt)")] = None,
    format: Annotated[str, typer.Option("--format", help="Export format: txt or json")] = "txt",
    board: Annotated[str | None, typer.Option("--board", help="Board ID (e.g., ncdsb, tcdsb)")] = None,
) -> None:
    """Export assembled comment for a student."""
    # Load board config if specified
    board_config = None
    if board:
        board_config = _load_board_config(board)
        if board_config:
            console.print(f"[blue]Using board config: {board_config.get('board_name', board)}[/blue]")

    # Load student data
    child_file = Path(child_file).resolve()
    if not child_file.exists():
        console.print(f"[red]Child file not found: {child_file}[/red]")
        raise typer.Exit(1)

    with child_file.open("r", encoding="utf-8") as f:
        child_data = json.load(f)

    # Load template selections
    template_ids: dict[str, list[str]] = {}
    if templates_file:
        templates_file = Path(templates_file).resolve()
        if not templates_file.exists():
            console.print(f"[red]Templates file not found: {templates_file}[/red]")
            raise typer.Exit(1)

        with templates_file.open("r", encoding="utf-8") as f:
            template_data = YAML_LOADER.load(f) or {}
            template_ids = template_data.get("template_ids", {})
    else:
        # Default: use first template for each section (for demo purposes)
        templates = _load_templates()
        for section in ["key_learning", "growth", "next_steps"]:
            section_templates = [t for t in templates if t.get("section") == section]
            if section_templates:
                template_ids[section] = [section_templates[0]["id"]]

    # Assemble comment
    assembler = CommentAssembler()
    request = AssemblyRequest(template_ids=template_ids, child_data=child_data)

    result = assembler.assemble(request)

    if result.errors:
        console.print("[red]Assembly errors:[/red]")
        for error in result.errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)

    # Validate against board limits if config provided
    if board_config and "char_limits" in board_config and result.comment:
        limits = board_config["char_limits"]
        total_length = len(result.comment)

        # Check total length
        if total_length > limits.get("total_max", float("inf")):
            console.print(
                f"[yellow]⚠ Comment exceeds board maximum: {total_length} > {limits['total_max']} chars[/yellow]"
            )
        elif total_length < limits.get("total_min", 0):
            console.print(
                f"[yellow]⚠ Comment below board minimum: {total_length} < {limits['total_min']} chars[/yellow]"
            )

        # Check section lengths
        if result.stats and "section_lengths" in result.stats:
            for section, length in result.stats["section_lengths"].items():
                if length > limits.get("per_section_max", float("inf")):
                    max_len = limits["per_section_max"]
                    console.print(f"[yellow]⚠ Section '{section}' exceeds maximum: {length} > {max_len} chars[/yellow]")

    # Determine output path
    if output is None:
        student_id = child_data.get("student_id", "student")
        output = ROOT / f"{student_id}_comment.{format}"
    else:
        output = Path(output).resolve()

    # Export
    if format == "txt":
        _export_comment_txt(result.comment, output)
    elif format == "json":
        _export_comment_json(result, child_data, template_ids, output)
    else:
        console.print(f"[red]Unsupported format: {format}. Use 'txt' or 'json'.[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Exported comment to {output}")


def _export_comment_txt(comment: str | None, output: Path) -> None:
    """Export assembled comment to plain text format."""
    if not comment:
        raise ValueError("No comment to export")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        f.write(comment)


def _export_comment_json(result, child_data: dict, template_ids: dict[str, list[str]], output: Path) -> None:
    """Export assembled comment to JSON format."""
    output.parent.mkdir(parents=True, exist_ok=True)

    # Extract section texts from full comment
    comment_sections: dict[str, str] = {}
    if result.comment:
        sections = result.comment.split("\n\n")
        for section_text in sections:
            if section_text.startswith("[Key Learning]"):
                comment_sections["key_learning"] = section_text.replace("[Key Learning]\n", "").strip()
            elif section_text.startswith("[Growth]"):
                comment_sections["growth"] = section_text.replace("[Growth]\n", "").strip()
            elif section_text.startswith("[Next Steps]"):
                comment_sections["next_steps"] = section_text.replace("[Next Steps]\n", "").strip()

    # Flatten template IDs
    all_template_ids = []
    for section_list in template_ids.values():
        all_template_ids.extend(section_list)

    # Extract stats
    flesch_reading_ease = None
    if result.stats:
        flesch_reading_ease = result.stats.get("flesch_reading_ease")

    export_data = {
        "student_id": child_data.get("student_id", "unknown"),
        "student_name": child_data.get("child", "Unknown"),
        "comment_sections": comment_sections,
        "full_comment": result.comment,
        "template_ids_used": all_template_ids,
        "metadata": {
            "total_length": len(result.comment) if result.comment else 0,
            "indicator_count": len(set(result.stats.get("indicators", []))) if result.stats else 0,
            "flesch_reading_ease": flesch_reading_ease,
            "assembled_at": datetime.now(UTC).isoformat(),
        },
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
