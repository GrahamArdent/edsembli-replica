from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "datasets" / "traceability"
CSV_PATH = DATA_DIR / "matrix.csv"
PARQUET_PATH = DATA_DIR / "matrix.parquet"
SCHEMA_PATH = DATA_DIR / "matrix.schema.json"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _fail(message: str) -> None:
    raise SystemExit(message)


def _validate_csv_contract() -> None:
    if not CSV_PATH.exists():
        _fail(f"Missing dataset: {CSV_PATH.relative_to(ROOT)}")
    if not SCHEMA_PATH.exists():
        _fail(f"Missing schema: {SCHEMA_PATH.relative_to(ROOT)}")

    schema_descriptor = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    expected_fields = [f["name"] for f in schema_descriptor.get("fields", []) if isinstance(f, dict) and "name" in f]
    if not expected_fields:
        _fail(f"Schema has no fields: {SCHEMA_PATH.relative_to(ROOT)}")

    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)

    missing_cols = [c for c in expected_fields if c not in df.columns]
    extra_cols = [c for c in df.columns if c not in expected_fields]
    if missing_cols or extra_cols:
        _fail(f"CSV columns do not match schema. Missing={missing_cols} Extra={extra_cols}")

    # Keep column order stable
    df = df[expected_fields]

    if any(not str(v).strip() for v in df["frame_id"].tolist()):
        _fail("CSV contains empty frame_id")
    if any(not str(v).strip() for v in df["indicator_id"].tolist()):
        _fail("CSV contains empty indicator_id")
    if any(not str(v).strip() for v in df["template_id"].tolist()):
        _fail("CSV contains empty template_id")

    # Ensure ref_ids is JSON list
    for raw in df["ref_ids"].tolist():
        try:
            parsed = json.loads(raw) if raw else []
        except json.JSONDecodeError as exc:
            _fail(f"ref_ids is not valid JSON: {raw!r} ({exc})")
        if not isinstance(parsed, list):
            _fail(f"ref_ids must decode to list, got {type(parsed).__name__}")

    # Ensure generated date format is yyyy-mm-dd
    bad_dates = [d for d in df["generated"].tolist() if d and not DATE_RE.match(d)]
    if bad_dates:
        _fail(f"generated contains invalid dates: {sorted(set(bad_dates))[:5]}")

    allowed_sections = {"key_learning", "growth", "next_steps"}
    bad_sections = sorted({s for s in df["section"].tolist() if s and s not in allowed_sections})
    if bad_sections:
        _fail(f"section contains invalid values: {bad_sections}")


def _validate_parquet_matches_csv() -> None:
    # Parquet is optional (generate_matrix.py may skip on write failure)
    if not PARQUET_PATH.exists():
        return

    csv_df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
    pq_df = pd.read_parquet(PARQUET_PATH)

    csv_cols = list(csv_df.columns)
    pq_cols = list(pq_df.columns)
    if csv_cols != pq_cols:
        _fail(f"Parquet columns do not match CSV columns.\nCSV: {csv_cols}\nParquet: {pq_cols}")

    if len(csv_df) != len(pq_df):
        _fail(f"Row count mismatch CSV={len(csv_df)} Parquet={len(pq_df)}")


def main() -> int:
    _validate_csv_contract()
    _validate_parquet_matches_csv()
    print("Datasets validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
