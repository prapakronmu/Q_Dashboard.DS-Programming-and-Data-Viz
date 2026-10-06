# 📋 Project Status — Live-action Movie Analytics Dashboard

> **Last Updated:** 2026-10-06

---

## 🚦 Overall Status: 🟡 In Progress — Phase 5: QA & Pre-launch

```
Phase 1: Project Setup & Data Pipeline   ████████████████████  100% ✅
Phase 2: Data Cleaning & Transformation  ████████████████████  100% ✅
Phase 3: Dashboard — Core Components     ████████████████████  100% ✅
Phase 4: Dashboard — Analytics Views     ████████████████████  100% ✅
Phase 5: QA & Pre-launch Checklist       ░░░░░░░░░░░░░░░░░░░░    0% ⬜
```

---

## 📌 Milestone Tracker

| # | Milestone | Status | Notes |
|:--|:---|:---:|:---|
| 1 | Project Initialization (README + Git commit) | ✅ Done | README synthesized from both spec files |
| 2 | Project scaffold (folder structure, .gitignore, requirements.txt) | ✅ Done | `src/pipeline/`, `src/dashboard/`, `data/` |
| 3 | Data Cleaning Pipeline (`clean.py`) | ✅ Done | Filter, missing values, financial fields |
| 4 | Mock Data Loader (`loader.py`) | ✅ Done | Falls back to spec mock data if no CSV |
| 5 | Dashboard scaffolding + Global Filters | ✅ Done | Year, Genre (array-inclusive), Country |
| 6 | KPI Cards (Total Movies, Avg Rating, Avg Budget, Avg Revenue, Ratio) | ✅ Done | |
| 7 | Budget vs. Revenue Scatter (Q1) | ✅ Done | Break-even line included |
| 8 | Genre Profitability Bar Chart (Q3) | ✅ Done | Array-inclusion; no double counting |
| 9 | Runtime Evolution Line Chart (Q4) | ✅ Done | |
| 10 | Release Timing Bar Chart (Q7) | ✅ Done | |
| 11 | Ratings vs. Revenue Scatter (Q2) | ✅ Done | OLS trendline |
| 12 | Director Rankings Bar Chart (Q6) | ✅ Done | |
| 13 | Data Table with all schema fields | ✅ Done | |
| 14 | Financial Disclaimers on all financial widgets | ✅ Done | Mandatory per spec |
| 15 | QA Checklist & Pre-launch Validation | ⬜ Pending | Run after real data connected |

---

## 🗓️ Phase Details

### ✅ Phase 1 — Project Setup & Data Pipeline

| Task | Status | Details |
|:---|:---:|:---|
| Read and analyze spec documents (`code_artifact.md`, `open_data.md`) | ✅ | Completed |
| Create `README.md` | ✅ | Synthesized from both spec files |
| Create `PROJECT_STATUS.md` | ✅ | This file |
| Initial Git commit | ✅ | `feat: initialize project with README and status file` |
| Set up project folder structure (`src/`, `data/`, `docs/`) | ✅ | Created |
| Set up `.gitignore` | ✅ | Excludes `data/raw/`, `.env`, Python caches |
| Create `requirements.txt` | ✅ | streamlit, pandas, numpy, plotly, python-dotenv |
| Write data ingestion scaffold (`loader.py`) | ✅ | Loads processed JSON; falls back to mock data |

---

### ✅ Phase 2 — Data Cleaning & Transformation

| Task | Status | Details |
|:---|:---:|:---|
| Filter: `Title Type = movie` only | ✅ | `filter_live_action()` in `clean.py` |
| Filter: Exclude pure Animation genre | ✅ | Drops rows where genres = `["Animation"]` only |
| Flag: Hybrid Animation/Live-action titles | ✅ | Tagged `_live_action_status = "hybrid_flag"` |
| Missing value handling — Strings → `"Unknown"` | ✅ | |
| Missing value handling — Drop null `runtime_minutes` rows | ✅ | Flagged with `_runtime_valid` col |
| Missing value handling — Financial fields `null`/`0`/`< 10,000` → `null` | ✅ | |
| Compute `revenue_budget_diff_usd` | ✅ | `revenue_worldwide_usd - budget_usd` |
| Compute `revenue_to_budget_ratio` | ✅ | `revenue_worldwide_usd / budget_usd` |
| Denormalize to JSON document format | ✅ | `save_processed()` |
| Validate schema against `code_artifact.md` spec | ✅ | Smoke test with mock data |
| Output cleaned dataset | ✅ | `data/processed/movies_clean.json` |

---

### ✅ Phase 3 — Dashboard Core Components

| Task | Status | Details |
|:---|:---:|:---|
| Dashboard scaffolding (Streamlit) | ✅ | `src/dashboard/app.py` |
| Global filter bar (Year range, Genre, Country) | ✅ | Genre uses array-inclusion |
| KPI Cards (5 metrics) | ✅ | Total Movies, Avg Rating, Avg Budget, Avg Revenue, Avg Ratio |
| Data table with all fields | ✅ | Sortable, all schema columns |
| Financial disclaimer component | ✅ | Shown on EVERY financial widget |
| Demo-mode warning (mock data) | ✅ | Sidebar warning when no real data |

---

### ✅ Phase 4 — Dashboard Analytics Views

| Task | Status | Details |
|:---|:---:|:---|
| Budget vs. Revenue Scatter Plot (Q1) | ✅ | Break-even line at 1:1 ratio |
| Genre Profitability Bar Chart (Q3) | ✅ | Array-inclusion, no double counting |
| Runtime Evolution Line Chart (Q4) | ✅ | Year-over-year avg runtime |
| Release Timing Bar Chart (Q7) | ✅ | Avg revenue by release month |
| Ratings vs. Revenue Scatter (Q2) | ✅ | OLS trendline |
| Director Rankings Table/Bar (Q6) | ✅ | Top 15 by Revenue-to-Budget Ratio |
| Domestic vs. Foreign Revenue (Q5) | ⬜ | Requires Domestic revenue field (not in current data source) |

---

### ⬜ Phase 5 — QA & Pre-launch

| Checklist Item | Status |
|:---|:---:|
| Animation-only titles fully excluded or flagged | ✅ (pipeline) / ⬜ (need real data) |
| "Total Movies" count ≤ distinct `movie_id` | ✅ (always `nunique()`) |
| No Division-by-Zero from null financial fields | ✅ (guarded in pipeline and charts) |
| No "Net Profit" or "ROI" labels on dashboard | ✅ |
| Financial disclaimer visible on all financial widgets | ✅ |
| End-to-end test with real TMDB/Kaggle data | ⬜ |

---

## 📝 Change Log

| Date | Version | Change |
|:---|:---|:---|
| 2026-10-06 | v0.1.0 | Initial project setup — README and status file created |
| 2026-10-06 | v0.2.0 | Full implementation: pipeline (`clean.py`, `loader.py`) + Streamlit dashboard (`app.py`) with all 6 analytical views, QA disclaimers, and global filters |

---

*This file is updated at each phase milestone.*
