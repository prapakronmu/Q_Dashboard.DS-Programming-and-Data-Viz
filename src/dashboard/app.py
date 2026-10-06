"""
app.py — Live-action Movie Analytics Dashboard
================================================
Run with:  streamlit run src/dashboard/app.py

Data: TMDB 5000 Movies Dataset (CC0 Public Domain)
      Source: The Movie Database (TMDB) — https://www.themoviedb.org
      Dataset mirror: github.com/vamshi121/TMDB-5000-Movie-Dataset

Financial terminology rules (code_artifact.md):
  OK : "Revenue – Budget (ส่วนต่างรายได้กับงบผลิต)"
  OK : "Revenue-to-Budget Ratio"
  NO : NEVER "Net Profit" or "ROI"
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.pipeline.loader import load_movies, movies_with_financials, movies_with_runtime

# ---------------------------------------------------------------------------
# Data Source Reference Strings
# ---------------------------------------------------------------------------
SOURCE_TMDB = (
    "📊 **Data source:** TMDB 5000 Movies Dataset · "
    "[The Movie Database (TMDB)](https://www.themoviedb.org) · "
    "License: CC BY-NC 4.0 (attribution required, non-commercial) · "
    "Dataset mirror: [vamshi121/TMDB-5000-Movie-Dataset](https://github.com/vamshi121/TMDB-5000-Movie-Dataset)"
)
SOURCE_TMDB_SHORT = (
    "Source: TMDB 5000 Movies Dataset · themoviedb.org · CC BY-NC 4.0"
)

FINANCIAL_DISCLAIMER = (
    "⚠️ **หมายเหตุ:** ตัวเลขรายได้และงบประมาณอ้างอิงจากชุดข้อมูลดิบเท่านั้น "
    "ไม่รวมต้นทุนทางการตลาด (Marketing / P&A Costs) การจัดจำหน่าย และส่วนแบ่งโรงภาพยนตร์ "
    "จึงไม่ใช่กำไรสุทธิ (Net Profit) ที่แท้จริง"
)

DATA_SCOPE_NOTE = (
    "📌 ตัวเลขสรุปสถิติทั้งหมดบน Dashboard นี้คือ "
    "**\"จำนวนภาพยนตร์ที่รวบรวมได้ภายในชุดข้อมูลนี้เท่านั้น\"** "
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

# Inject minimal CSS for cleaner look
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    [data-testid="metric-container"] { background: rgba(255,255,255,0.04);
        border-radius: 12px; padding: 0.8rem 1rem; border: 1px solid rgba(255,255,255,0.08); }
    .source-box { font-size: 0.72rem; color: #888; margin-top: 2px;
        padding: 4px 8px; border-left: 2px solid #444; }
    .disclaimer-box { font-size: 0.72rem; color: #f0a06a; margin-top: 2px;
        padding: 4px 8px; border-left: 2px solid #f0a06a; }
    h2 { font-size: 1.1rem !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
@st.cache_data
def get_data():
    return load_movies(use_mock_fallback=True)


df_all, is_mock = get_data()

# ---------------------------------------------------------------------------
# Sidebar — Info & Filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🎬 Movie Analytics")

    # Data source info box
    if is_mock:
        st.warning("🔶 **Demo Mode** — Using 3-record mock data.\n\nRun `python src/pipeline/download.py` for real data.", icon="🔶")
    else:
        total = df_all["movie_id"].nunique()
        st.success(f"✅ **Real Data Loaded**\n\n{total:,} movies from TMDB", icon="✅")
        st.caption("Source: TMDB 5000 Movies Dataset\nLicense: CC BY-NC 4.0\nthemoviedb.org")

    st.markdown("---")
    st.subheader("🎛️ Filters")

    # Year range
    if "release_year" in df_all.columns and df_all["release_year"].notna().any():
        min_y = int(df_all["release_year"].min())
        max_y = int(df_all["release_year"].max())
        year_range = st.slider("Release Year", min_value=min_y, max_value=max_y, value=(min_y, max_y))
    else:
        year_range = (1900, 2030)

    # Genre multiselect
    all_genres = sorted({
        g for gs in df_all["genres"].dropna()
        for g in (gs if isinstance(gs, list) else [])
    })
    selected_genres = st.multiselect("Genre (array-inclusive)", options=all_genres, default=[])

    # Country filter
    all_countries = sorted({
        c for cs in df_all["country_origin"].dropna()
        for c in (cs if isinstance(cs, list) else [])
    })
    selected_countries = st.multiselect("Production Country", options=all_countries, default=[])

    st.markdown("---")
    st.caption(DATA_SCOPE_NOTE)


# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if "release_year" in df.columns:
        df = df[df["release_year"].between(*year_range, inclusive="both") | df["release_year"].isna()]
    if selected_genres:
        df = df[df["genres"].apply(
            lambda gs: bool(gs and any(g in gs for g in selected_genres)) if isinstance(gs, list) else False
        )]
    if selected_countries:
        df = df[df["country_origin"].apply(
            lambda cs: bool(cs and any(c in cs for c in selected_countries)) if isinstance(cs, list) else False
        )]
    return df


df       = apply_filters(df_all)
df_fin   = movies_with_financials(df)
df_rt    = movies_with_runtime(df)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🎬 Live-action Movie Analytics Dashboard")
st.caption(DATA_SCOPE_NOTE)
st.markdown(SOURCE_TMDB)
st.markdown("---")


# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🎥 Total Movies",          f"{df['movie_id'].nunique():,}")
k2.metric("⭐ Avg Rating",            f"{df['vote_average'].mean():.2f}" if df["vote_average"].notna().any() else "N/A")
k3.metric("💰 Avg Budget",            f"${df_fin['budget_usd'].mean()/1e6:.0f}M"          if not df_fin.empty else "N/A")
k4.metric("🌍 Avg Worldwide Revenue", f"${df_fin['revenue_worldwide_usd'].mean()/1e6:.0f}M" if not df_fin.empty else "N/A")
k5.metric("📊 Avg Rev/Budget Ratio",  f"{df_fin['revenue_to_budget_ratio'].mean():.2f}x"   if not df_fin.empty else "N/A")

st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · KPI cards computed from {df['movie_id'].nunique():,} distinct movies (distinct movie_id count — no double counting)</div>", unsafe_allow_html=True)
st.markdown("---")


# ---------------------------------------------------------------------------
# Row 1 — Budget vs Revenue Scatter  |  Genre Profitability Bar
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Budget vs. Worldwide Revenue")
    if not df_fin.empty:
        fig = px.scatter(
            df_fin,
            x="budget_usd", y="revenue_worldwide_usd",
            color="revenue_to_budget_ratio",
            hover_name="title",
            hover_data={"budget_usd": ":,.0f", "revenue_worldwide_usd": ":,.0f",
                        "revenue_to_budget_ratio": ":.2f", "release_year": True},
            labels={
                "budget_usd": "Production Budget (USD)",
                "revenue_worldwide_usd": "Worldwide Revenue (USD)",
                "revenue_to_budget_ratio": "Revenue-to-Budget Ratio",
                "release_year": "Year",
            },
            color_continuous_scale="Plasma",
            opacity=0.75,
        )
        mx = max(df_fin["budget_usd"].max(), df_fin["revenue_worldwide_usd"].max())
        fig.add_trace(go.Scatter(
            x=[0, mx], y=[0, mx], mode="lines",
            line=dict(dash="dash", color="rgba(255,100,80,0.7)", width=1.5),
            name="Break-even (1×)", showlegend=True,
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.15),
            coloraxis_colorbar=dict(title="Rev/Budget"),
            margin=dict(t=30, b=10),
        )
        st.plotly_chart(fig, width='stretch')
        st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · n={len(df_fin):,} films with complete budget & revenue data · Red dashed line = break-even (Revenue = Budget)</div>", unsafe_allow_html=True)
    else:
        st.info("No movies with complete financial data in current filter.")

with col2:
    st.subheader("🎭 Genre Profitability (Revenue-to-Budget Ratio)")
    if not df_fin.empty:
        rows = [{"genre": g, "revenue_to_budget_ratio": row["revenue_to_budget_ratio"]}
                for _, row in df_fin.iterrows()
                for g in (row["genres"] if isinstance(row["genres"], list) else [])]
        if rows:
            dg = pd.DataFrame(rows)
            genre_avg = (dg.groupby("genre")["revenue_to_budget_ratio"]
                         .agg(["mean", "count"]).reset_index()
                         .rename(columns={"mean": "avg_ratio", "count": "n_films"})
                         .query("n_films >= 5")
                         .sort_values("avg_ratio", ascending=True))
            fig2 = px.bar(genre_avg, x="avg_ratio", y="genre", orientation="h",
                          hover_data={"n_films": True, "avg_ratio": ":.2f"},
                          labels={"avg_ratio": "Avg Revenue-to-Budget Ratio",
                                  "genre": "Genre", "n_films": "# Films"},
                          color="avg_ratio", color_continuous_scale="Oranges")
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               showlegend=False, margin=dict(t=30, b=10),
                               yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig2, width='stretch')
            st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · Genre filter uses array-inclusion (1 film may appear in multiple genre bars; total count is always distinct movie_id) · Only genres with ≥5 films shown</div>", unsafe_allow_html=True)
    else:
        st.info("No financial data for genre analysis in current filter.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Row 2 — Runtime Trend  |  Release Timing
# ---------------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("⏱️ Average Runtime Over Time")
    if not df_rt.empty and "release_year" in df_rt.columns:
        rt_yr = (df_rt.dropna(subset=["release_year", "runtime_minutes"])
                 .groupby("release_year")["runtime_minutes"]
                 .agg(["mean", "count"]).reset_index()
                 .rename(columns={"mean": "avg_runtime", "count": "n_films"})
                 .query("n_films >= 3"))
        fig3 = px.line(rt_yr, x="release_year", y="avg_runtime", markers=True,
                       hover_data={"n_films": True, "avg_runtime": ":.1f"},
                       labels={"release_year": "Release Year",
                               "avg_runtime": "Avg Runtime (min)",
                               "n_films": "# Films"})
        fig3.update_traces(line_color="#FF6847", marker_color="#FF6847")
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=30, b=10))
        st.plotly_chart(fig3, width='stretch')
        st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · n={len(df_rt):,} films with valid runtime · Only years with ≥3 films shown · Films with null runtime excluded from this chart</div>", unsafe_allow_html=True)
    else:
        st.info("No runtime data in current filter.")

with col4:
    st.subheader("📅 Avg Worldwide Revenue by Release Month")
    if not df_fin.empty and "release_month" in df_fin.columns:
        monthly = (df_fin.dropna(subset=["release_month"])
                   .groupby("release_month")["revenue_worldwide_usd"]
                   .agg(["mean", "count"]).reset_index()
                   .rename(columns={"mean": "avg_revenue", "count": "n_films"}))
        monthly["month_name"] = monthly["release_month"].map(MONTH_NAMES)
        fig4 = px.bar(monthly, x="month_name", y="avg_revenue",
                      hover_data={"n_films": True, "avg_revenue": ":,.0f"},
                      labels={"month_name": "Release Month",
                              "avg_revenue": "Avg Worldwide Revenue (USD)",
                              "n_films": "# Films"},
                      color="avg_revenue", color_continuous_scale="Blues")
        fig4.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           showlegend=False, margin=dict(t=30, b=10),
                           xaxis_categoryorder="array",
                           xaxis_categoryarray=list(MONTH_NAMES.values()))
        st.plotly_chart(fig4, width='stretch')
        st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · n={len(df_fin):,} films with release date + revenue data · Films with null revenue excluded</div>", unsafe_allow_html=True)
    else:
        st.info("No release timing + revenue data in current filter.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Row 3 — Ratings vs Revenue  |  Director Rankings
# ---------------------------------------------------------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("⭐ Vote Score vs. Worldwide Revenue")
    if not df_fin.empty and "vote_average" in df_fin.columns:
        df_rv = df_fin.dropna(subset=["vote_average"])
        fig5 = px.scatter(df_rv, x="vote_average", y="revenue_worldwide_usd",
                          hover_name="title",
                          hover_data={"vote_average": ":.1f",
                                      "revenue_worldwide_usd": ":,.0f",
                                      "vote_count": ":,",
                                      "release_year": True},
                          labels={"vote_average": "Avg Vote Score (0–10)",
                                  "revenue_worldwide_usd": "Worldwide Revenue (USD)",
                                  "vote_count": "# Votes",
                                  "release_year": "Year"},
                          color="vote_count", color_continuous_scale="Viridis",
                          opacity=0.7,
                          trendline="ols", trendline_color_override="#FF6847")
        fig5.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=30, b=10))
        st.plotly_chart(fig5, width='stretch')
        st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · n={len(df_rv):,} · Vote scores from TMDB user ratings · Color = number of votes (darker = more votes) · Red line = OLS trendline</div>", unsafe_allow_html=True)
    else:
        st.info("No ratings + revenue data in current filter.")

with col6:
    st.subheader("🎬 Top Genres by Avg Revenue (Absolute)")
    if not df_fin.empty:
        rows2 = [{"genre": g, "revenue_worldwide_usd": row["revenue_worldwide_usd"]}
                 for _, row in df_fin.iterrows()
                 for g in (row["genres"] if isinstance(row["genres"], list) else [])]
        if rows2:
            dg2 = pd.DataFrame(rows2)
            genre_rev = (dg2.groupby("genre")["revenue_worldwide_usd"]
                         .agg(["mean", "count"]).reset_index()
                         .rename(columns={"mean": "avg_revenue", "count": "n_films"})
                         .query("n_films >= 5")
                         .sort_values("avg_revenue", ascending=True).tail(15))
            fig6 = px.bar(genre_rev, x="avg_revenue", y="genre", orientation="h",
                          hover_data={"n_films": True, "avg_revenue": ":,.0f"},
                          labels={"avg_revenue": "Avg Worldwide Revenue (USD)",
                                  "genre": "Genre", "n_films": "# Films"},
                          color="avg_revenue", color_continuous_scale="Greens")
            fig6.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               showlegend=False, margin=dict(t=30, b=10),
                               yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig6, width='stretch')
            st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · Top 15 genres by average worldwide revenue · Array-inclusive genre attribution · Only genres with ≥5 films shown</div>", unsafe_allow_html=True)
    else:
        st.info("No genre + revenue data in current filter.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Row 4 — Yearly Movie Count  |  Financial Diff Distribution
# ---------------------------------------------------------------------------
col7, col8 = st.columns(2)

with col7:
    st.subheader("📈 Number of Movies Released Per Year")
    if "release_year" in df.columns and df["release_year"].notna().any():
        yearly = (df.dropna(subset=["release_year"])
                  .groupby("release_year")["movie_id"].nunique().reset_index()
                  .rename(columns={"movie_id": "n_films"}))
        fig7 = px.area(yearly, x="release_year", y="n_films",
                       labels={"release_year": "Release Year", "n_films": "# Films (distinct)"},
                       color_discrete_sequence=["#FF6847"])
        fig7.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=30, b=10))
        st.plotly_chart(fig7, width='stretch')
        st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · Count = distinct movie_id per year · Dataset coverage is strongest for 1990–2016</div>", unsafe_allow_html=True)
    else:
        st.info("No release year data available.")

with col8:
    st.subheader("💹 Distribution of Revenue – Budget (ส่วนต่างรายได้กับงบผลิต)")
    if not df_fin.empty and df_fin["revenue_budget_diff_usd"].notna().any():
        df_diff = df_fin.dropna(subset=["revenue_budget_diff_usd"])
        fig8 = px.histogram(df_diff, x="revenue_budget_diff_usd", nbins=60,
                            labels={"revenue_budget_diff_usd": "Revenue – Budget (USD)"},
                            color_discrete_sequence=["#5B9BD5"])
        fig8.add_vline(x=0, line_dash="dash", line_color="red",
                       annotation_text="Break-even", annotation_position="top right")
        fig8.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=30, b=10))
        st.plotly_chart(fig8, width='stretch')
        pct_positive = (df_diff["revenue_budget_diff_usd"] > 0).mean() * 100
        st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · n={len(df_diff):,} films with complete budget & revenue · {pct_positive:.1f}% of films have positive Revenue – Budget · Red line = break-even (diff = 0)</div>", unsafe_allow_html=True)
    else:
        st.info("No financial data for distribution chart.")

st.markdown("---")


# ---------------------------------------------------------------------------
# Data Table
# ---------------------------------------------------------------------------
st.subheader("📋 Full Dataset Table")
display_cols = [c for c in [
    "title", "release_date", "genres", "runtime_minutes", "country_origin",
    "budget_usd", "revenue_worldwide_usd", "revenue_budget_diff_usd",
    "revenue_to_budget_ratio", "vote_average", "vote_count", "popularity_score",
] if c in df.columns]

st.dataframe(
    df[display_cols].sort_values("vote_count", ascending=False),
    width='stretch', hide_index=True,
)
st.markdown(f"<div class='disclaimer-box'>{FINANCIAL_DISCLAIMER}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='source-box'>{SOURCE_TMDB_SHORT} · Showing {df['movie_id'].nunique():,} distinct films after applying current filters</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
**📚 Data Sources & Licenses**

| Source | Variables | License | Link |
|:---|:---|:---|:---|
| **TMDB 5000 Movies Dataset** | Title, date, genres, budget, revenue, ratings, runtime, popularity, production countries | CC BY-NC 4.0 (attribution required, non-commercial) | [themoviedb.org](https://www.themoviedb.org) · [Dataset](https://github.com/vamshi121/TMDB-5000-Movie-Dataset) |
| **IMDb Non-Commercial Datasets** | Ratings cross-reference | Non-commercial use only | [developer.imdb.com](https://developer.imdb.com/non-commercial-datasets/) |
| **Wikidata** | Awards, cross-IDs | CC0 1.0 (Public Domain) | [query.wikidata.org](https://query.wikidata.org/) |

> ⚠️ **สิทธิ์การใช้งาน:** ข้อมูลสถิติ (Text/Numbers) ใช้งานได้ในระดับ Open Data / Fair Use เพื่อการศึกษา
> ภาพประกอบ (โปสเตอร์/นักแสดง) มีลิขสิทธิ์คุ้มครอง **ไม่ได้แจกจ่ายผ่าน Dashboard นี้**

*Dashboard built for educational purposes only · Not affiliated with TMDB or IMDb*
""")
