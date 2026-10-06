"""
download.py — Real Open Data Downloader & Pipeline Runner
"""

import ast
import json
import sys
from pathlib import Path
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.pipeline.clean import run_pipeline, save_processed

MOVIES_URLS = [
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/main/tmdb_5000_movies.csv",
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/master/tmdb_5000_movies.csv",
]

CREDITS_URLS = [
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/main/tmdb_5000_credits.csv",
    "https://raw.githubusercontent.com/vamshi121/TMDB-5000-Movie-Dataset/master/tmdb_5000_credits.csv",
]

RAW_MOVIES_PATH = Path("data/raw/tmdb_5000_movies.csv")
RAW_CREDITS_PATH = Path("data/raw/tmdb_5000_credits.csv")
PROCESSED_PATH = Path("data/processed/movies_clean.json")

def download_file(urls: list[str], dest: Path) -> bool:
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

def _parse_json_col(value, key: str) -> list:
    if pd.isna(value) or value in ("", "[]"):
        return []
    try:
        items = ast.literal_eval(value)
        return [item[key] for item in items if key in item]
    except Exception:
        return []

def _parse_cast(value) -> list:
    if pd.isna(value) or value in ("", "[]"):
        return []
    try:
        items = ast.literal_eval(value)
        # Extract top 6 cast members with their profile path if available
        cast = []
        for item in items[:6]:
            cast.append({
                "name": item.get("name", "Unknown"),
                "img": "https://image.tmdb.org/t/p/w200" + item.get("profile_path", "") if item.get("profile_path") else "https://ui-avatars.com/api/?name=" + item.get("name", "U")
            })
        return cast
    except Exception:
        return []

def transform_movies(movies_df: pd.DataFrame, credits_df: pd.DataFrame) -> pd.DataFrame:
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
    df["overview"]         = movies_df["overview"].fillna("No overview available.")

    df["genres"] = movies_df["genres"].apply(lambda v: _parse_json_col(v, "name"))
    if "production_countries" in movies_df.columns:
        df["country_origin"] = movies_df["production_countries"].apply(lambda v: _parse_json_col(v, "name"))
    else:
        df["country_origin"] = [[] for _ in range(len(df))]

    # Merge credits
    # Rename movie_id in credits to match id
    credits_df["movie_id"] = "tmdb-" + credits_df["movie_id"].astype(str)
    
    # Map cast
    cast_map = credits_df.set_index("movie_id")["cast"].apply(_parse_cast).to_dict()
    df["cast"] = df["movie_id"].map(cast_map).apply(lambda x: x if isinstance(x, list) else [])

    df["directors"] = [["Unknown"] for _ in range(len(df))]
    df["title_type"] = "movie"

    return df

def main():
    print("=" * 60)
    print(" Live-action Movie Analytics — Data Download")
    print("=" * 60)

    ok = download_file(MOVIES_URLS, RAW_MOVIES_PATH)
    if not ok:
        print("[ERROR] Failed to download movies dataset.")
        sys.exit(1)
        
    ok2 = download_file(CREDITS_URLS, RAW_CREDITS_PATH)
    if not ok2:
        print("[WARN] Failed to download credits dataset. Cast will be empty.")
        credits_df = pd.DataFrame(columns=["movie_id", "cast"])
    else:
        credits_df = pd.read_csv(RAW_CREDITS_PATH, low_memory=False)
        
    movies_df = pd.read_csv(RAW_MOVIES_PATH, low_memory=False)
    
    df_raw = transform_movies(movies_df, credits_df)
    df_clean = run_pipeline(df_raw)
    save_processed(df_clean, PROCESSED_PATH)
    print(f"[OK] Saved {len(df_clean)} movies to {PROCESSED_PATH}")

if __name__ == "__main__":
    main()

