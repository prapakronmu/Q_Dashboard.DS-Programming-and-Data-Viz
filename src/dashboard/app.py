"""
app.py — Live-action Movie Analytics Dashboard
================================================
Run with:  streamlit run src/dashboard/app.py

Implements all 7 analytical questions from open_data.md with
the financial terminology rules from code_artifact.md:
  ✅ "Revenue – Budget (ส่วนต่างรายได้กับงบผลิต)"
  ✅ "Revenue-to-Budget Ratio"
  ❌ NEVER "Net Profit" or "ROI"
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.pipeline.loader import load_movies, movies_with_financials, movies_with_runtime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FINANCIAL_DISCLAIMER = (
    "⚠️ หมายเหตุ: ตัวเลขรายได้และงบประมาณ อ้างอิงจากชุดข้อมูลดิบเท่านั้น "
    "ไม่รวมต้นทุนทางการตลาด (Marketing / P&A Costs) การจัดจำหน่าย "
    "และส่วนแบ่งโรงภาพยนตร์ จึงไม่ใช่กำไรสุทธิ (Net Profit) ที่แท้จริง"
)
DATA_DISCLAIMER = (
    "📌 ตัวเลขสรุปสถิติทั้งหมดบน Dashboard นี้คือ "
    "\"จำนวนภาพยนตร์ที่รวบรวมได้ภายในชุดข้อมูลนี้เท่านั้น\" "
    "ไม่ใช่จำนวนภาพยนตร์ทั้งหมดที่เคยสร้างมาบนโลก"
)

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🎬 Live-action Movie Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def get_data():
    return load_movies(use_mock_fallback=True)


df_all, is_mock = get_data()


# ---------------------------------------------------------------------------
# Sidebar — Global Filters
# ---------------------------------------------------------------------------
st.sidebar.title("🎛️ Filters")

if is_mock:
    st.sidebar.warning(
        "🔶 **Demo Mode** — Using mock data from spec.\n\n"
        "Run the pipeline with real data to unlock full analytics.",
        icon="🔶",
    )

# Year range
if "release_year" in df_all.columns and df_all["release_year"].notna().any():
    min_year = int(df_all["release_year"].min())
    max_year = int(df_all["release_year"].max())
    year_range = st.sidebar.slider(
        "Release Year", min_value=min_year, max_value=max_year,
        value=(min_year, max_year),
    )
else:
    year_range = (1900, 2030)

# Genre multiselect (array-inclusion, no double-counting of totals)
all_genres = sorted(
    {g for genres in df_all["genres"].dropna() for g in (genres if isinstance(genres, list) else [])}
)
selected_genres = st.sidebar.multiselect(
    "Genre (array-inclusive)", options=all_genres, default=[]
)

# Country filter
all_countries = sorted(
    {c for countries in df_all["country_origin"].dropna()
     for c in (countries if isinstance(countries, list) else [])}
)
selected_countries = st.sidebar.multiselect(
    "Production Country", options=all_countries, default=[]
)

st.sidebar.markdown("---")
st.sidebar.caption(DATA_DISCLAIMER)


# ---------------------------------------------------------------------------
# Apply filters (genre = array inclusion, counts on distinct movie_id)
# ---------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    # Year filter
    if "release_year" in df.columns:
        df = df[
            df["release_year"].between(year_range[0], year_range[1], inclusive="both")
            | df["release_year"].isna()
        ]
    # Genre filter — array inclusion
    if selected_genres:
        df = df[
            df["genres"].apply(
                lambda gs: bool(gs and any(g in gs for g in selected_genres))
                if isinstance(gs, list) else False
            )
        ]
    # Country filter
    if selected_countries:
        df = df[
            df["country_origin"].apply(
                lambda cs: bool(cs and any(c in cs for c in selected_countries))
                if isinstance(cs, list) else False
            )
        ]
    return df


df = apply_filters(df_all)
df_fin = movies_with_financials(df)
df_runtime = movies_with_runtime(df)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎬 Live-action Movie Analytics Dashboard")
st.caption(DATA_DISCLAIMER)
st.markdown("---")


# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🎥 Total Movies", f"{df['movie_id'].nunique():,}")
k2.metric(
    "⭐ Avg Rating",
    f"{df['vote_average'].mean():.2f}" if df["vote_average"].notna().any() else "N/A",
)
k3.metric(
    "💰 Avg Budget (USD)",
    f"\${df_fin['budget_usd'].mean() / 1e6:.1f}M" if not df_fin.empty else "N/A",
)
k4.metric(
    "🌍 Avg Revenue (USD)",
    f"\${df_fin['revenue_worldwide_usd'].mean() / 1e6:.1f}M" if not df_fin.empty else "N/A",
)
k5.metric(
    "📊 Avg Revenue-to-Budget Ratio",
    f"{df_fin['revenue_to_budget_ratio'].mean():.2f}x" if not df_fin.empty else "N/A",
)

st.markdown("---")


# ---------------------------------------------------------------------------
# Row 1 — Budget vs Revenue Scatter  |  Genre Profitability Bar
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Budget vs. Revenue")
    if not df_fin.empty:
        fig_scatter = px.scatter(
            df_fin,
            x="budget_usd",
            y="revenue_worldwide_usd",
            color="revenue_to_budget_ratio",
            hover_name="title",
            hover_data={"budget_usd": ":,.0f", "revenue_worldwide_usd": ":,.0f",
                        "revenue_to_budget_ratio": ":.2f"},
            labels={
                "budget_usd": "Production Budget (USD)",
                "revenue_worldwide_usd": "Worldwide Revenue (USD)",
                "revenue_to_budget_ratio": "Revenue-to-Budget Ratio",
            },
            color_continuous_scale="Viridis",
            title="Budget vs. Worldwide Revenue",
        )
        # Add break-even line (ratio = 1)
        max_val = max(df_fin["budget_usd"].max(), df_fin["revenue_worldwide_usd"].max())
        fig_scatter.add_trace(
            go.Scatter(
                x=[0, max_val], y=[0, max_val],
                mode="lines",
                line=dict(dash="dash", color="red", width=1),
                name="Break-even (1:1)",
            )
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption(FINANCIAL_DISCLAIMER)
    else:
        st.info("No movies with complete budget & revenue data in current filter.")

with col2:
    st.subheader("🎭 Genre Profitability (Revenue-to-Budget Ratio)")
    if not df_fin.empty and "genres" in df_fin.columns:
        # Explode genres for per-genre analysis (distinct movie_id preserved in ratio)
        genre_rows = []
        for _, row in df_fin.iterrows():
            genres = row["genres"] if isinstance(row["genres"], list) else []
            for g in genres:
                genre_rows.append({
                    "genre": g,
                    "revenue_to_budget_ratio": row["revenue_to_budget_ratio"],
                })
        df_genre = pd.DataFrame(genre_rows)
        if not df_genre.empty:
            genre_avg = (
                df_genre.groupby("genre")["revenue_to_budget_ratio"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            fig_genre = px.bar(
                genre_avg,
                x="revenue_to_budget_ratio",
                y="genre",
                orientation="h",
                labels={
                    "revenue_to_budget_ratio": "Avg Revenue-to-Budget Ratio",
                    "genre": "Genre",
                },
                color="revenue_to_budget_ratio",
                color_continuous_scale="Blues",
            )
            fig_genre.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_genre, use_container_width=True)
            st.caption(FINANCIAL_DISCLAIMER)
    else:
        st.info("No financial data available for genre profitability analysis.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Row 2 — Runtime Evolution  |  Release Timing Heatmap
# ---------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("⏱️ Runtime Evolution Over Time")
    if not df_runtime.empty and "release_year" in df_runtime.columns:
        df_rt_yr = (
            df_runtime.dropna(subset=["release_year", "runtime_minutes"])
            .groupby("release_year")["runtime_minutes"]
            .mean()
            .reset_index()
        )
        fig_runtime = px.line(
            df_rt_yr,
            x="release_year",
            y="runtime_minutes",
            labels={"release_year": "Release Year", "runtime_minutes": "Avg Runtime (minutes)"},
            markers=True,
        )
        st.plotly_chart(fig_runtime, use_container_width=True)
    else:
        st.info("No runtime data available for current filter.")

with col4:
    st.subheader("📅 Release Timing vs. Avg Revenue")
    if not df_fin.empty and "release_month" in df_fin.columns:
        monthly = (
            df_fin.groupby("release_month")["revenue_worldwide_usd"]
            .mean()
            .reset_index()
        )
        monthly["month_name"] = monthly["release_month"].map(MONTH_NAMES)
        fig_month = px.bar(
            monthly,
            x="month_name",
            y="revenue_worldwide_usd",
            labels={
                "month_name": "Release Month",
                "revenue_worldwide_usd": "Avg Worldwide Revenue (USD)",
            },
            color="revenue_worldwide_usd",
            color_continuous_scale="Oranges",
        )
        fig_month.update_layout(showlegend=False, xaxis_categoryorder="array",
                                xaxis_categoryarray=list(MONTH_NAMES.values()))
        st.plotly_chart(fig_month, use_container_width=True)
        st.caption(FINANCIAL_DISCLAIMER)
    else:
        st.info("No release date + revenue data for current filter.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Row 3 — Ratings vs Revenue  |  Director Rankings
# ---------------------------------------------------------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("⭐ Ratings vs. Box Office Revenue")
    if not df_fin.empty and "vote_average" in df_fin.columns:
        fig_rating = px.scatter(
            df_fin.dropna(subset=["vote_average"]),
            x="vote_average",
            y="revenue_worldwide_usd",
            hover_name="title",
            labels={
                "vote_average": "Avg Vote Score (0–10)",
                "revenue_worldwide_usd": "Worldwide Revenue (USD)",
            },
            trendline="ols",
            trendline_color_override="red",
        )
        st.plotly_chart(fig_rating, use_container_width=True)
        st.caption(FINANCIAL_DISCLAIMER)
    else:
        st.info("No ratings + revenue data for current filter.")

with col6:
    st.subheader("🎬 Director Rankings by Revenue-to-Budget Ratio")
    if not df_fin.empty and "directors" in df_fin.columns:
        dir_rows = []
        for _, row in df_fin.iterrows():
            directors = row["directors"] if isinstance(row["directors"], list) else [row["directors"]]
            if directors and directors[0] not in (None, "Unknown", np.nan):
                for d in directors:
                    dir_rows.append({
                        "director": d,
                        "revenue_to_budget_ratio": row["revenue_to_budget_ratio"],
                        "title": row["title"],
                    })
        if dir_rows:
            df_dir = pd.DataFrame(dir_rows)
            dir_avg = (
                df_dir.groupby("director")["revenue_to_budget_ratio"]
                .mean()
                .sort_values(ascending=False)
                .head(15)
                .reset_index()
            )
            fig_dir = px.bar(
                dir_avg,
                x="revenue_to_budget_ratio",
                y="director",
                orientation="h",
                labels={
                    "revenue_to_budget_ratio": "Avg Revenue-to-Budget Ratio",
                    "director": "Director",
                },
                color="revenue_to_budget_ratio",
                color_continuous_scale="Greens",
            )
            fig_dir.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_dir, use_container_width=True)
            st.caption(FINANCIAL_DISCLAIMER)
        else:
            st.info("No director data with financial records in current filter.")
    else:
        st.info("No director data available.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Data Table
# ---------------------------------------------------------------------------
st.subheader("📋 Movie Data Table")
display_cols = [
    "movie_id", "title", "release_date", "genres", "runtime_minutes",
    "budget_usd", "revenue_worldwide_usd", "revenue_budget_diff_usd",
    "revenue_to_budget_ratio", "vote_average", "vote_count", "popularity_score",
]
display_cols = [c for c in display_cols if c in df.columns]
st.dataframe(
    df[display_cols].sort_values("vote_count", ascending=False),
    use_container_width=True,
    hide_index=True,
)
st.caption(FINANCIAL_DISCLAIMER)

st.markdown("---")
st.caption(
    "Data sources: TMDB, IMDb, Wikidata, Kaggle — for educational / non-commercial use only. "
    "Multimedia assets (posters, actor images) are NOT redistributed via this dashboard."
)
