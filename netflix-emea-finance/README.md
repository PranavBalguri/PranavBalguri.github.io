# 🎬 Netflix EMEA Production Finance Analysis

A SQL-driven financial data analysis project exploring vendor spend,
jobs created, and production P&L across EMEA markets — built to
demonstrate strong SQL and data analysis skills.

> Built by Pranav Rao Balguri | [LinkedIn](https://www.linkedin.com/in/pranavraobalguri) | [Portfolio](https://pranavbalguri.github.io)

---

## 🌐 Live Dashboard

👉 **[View the live Streamlit dashboard](https://pranavbalguriappio-netflix-emea-finance.streamlit.app/)**

---

## 💡 Project Philosophy

**SQL does the analysis. Python presents it.**

All business logic lives in SQL - aggregations, window functions,
YoY comparisons, variance analysis, and ranking. Python/Streamlit
purely visualises the SQL results. This mirrors how production
finance reporting works in practice at scale.

---

## 📊 SQL Queries

| Query | Business Question | Key Techniques |
|---|---|---|
| `01_vendor_spend_by_market.sql` | Which markets have highest vendor spend? | CTEs, aggregation, window RANK() |
| `02_yoy_spend_growth.sql` | How does 2025 compare to 2024 per market? | LAG(), YoY variance calculation |
| `03_production_pnl_variance.sql` | Which productions are over/under budget? | CASE statements, RANK() |
| `04_vendor_concentration.sql` | Do we have vendor concentration risk? | Cumulative SUM(), CROSS JOIN |
| `05_jobs_by_market.sql` | What is Netflix's employment impact? | Multi-table JOIN, derived KPIs |
| `06_genre_budget_adherence.sql` | Which genres consistently overspend? | GROUP BY, risk classification |
| `07_spend_category_trends.sql` | Which spend categories are growing? | LAG(), running totals |
| `08_executive_summary.sql` | Single-page stakeholder summary | Composite KPIs, health scoring |

---

## 🔍 Key Insights

**Vendor Spend:**
- UK accounts for 58% of total EMEA vendor spend
- VFX is the largest and fastest growing spend category
- Top 3 vendors represent 58% of total spend — concentration risk flagged

**Jobs Created:**
- Netflix created 17,000+ total jobs across EMEA in 2024–2025
- France is the most cost-efficient market at £19,500 spend per job
- UK generates highest absolute jobs but also highest overspend risk

**Production P&L:**
- 7 of 15 productions exceeded budget
- Sci-Fi and Fantasy genres have 100% over-budget rate due to VFX escalation
- Drama shows strongest budget adherence at 67% on or under budget

---

## 🛠 Tech Stack

| Tool | Role |
|---|---|
| **SQL** | All analysis logic — aggregations, window functions, YoY comparisons |
| **DuckDB** | Runs SQL queries against CSV files locally — no database setup needed |
| **Python / Pandas** | Passes SQL results to visualisation layer |
| **Streamlit** | Interactive dashboard |
| **Plotly** | Charts and visualisations |

---

## 🚀 Run Locally

```bash
# Install dependencies
pip install streamlit pandas plotly duckdb

# Run dashboard
cd dashboard
streamlit run app.py
```

---

## 📁 Project Structure

```
netflix-emea-finance/
├── sql/
│   ├── 01_vendor_spend_by_market.sql
│   ├── 02_yoy_spend_growth.sql
│   ├── 03_production_pnl_variance.sql
│   ├── 04_vendor_concentration.sql
│   ├── 05_jobs_by_market.sql
│   ├── 06_genre_budget_adherence.sql
│   ├── 07_spend_category_trends.sql
│   └── 08_executive_summary.sql
├── data/
│   ├── raw_productions.csv
│   ├── raw_vendors.csv
│   ├── raw_spend.csv
│   └── raw_headcount.csv
├── dashboard/
│   └── app.py
├── requirements.txt
└── README.md
```

---

## 📝 About the Data

All data is synthetic designed to mirror real production finance
reporting structures. Markets covered: UK, Germany, Spain, France,
Italy. Productions are fictional but use realistic budget ranges
and spend patterns for EMEA streaming productions.
