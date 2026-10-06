"""
clean.py — Data Cleaning & Transformation Pipeline
=====================================================
Rules:
  - Filter: live-action feature films only (Title Type = movie, not Animation-only)
  - Missing value handling for strings, runtime, and financial fields
  - Compute derived financial fields (revenue_budget_diff_usd, revenue_to_budget_ratio)
  - Output: denormalized JSON documents, one record per movie

CRITICAL RULES:
  - NEVER label anything as "Net Profit" or "ROI"
  - Financial fields with null/0/<10000 must stay null — excluded from averages & charts
  - Guarantee strict JSON serialization (no NaN / Infinity literals)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

FINANCIAL_MIN_THRESHOLD = 10_000

def filter_live_action(df: pd.DataFrame) -> pd.DataFrame:
    if "title_type" in df.columns:
        df = df[df["title_type"] == "movie"].copy()

    if "genres" in df.columns and df["genres"].dtype == object:
        df["genres"] = df["genres"].apply(_parse_list_field)

    def _classify(genres):
        if not isinstance(genres, list):
            return "unknown"
        genre_set = {g.strip() for g in genres}
        if genre_set == {"Animation"}:
            return "pure_animation"
        if "Animation" in genre_set:
            return "hybrid_flag"
        return "live_action"

    df["_live_action_status"] = df["genres"].apply(_classify)
    df = df[df["_live_action_status"] != "pure_animation"].copy()
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    string_cols = ["title", "directors", "country_origin"]
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    if "runtime_minutes" in df.columns:
        df["runtime_minutes"] = pd.to_numeric(df["runtime_minutes"], errors="coerce")

    for fin_col in ["budget_usd", "revenue_worldwide_usd"]:
        if fin_col in df.columns:
            df[fin_col] = pd.to_numeric(df[fin_col], errors="coerce")
            df[fin_col] = df[fin_col].where(df[fin_col] >= FINANCIAL_MIN_THRESHOLD, other=np.nan)

    return df

def compute_financial_fields(df: pd.DataFrame) -> pd.DataFrame:
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
    return df

SCHEMA_FIELDS = [
    "movie_id",
    "title",
    "release_date",
    "country_origin",
    "runtime_minutes",
    "genres",
    "directors",
    "cast",
    "budget_usd",
    "revenue_worldwide_usd",
    "revenue_budget_diff_usd",
    "revenue_to_budget_ratio",
    "popularity_score",
    "vote_average",
    "vote_count",
    "overview",
    "poster_path",
    "backdrop_path"
]

def standardize_schema(df: pd.DataFrame) -> pd.DataFrame:
    for field in SCHEMA_FIELDS:
        if field not in df.columns:
            df[field] = np.nan if field not in ["genres", "country_origin", "cast"] else None

    if "vote_count" in df.columns:
        df["vote_count"] = df["vote_count"].fillna(0).astype(int)

    return df[SCHEMA_FIELDS]

def _parse_list_field(value):
    if isinstance(value, list):
        return value
    if pd.isna(value) or value == "":
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value.replace("'", '"'))
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [v.strip() for v in value.split(",") if v.strip()]
    return []

def run_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    df = filter_live_action(df)
    df = handle_missing_values(df)
    df = compute_financial_fields(df)
    df = standardize_schema(df)
    return df

def save_processed(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_str = df.to_json(orient="records", date_format="iso", force_ascii=False)
    records = json.loads(json_str)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
    print(f"[save] Wrote {len(records)} records to {output_path}")
