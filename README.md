# 🎬 Live-action Movie Analytics Dashboard

> **Interactive analytics dashboard for live-action feature films**, powered by open data sources. Explore budget vs. revenue, genre trends, ratings, and more.

---

## 📌 Project Overview

This project builds an **interactive, browser-based analytics dashboard** focused exclusively on **live-action feature films** — including photorealistic CGI titles classified as live-action by the industry (e.g., *The Lion King* (2019)). It is designed for educational and non-commercial use.

> ⚠️ **Data Disclaimer:** All statistics displayed on this dashboard represent only the movies collected within this dataset. The figures do **not** represent the complete history of cinema worldwide.

---

## 🗂️ Data Scope & Filtering Rules

| Rule | Description |
|:---|:---|
| ✅ Include | Live-action Feature Films (human cast or photorealistic CGI) |
| ✅ Include | Streaming feature films (`Title Type = movie`) |
| ❌ Exclude | TV Series, Mini-series, Short Films |
| ❌ Exclude | Pure Animation (genres tagged `Animation` only, with no human cast) |
| ⚠️ Flag | Hybrid Animation/Live-action titles — require manual review or keyword-based profiling |

---

## 📊 Data Schema

Each record is stored as a **denormalized JSON document** (1 document = 1 movie):

| Field | Type | Nullable | Description |
|:---|:---|:---|:---|
| `movie_id` | String | NOT NULL | Primary Key (TMDB ID or IMDb ID) |
| `title` | String | NOT NULL | International/English title |
| `release_date` | Date (YYYY-MM-DD) | NULL | Official release date |
| `country_origin` | Array[String] | NULL | Production country (first 1–2 only) |
| `runtime_minutes` | Integer | NULL | Film duration in minutes |
| `genres` | Array[String] | NOT NULL | Multi-value genre tags |
| `directors` | Array[String] | NULL | Director name(s) |
| `budget_usd` | Float | NULL | Production budget (USD) |
| `revenue_worldwide_usd` | Float | NULL | Worldwide gross revenue (USD) |
| `revenue_budget_diff_usd` | Float | NULL | Revenue minus Budget (USD) |
| `revenue_to_budget_ratio` | Float | NULL | Revenue ÷ Budget |
| `popularity_score` | Float | NULL | Popularity score from source database |
| `vote_average` | Float | NULL | Average audience/critic score (0.0–10.0) |
| `vote_count` | Integer | NOT NULL | Number of votes (default: 0) |

---

## 🔧 Data Cleaning Rules

### Missing Value Handling
- **String fields:** `null` → `"Unknown"`
- **Runtime:** Drop rows where `runtime_minutes` is `null` from time-based analysis
- **Financial fields:** Values that are `null`, `0`, or `< 10,000` → set to `null`; **never use in financial averages or charts**

### Multi-value Fields (Genres & Countries)
- **Total movie counts:** Always count **distinct `movie_id`** — never from exploded/unnested rows
- **Genre filtering:** Use array inclusion check (e.g., `genres.includes("Action")`) — a single film can appear in multiple genre bars without distorting totals

### ⚠️ Critical Financial Terminology
> **NEVER use "Net Profit" or "ROI"** — these imply costs (marketing, distribution, exhibitor splits) that are not in the raw dataset.

| Allowed Term | Formula |
|:---|:---|
| **Revenue – Budget (ส่วนต่างรายได้กับงบผลิต)** | `revenue_worldwide_usd - budget_usd` |
| **Revenue-to-Budget Ratio** | `revenue_worldwide_usd / budget_usd` |

Every financial widget **must** display this disclaimer:
> *"หมายเหตุ: ตัวเลขรายได้และงบประมาณ อ้างอิงจากชุดข้อมูลดิบเท่านั้น ไม่รวมต้นทุนทางการตลาด (Marketing / P&A Costs) การจัดจำหน่าย และส่วนแบ่งโรงภาพยนตร์ จึงไม่ใช่กำไรสุทธิ (Net Profit) ที่แท้จริง"*

---

## 🌐 Open Data Sources

| Source | Key Variables | License | Limitations |
|:---|:---|:---|:---|
| **[TMDB API & Daily Exports](https://developer.themoviedb.org/docs)** | Title, date, country, language, runtime, genres, studio, director, cast, budget, revenue, vote scores, TMDB ID, IMDb ID | CC BY-NC 4.0 (attribution required, no commercial use) | Budget/revenue often null for indie/non-mainstream films |
| **[IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)** | Title, year, runtime, genres, director, writer, IMDb rating, vote count, IMDb ID | Proprietary / Non-Commercial Use Only | No budget or revenue data; large TSV files |
| **[Wikidata SPARQL](https://query.wikidata.org/)** | Awards, studios, distributors, country of origin, cross-ID links | CC0 1.0 (Public Domain) | Incomplete for non-mainstream films |
| **[The Movies Dataset (Kaggle)](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)** | ~45,000 films, pre-cleaned TMDB-based data | CC0: Public Domain | Data stops at 2017 — misses post-COVID era films |

> ⚠️ **Licensing Note:** Dataset statistics (text/numbers) may be used under Open Data / Fair Use for education. **Multimedia assets (posters, actor images) are copyrighted and must NOT be redistributed via the dashboard.**

---

## 🔍 Analytical Questions

1. **Budget vs. Revenue:** What is the relationship between production budget and worldwide revenue? What is the average break-even threshold (revenue-to-budget ratio)?
2. **Ratings vs. Box Office:** Does a higher average vote score correlate with higher revenue?
3. **Genre Profitability:** Which live-action genres have the highest average Revenue-to-Budget Ratio over the last 20 years?
4. **Runtime Evolution:** Has average film runtime changed over time? Does runtime correlate with popularity?
5. **Domestic vs. Foreign Revenue:** How do revenue splits differ between production regions (e.g., US vs. Asia)?
6. **Director & Cast Impact:** Which directors or lead actors consistently produce films with the highest Revenue-to-Budget Ratio?
7. **Release Timing:** Which release months or seasons generate the highest average revenue for live-action films?

---

## 🏗️ Multi-genre & Multi-country Counting Strategies

To avoid **double-counting**, three strategies are available:

| Strategy | Best For | Trade-off |
|:---|:---|:---|
| **Bridge Table** (Fact-Dimension schema) | Relational DB backends | Requires JOIN logic |
| **Primary Key Extraction** (`genres[0]`, `countries[0]`) | High-level macro views | Loses secondary genre signal |
| **Fractional Counting** (weight = 1/N genres) | Budget/revenue aggregation by genre | Sum across genres equals true total |

---

## ✅ Pre-launch QA Checklist

- [ ] **Filter Check:** `Animation`-only titles fully excluded (or flagged as Live-action Hybrid)
- [ ] **Aggregate Check:** "Total Movies" KPI card ≤ distinct `movie_id` count (no double counting)
- [ ] **Financial Filter Check:** Films with `null` budget/revenue excluded from financial averages; no Division-by-Zero errors
- [ ] **Terminology Check:** No "Net Profit" or "ROI" labels anywhere on the dashboard
- [ ] **Disclaimer Check:** Financial disclaimer visible on all budget/revenue widgets

---

## 📁 Project Structure

```
Q_Dashboard.DS-Programming-and-Data-Viz/
├── README.md               # This file
├── code_artifact.md        # Data schema & transformation spec
├── open_data.md            # Open data sources & analytical questions
├── data/                   # Raw and processed datasets (gitignored)
├── src/                    # Source code
│   ├── pipeline/           # Data ingestion & cleaning scripts
│   └── dashboard/          # Frontend dashboard application
└── docs/                   # Additional documentation
```

---

## 📋 Project Status

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for live implementation progress.

---

*Built for educational purposes. Data sourced from TMDB, IMDb, Wikidata, and Kaggle under their respective non-commercial licenses.*
