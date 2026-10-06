"""
clean.py — Data Cleaning & Transformation Pipeline
=====================================================
Implements all rules from code_artifact.md:
  - Filter: live-action feature films only (Title Type = movie, not Animation-only)
  - Missing value handling for strings, runtime, and financial fields
  - Compute derived financial fields (revenue_budget_diff_usd, revenue_to_budget_ratio)
  - Output: denormalized JSON documents, one record per movie

CRITICAL RULES (from spec):
  - NEVER label anything as "Net Profit" or "ROI"
  - Financial fields with null/0/<10000 must stay null — excluded from averages & charts
  - Always count distinct movie_id; never count from exploded genre/country rows
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FINANCIAL_MIN_THRESHOLD = 10_000  # Values below this are treated as missing

FINANCIAL_DISCLAIMER = (
    "หมายเหตุ: ตัวเลขรายได้และงบประมาณ อ้างอิงจากชุดข้อมูลดิบเท่านั้น "
    "ไม่รวมต้นทุนทางการตลาด (Marketing / P&A Costs) การจัดจำหน่าย "
    "และส่วนแบ่งโรงภาพยนตร์ จึงไม่ใช่กำไรสุทธิ (Net Profit) ที่แท้จริง"
)


# ---------------------------------------------------------------------------
# Step 1 – Filter: live-action feature films only
# ---------------------------------------------------------------------------

def filter_live_action(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only live-action feature films:
      - title_type == 'movie'
      - genres must NOT be purely ['Animation'] with no human cast flag

    Hybrid Animation+Live-action titles are flagged, not dropped.
    """
    # Filter to movies only (drop TV, shorts, series, etc.)
    if "title_type" in df.columns:
        df = df[df["title_type"] == "movie"].copy()

    # Parse genres if stored as a string representation of a list
    if "genres" in df.columns and df["genres"].dtype == object:
        df["genres"] = df["genres"].apply(_parse_list_field)

    # Flag hybrid titles (Animation + other genres) — keep but mark
    def _classify(genres):
        if not isinstance(genres, list):
            return "unknown"
        genre_set = {g.strip() for g in genres}
        if genre_set == {"Animation"}:
            return "pure_animation"
        if "Animation" in genre_set:
            return "hybrid_flag"  # Needs manual review
        return "live_action"

    df["_live_action_status"] = df["genres"].apply(_classify)

    # Drop pure animation; keep live_action and hybrid (flagged)
    df = df[df["_live_action_status"] != "pure_animation"].copy()
    print(
        f"[filter] Kept {len(df)} rows — "
        f"{(df['_live_action_status'] == 'hybrid_flag').sum()} hybrid-flagged titles"
    )
    return df


# ---------------------------------------------------------------------------
# Step 2 – Missing value handling
# ---------------------------------------------------------------------------

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply missing-value rules from spec:
      - String fields: null → "Unknown"
      - runtime_minutes: drop rows where null (for time-based analysis; set flag col)
      - Financial fields: null / 0 / <10000 → null
    """
    string_cols = ["title", "directors", "country_origin"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # Runtime: flag instead of drop so row is still usable for non-time analysis
    if "runtime_minutes" in df.columns:
        df["runtime_minutes"] = pd.to_numeric(df["runtime_minutes"], errors="coerce")
        df["_runtime_valid"] = df["runtime_minutes"].notna()

    # Financial fields
    for fin_col in ["budget_usd", "revenue_worldwide_usd"]:
        if fin_col in df.columns:
            df[fin_col] = pd.to_numeric(df[fin_col], errors="coerce")
            # Set to null where 0 or below threshold
            df[fin_col] = df[fin_col].where(
                df[fin_col] >= FINANCIAL_MIN_THRESHOLD, other=np.nan
            )

    print("[missing] Missing value handling applied.")
    return df


# ---------------------------------------------------------------------------
# Step 3 – Compute derived financial fields
# ---------------------------------------------------------------------------

def compute_financial_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute:
      - revenue_budget_diff_usd  = revenue_worldwide_usd - budget_usd
      - revenue_to_budget_ratio  = revenue_worldwide_usd / budget_usd

    Only computed when BOTH fields are non-null.
    CRITICAL: Labels use approved terminology — NO "Net Profit" or "ROI".
    """
    has_both = df["budget_usd"].notna() & df["revenue_worldwide_usd"].notna()

    df["revenue_budget_diff_usd"] = np.where(
        has_both,
        df["revenue_worldwide_usd"] - df["budget_usd"],
        np.nan,
    )
    df["revenue_to_budget_ratio"] = np.where(
        has_both & (df["budget_usd"] > 0),
        df["revenue_worldwide_usd"] / df["budget_usd"],
        np.nan,
    )
    print(
        f"[financial] Computed derived fields for "
        f"{has_both.sum()} / {len(df)} records."
    )
    return df


# ---------------------------------------------------------------------------
# Step 4 – Standardize schema & output
# ---------------------------------------------------------------------------

SCHEMA_FIELDS = [
    "movie_id",
    "title",
    "release_date",
    "country_origin",
    "runtime_minutes",
    "genres",
    "directors",
    "budget_usd",
    "revenue_worldwide_usd",
    "revenue_budget_diff_usd",
    "revenue_to_budget_ratio",
    "popularity_score",
    "vote_average",
    "vote_count",
    # Internal flags (not for dashboard display)
    "_live_action_status",
    "_runtime_valid",
]


def standardize_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only schema fields that exist; add missing ones as null."""
    for field in SCHEMA_FIELDS:
        if field not in df.columns:
            df[field] = np.nan if field not in ["genres", "country_origin"] else None

    # Ensure vote_count defaults to 0 (not null)
    if "vote_count" in df.columns:
        df["vote_count"] = df["vote_count"].fillna(0).astype(int)

    return df[SCHEMA_FIELDS]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_list_field(value):
    """Parse a stringified list or comma-separated string into a Python list."""
    if isinstance(value, list):
        return value
    if pd.isna(value) or value == "":
        return []
    if isinstance(value, str):
        # Handle "['Action', 'Adventure']" format
        try:
            parsed = json.loads(value.replace("'", '"'))
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        # Fallback: split by comma
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full cleaning pipeline and return a clean DataFrame."""
    df = filter_live_action(df)
    df = handle_missing_values(df)
    df = compute_financial_fields(df)
    df = standardize_schema(df)
    return df


def save_processed(df: pd.DataFrame, output_path: Path) -> None:
    """Save cleaned DataFrame to JSON (records format)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = df.where(df.notna(), other=None).to_dict(orient="records")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    print(f"[save] Wrote {len(records)} records to {output_path}")


if __name__ == "__main__":
    # Quick smoke test with mock data from code_artifact.md
    mock_data = [
        {
            "movie_id": "tt4154796",
            "title": "Avengers: Endgame",
            "title_type": "movie",
            "release_date": "2019-04-24",
            "country_origin": ["United States"],
            "runtime_minutes": 181,
            "genres": ["Action", "Adventure", "Science Fiction"],
            "directors": ["Anthony Russo", "Joe Russo"],
            "budget_usd": 356_000_000.0,
            "revenue_worldwide_usd": 2_797_800_564.0,
            "popularity_score": 150.43,
            "vote_average": 8.4,
            "vote_count": 23800,
        },
        {
            "movie_id": "tt1160419",
            "title": "Dune",
            "title_type": "movie",
            "release_date": "2021-09-15",
            "country_origin": ["United States", "Canada"],
            "runtime_minutes": 155,
            "genres": ["Science Fiction", "Adventure"],
            "directors": ["Denis Villeneuve"],
            "budget_usd": 165_000_000.0,
            "revenue_worldwide_usd": 402_027_830.0,
            "popularity_score": 112.10,
            "vote_average": 7.8,
            "vote_count": 14500,
        },
        {
            "movie_id": "tt0000001",
            "title": "Indie Unknown Film",
            "title_type": "movie",
            "release_date": "2023-01-10",
            "country_origin": ["Thailand"],
            "runtime_minutes": 90,
            "genres": ["Drama"],
            "directors": None,
            "budget_usd": None,
            "revenue_worldwide_usd": None,
            "popularity_score": 5.2,
            "vote_average": 6.5,
            "vote_count": 15,
        },
    ]

    df_mock = pd.DataFrame(mock_data)
    df_clean = run_pipeline(df_mock)
    print("\n=== Cleaned Data ===")
    print(df_clean.to_string())

    out = Path("data/processed/movies_clean.json")
    save_processed(df_clean, out)
    print(f"\n[OK] Pipeline smoke test passed. Output: {out}")
