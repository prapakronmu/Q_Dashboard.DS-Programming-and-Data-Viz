"""
download.py — Real Open Data Downloader
========================================
Downloads the TMDB 5000 Movies dataset (public/CC0) from GitHub mirrors,
merges with credits for director info, runs the cleaning pipeline,
and saves to data/processed/movies_clean.json

Data Sources:
  - TMDB 5000 Movies : https://github.com/dsrscientist/dataset1
    License: CC0 / Public Domain (originally from Kaggle - The Movies Dataset)
  - TMDB 5000 Credits: same repository
    Attribution: The Movie Database (TMDB) — https://www.themoviedb.org
"""

import ast
import json
import sys
from pathlib import Path

import pandas as pd
import requests

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.pipeline.clean import run_pipeline, save_processed

# ---------------------------------------------------------------------------
# Source URLs (public GitHub mirrors of the TMDB 5000 dataset, CC0)
# ---------------------------------------------------------------------------
MOVIES_URLS = [
    # Verified working mirror (vamshi121/TMDB-5000-Movie-Dataset, CC0)
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/main/tmdb_5000_movies.csv",
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/master/tmdb_5000_movies.csv",
]

# Credits file not available on this mirror — directors will default to "Unknown"
CREDITS_URLS: list[str] = []

RAW_MOVIES_PATH  = Path("data/raw/tmdb_5000_movies.csv")
RAW_CREDITS_PATH = Path("data/raw/tmdb_5000_credits.csv")
PROCESSED_PATH   = Path("data/processed/movies_clean.json")


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def download_file(urls: list[str], dest: Path) -> bool:
    """Try each URL in order; save to dest on first success."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[cache] Using existing {dest}")
        return True
    for url in urls:
        print(f"[download] Trying {url} ...")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            dest.write_bytes(r.content)
            print(f"[download] Saved {len(r.content):,} bytes -> {dest}")
            return True
        except Exception as e:
            print(f"[download] Failed: {e}")
    return False


# ---------------------------------------------------------------------------
# Parse JSON-encoded columns in TMDB CSV
# ---------------------------------------------------------------------------

def _parse_json_col(value, key: str) -> list:
    """Extract a list of 'name' values from a JSON-encoded column."""
    if pd.isna(value) or value in ("", "[]"):
        return []
    try:
        items = ast.literal_eval(value)
        return [item[key] for item in items if key in item]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Extract directors from credits
# ---------------------------------------------------------------------------

def extract_directors(credits_df: pd.DataFrame) -> dict:
    """
    Parse credits CSV and return {movie_id: [director_name, ...]} mapping.
    The crew column contains JSON list with 'job' and 'name' fields.
    """
    director_map = {}
    for _, row in credits_df.iterrows():
        mid = str(row.get("movie_id", row.get("id", "")))
        crew_raw = row.get("crew", "[]")
        try:
            crew = ast.literal_eval(crew_raw)
            directors = [p["name"] for p in crew if p.get("job") == "Director"]
        except Exception:
            directors = []
        director_map[mid] = directors if directors else ["Unknown"]
    return director_map


# ---------------------------------------------------------------------------
# Transform raw TMDB CSV → our schema
# ---------------------------------------------------------------------------

def transform_movies(movies_df: pd.DataFrame, director_map: dict) -> pd.DataFrame:
    """Map TMDB columns to our denormalized schema."""
    df = pd.DataFrame()

    df["movie_id"]  = "tmdb-" + movies_df["id"].astype(str)
    df["title"]     = movies_df["title"].fillna(movies_df.get("original_title", "Unknown"))
    df["release_date"] = movies_df["release_date"]
    df["runtime_minutes"] = pd.to_numeric(movies_df["runtime"], errors="coerce")
    df["budget_usd"]  = pd.to_numeric(movies_df["budget"],  errors="coerce")
    df["revenue_worldwide_usd"] = pd.to_numeric(movies_df["revenue"], errors="coerce")
    df["popularity_score"] = pd.to_numeric(movies_df["popularity"], errors="coerce")
    df["vote_average"]     = pd.to_numeric(movies_df["vote_average"], errors="coerce")
    df["vote_count"]       = pd.to_numeric(movies_df["vote_count"],   errors="coerce").fillna(0).astype(int)

    # Parse genres from JSON column
    df["genres"] = movies_df["genres"].apply(lambda v: _parse_json_col(v, "name"))

    # Parse production countries
    col = "production_countries" if "production_countries" in movies_df.columns else None
    if col:
        df["country_origin"] = movies_df[col].apply(lambda v: _parse_json_col(v, "name"))
    else:
        df["country_origin"] = [[] for _ in range(len(df))]

    # Attach directors from credits
    movie_ids_raw = movies_df["id"].astype(str)
    df["directors"] = movie_ids_raw.apply(
        lambda mid: director_map.get(f"tmdb-{mid}", director_map.get(mid, ["Unknown"]))
    )

    # Required by filter_live_action()
    df["title_type"] = "movie"

    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print(" Live-action Movie Analytics — Data Download & Pipeline")
    print("=" * 60)

    # 1. Download
    ok_movies  = download_file(MOVIES_URLS,  RAW_MOVIES_PATH)
    ok_credits = download_file(CREDITS_URLS, RAW_CREDITS_PATH)

    if not ok_movies:
        print("[ERROR] Could not download movies CSV. Check internet connection.")
        sys.exit(1)

    # 2. Load CSVs
    print(f"\n[load] Reading {RAW_MOVIES_PATH} ...")
    movies_df = pd.read_csv(RAW_MOVIES_PATH, low_memory=False)
    print(f"[load] {len(movies_df):,} movies loaded.")

    director_map = {}
    if ok_credits:
        print(f"[load] Reading {RAW_CREDITS_PATH} ...")
        credits_df = pd.read_csv(RAW_CREDITS_PATH, low_memory=False)
        # credits may use 'movie_id' or 'id' column
        if "movie_id" not in credits_df.columns and "id" in credits_df.columns:
            credits_df = credits_df.rename(columns={"id": "movie_id"})
        director_map = extract_directors(credits_df)
        print(f"[load] Directors extracted for {len(director_map):,} films.")

    # 3. Transform to schema
    print("\n[transform] Mapping to project schema ...")
    df_raw = transform_movies(movies_df, director_map)

    # 4. Run cleaning pipeline
    print("\n[pipeline] Running cleaning pipeline ...")
    df_clean = run_pipeline(df_raw)
    print(f"[pipeline] Clean records: {len(df_clean):,}")
    print(f"[pipeline] With financial data: {df_clean['budget_usd'].notna().sum():,}")
    print(f"[pipeline] Hybrid-flagged: {(df_clean['_live_action_status'] == 'hybrid_flag').sum():,}")

    # 5. Save
    save_processed(df_clean, PROCESSED_PATH)
    print(f"\n[OK] Done. {len(df_clean):,} movies saved to {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
