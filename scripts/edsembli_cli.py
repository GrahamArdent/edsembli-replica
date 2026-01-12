from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import typer
from rich.console import Console
from rich.table import Table
from ruamel.yaml import YAML

# Add lib to path for agent imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.agents.validation import ValidationAgent

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
