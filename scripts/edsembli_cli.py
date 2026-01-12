from __future__ import annotations

import json
from pathlib import Path

import duckdb
import typer
from rich.console import Console
from rich.table import Table
from ruamel.yaml import YAML

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
