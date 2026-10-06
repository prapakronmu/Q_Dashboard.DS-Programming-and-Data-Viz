# 📋 Project Status — Live-action Movie Analytics Dashboard

> **Last Updated:** 2026-10-06

---

## 🚦 Overall Status: 🟡 In Progress — Phase 1: Setup & Data Pipeline

```
Phase 1: Project Setup & Data Pipeline   ████░░░░░░░░░░░░░░░░  20%
Phase 2: Data Cleaning & Transformation  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3: Dashboard — Core Components     ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4: Dashboard — Analytics Views     ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5: QA & Pre-launch Checklist       ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## 📌 Milestone Tracker

| # | Milestone | Status | Notes |
|:--|:---|:---:|:---|
| 1 | Project Initialization (README + Git commit) | ✅ Done | README created from spec documents |
| 2 | Data Source Integration (TMDB API / IMDb / Kaggle) | ⬜ Pending | |
| 3 | Data Cleaning Pipeline | ⬜ Pending | |
| 4 | Mock Data & Schema Validation | ⬜ Pending | |
| 5 | Dashboard — KPI Cards | ⬜ Pending | |
| 6 | Dashboard — Genre Analysis Chart | ⬜ Pending | |
| 7 | Dashboard — Budget vs. Revenue Scatter | ⬜ Pending | |
| 8 | Dashboard — Runtime Trend Line | ⬜ Pending | |
| 9 | Dashboard — Release Timing Heatmap | ⬜ Pending | |
| 10 | Dashboard — Director / Cast Rankings | ⬜ Pending | |
| 11 | Financial Disclaimers on all widgets | ⬜ Pending | |
| 12 | QA Checklist & Pre-launch Validation | ⬜ Pending | |

---

## 🗓️ Phase Details

### ✅ Phase 1 — Project Setup & Data Pipeline

| Task | Status | Details |
|:---|:---:|:---|
| Read and analyze spec documents (`code_artifact.md`, `open_data.md`) | ✅ | Completed |
| Create `README.md` | ✅ | Synthesized from both spec files |
| Create `PROJECT_STATUS.md` | ✅ | This file |
| Initial Git commit | ✅ | `feat: initialize project with README and status file` |
| Set up project folder structure (`src/`, `data/`, `docs/`) | ⬜ | |
| Set up `.gitignore` (exclude `data/raw/`) | ⬜ | |
| Configure TMDB API key handling | ⬜ | |
| Write data ingestion script — TMDB Daily Exports | ⬜ | |
| Write data ingestion script — IMDb TSV datasets | ⬜ | |
| Join / merge TMDB + IMDb on shared ID | ⬜ | |

---

### ⬜ Phase 2 — Data Cleaning & Transformation

| Task | Status | Details |
|:---|:---:|:---|
| Filter: `Title Type = movie` only | ⬜ | |
| Filter: Exclude pure Animation genre | ⬜ | |
| Flag: Hybrid Animation/Live-action titles | ⬜ | |
| Missing value handling — Strings → `"Unknown"` | ⬜ | |
| Missing value handling — Drop null `runtime_minutes` rows | ⬜ | |
| Missing value handling — Financial fields `null`/`0`/`< 10,000` → `null` | ⬜ | |
| Compute `revenue_budget_diff_usd` | ⬜ | |
| Compute `revenue_to_budget_ratio` | ⬜ | |
| Denormalize to JSON document format | ⬜ | |
| Validate schema against `code_artifact.md` spec | ⬜ | |
| Output cleaned dataset | ⬜ | |

---

### ⬜ Phase 3 — Dashboard Core Components

| Task | Status | Details |
|:---|:---:|:---|
| Dashboard scaffolding & tooling setup | ⬜ | |
| Global filter bar (Year range, Genre, Country) | ⬜ | |
| KPI Cards (Total Movies, Avg Rating, Avg Budget, Avg Revenue) | ⬜ | |
| Data table with all fields | ⬜ | |
| Financial disclaimer component | ⬜ | Mandatory on every financial widget |

---

### ⬜ Phase 4 — Dashboard Analytics Views

| Task | Status | Details |
|:---|:---:|:---|
| Budget vs. Revenue Scatter Plot | ⬜ | Use `revenue_to_budget_ratio` |
| Genre Profitability Bar Chart | ⬜ | Array-inclusion filter; no double counting |
| Runtime Evolution Line Chart | ⬜ | Year-over-year average runtime trend |
| Release Timing Heatmap (Month × Year) | ⬜ | |
| Director / Cast Rankings Table | ⬜ | Ranked by Revenue-to-Budget Ratio |
| Domestic vs. Foreign Revenue (if data available) | ⬜ | |

---

### ⬜ Phase 5 — QA & Pre-launch

| Checklist Item | Status |
|:---|:---:|
| Animation-only titles fully excluded or flagged | ⬜ |
| "Total Movies" count ≤ distinct `movie_id` | ⬜ |
| No Division-by-Zero from null financial fields | ⬜ |
| No "Net Profit" or "ROI" labels on dashboard | ⬜ |
| Financial disclaimer visible on all financial widgets | ⬜ |

---

## 📝 Change Log

| Date | Version | Change |
|:---|:---|:---|
| 2026-10-06 | v0.1.0 | Initial project setup — README and status file created |

---

*This file is updated at each phase milestone.*
