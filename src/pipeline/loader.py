"""
loader.py — Data Loader for Dashboard
=======================================
Loads the cleaned movie dataset.
Falls back to embedded mock data (from code_artifact.md) if no processed file exists.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

PROCESSED_DATA_PATH = Path("data/processed/movies_clean.json")

# ---------------------------------------------------------------------------
# Mock data (from code_artifact.md § 4 — always available as fallback)
# ---------------------------------------------------------------------------
MOCK_RECORDS = [
    {
        "movie_id": "tt4154796",
        "title": "Avengers: Endgame",
        "release_date": "2019-04-24",
        "country_origin": ["United States"],
        "runtime_minutes": 181,
        "genres": ["Action", "Adventure", "Science Fiction"],
        "directors": ["Anthony Russo", "Joe Russo"],
        "budget_usd": 356_000_000.0,
        "revenue_worldwide_usd": 2_797_800_564.0,
        "revenue_budget_diff_usd": 2_441_800_564.0,
        "revenue_to_budget_ratio": 7.86,
        "popularity_score": 150.43,
        "vote_average": 8.4,
        "vote_count": 23800,
        "_live_action_status": "live_action",
        "_runtime_valid": True,
    },
    {
        "movie_id": "tt1160419",
        "title": "Dune",
        "release_date": "2021-09-15",
        "country_origin": ["United States", "Canada"],
        "runtime_minutes": 155,
        "genres": ["Science Fiction", "Adventure"],
        "directors": ["Denis Villeneuve"],
        "budget_usd": 165_000_000.0,
        "revenue_worldwide_usd": 402_027_830.0,
        "revenue_budget_diff_usd": 237_027_830.0,
        "revenue_to_budget_ratio": 2.43,
        "popularity_score": 112.10,
        "vote_average": 7.8,
        "vote_count": 14500,
        "_live_action_status": "live_action",
        "_runtime_valid": True,
    },
    {
        "movie_id": "tt0000001",
        "title": "Indie Unknown Film",
        "release_date": "2023-01-10",
        "country_origin": ["Thailand"],
        "runtime_minutes": 90,
        "genres": ["Drama"],
        "directors": ["Unknown"],
        "budget_usd": None,
        "revenue_worldwide_usd": None,
        "revenue_budget_diff_usd": None,
        "revenue_to_budget_ratio": None,
        "popularity_score": 5.2,
        "vote_average": 6.5,
        "vote_count": 15,
        "_live_action_status": "live_action",
        "_runtime_valid": True,
    },
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_movies(use_mock_fallback: bool = True) -> tuple[pd.DataFrame, bool]:
    """
    Load the cleaned movie dataset.

    Returns:
        (df, is_mock) where is_mock=True when using embedded mock data.
    """
    if PROCESSED_DATA_PATH.exists():
        with open(PROCESSED_DATA_PATH, encoding="utf-8") as f:
            records = json.load(f)
        df = pd.DataFrame(records)
        return _post_process(df), False

    if use_mock_fallback:
        df = pd.DataFrame(MOCK_RECORDS)
        return _post_process(df), True

    raise FileNotFoundError(
        f"No processed data found at {PROCESSED_DATA_PATH}. "
        "Run the pipeline first: python src/pipeline/clean.py"
    )


def _post_process(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure correct dtypes after loading."""
    # Parse dates
    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
        df["release_year"] = df["release_date"].dt.year
        df["release_month"] = df["release_date"].dt.month

    # Numeric coercions
    for col in ["budget_usd", "revenue_worldwide_usd",
                "revenue_budget_diff_usd", "revenue_to_budget_ratio",
                "popularity_score", "vote_average"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "vote_count" in df.columns:
        df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0).astype(int)

    if "runtime_minutes" in df.columns:
        df["runtime_minutes"] = pd.to_numeric(df["runtime_minutes"], errors="coerce")

    return df


def movies_with_financials(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where both budget and revenue are non-null (for financial charts)."""
    return df[df["budget_usd"].notna() & df["revenue_worldwide_usd"].notna()].copy()


def movies_with_runtime(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where runtime is valid (for time-analysis charts)."""
    return df[df["runtime_minutes"].notna()].copy()
