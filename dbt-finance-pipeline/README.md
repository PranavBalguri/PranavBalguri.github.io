# 💰 Financial Reporting Pipeline — dbt + DuckDB + Streamlit

A production-style analytics engineering project modelling financial transactions,
P&L reporting, and fraud risk indicators. Built with **dbt Core**, **DuckDB**, and **Streamlit**.

---

## 🌐 Live Dashboard

👉 **[View the live Streamlit dashboard here](https://pranavbalguri-pranavbalgur-dbt-finance-pipelinedashboard-hgrdij.streamlit.app/)**

No setup needed, just open the link and explore the data directly in your browser.

---

## 🏗️ Project Overview

This project has two layers:

| Layer | Tool | Purpose |
|---|---|---|
| **Data Pipeline** | dbt Core + DuckDB | Transforms raw CSV data into clean reporting marts locally |
| **Dashboard** | Streamlit + Plotly | Visualises the pipeline outputs which are deployed on Streamlit Cloud |

```
Raw Data (CSV seeds)
    └── Staging Layer       → cleaned, typed, renamed
        └── Intermediate    → business logic, joins
            └── Marts       → P&L, fraud risk, accounts
                └── Streamlit Dashboard → live at streamlit.app
```

### Models Built

| Layer | Model | Description |
|---|---|---|
| Staging | `stg_transactions` | Cleaned raw transactions |
| Staging | `stg_accounts` | Cleaned account master data |
| Intermediate | `int_transactions_enriched` | Transactions joined with account info |
| Mart | `fct_daily_pnl` | Daily P&L by business line |
| Mart | `fct_fraud_indicators` | Fraud risk scoring per account |
| Mart | `dim_accounts` | Account dimension table |

---

## 📊 Dashboard Features

The Streamlit dashboard (`dashboard.py`) is deployed on Streamlit Cloud and
works without any local setup. It mirrors the logic from the dbt marts exactly.

| Tab | What it shows |
|---|---|
| 📈 P&L Analysis | Daily revenue by business line, inflow/outflow chart, full P&L table |
| 🚨 Fraud Risk | Risk score bar chart, colour-coded account risk table |
| 👤 Accounts | Account age vs volume scatter, engagement tier breakdown |
| 📋 Raw Transactions | Filterable transaction table by status, business line, direction |

---

## 🖥️ Run the dbt Pipeline Locally

Want to run the full pipeline with the lineage graph? Follow these steps.

### Step 1 — Install Python 3.11

Download from:
```
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
```

> ⚠️ Use Python 3.11 — dbt is not yet compatible with Python 3.13+

During install — tick ✅ **"Add Python to PATH"**

### Step 2 — Install dbt + DuckDB

```bash
pip install dbt-core dbt-duckdb
```

Verify:
```bash
dbt --version
```

### Step 3 — Clone this repo

```bash
git clone https://github.com/PranavBalguri/PranavBalguri.github.io.git
cd PranavBalguri.github.io/dbt-finance-pipeline
```

### Step 4 — Set up your dbt profile

Create a file at `~/.dbt/profiles.yml`:

```yaml
dbt_finance_pipeline:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ./finance.duckdb
```

### Step 5 — Run the pipeline

```bash
# Load seed data
dbt seed --profiles-dir .

# Build all models
dbt run --profiles-dir .

# Run 20 data quality tests
dbt test --profiles-dir .
```

### Step 6 — View the lineage graph

```bash
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

Open **http://localhost:8080** to see the full data lineage graph.

---

## 🧪 Data Quality Tests (20 passing)

- Unique and not null checks on all key fields
- Accepted value checks on transaction types and statuses
- Custom test: fraud score must always be between 0 and 100

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| dbt Core | Transformation, testing, documentation |
| DuckDB | Local analytical database (free, no cloud needed) |
| Streamlit | Interactive dashboard — deployed on Streamlit Cloud |
| Plotly | Charts and visualisations |
| Python | Runtime for dbt and Streamlit |
| SQL | All transformation logic |
| Git + GitHub | Version control and hosting |

---

## 📁 Project Structure

```
dbt-finance-pipeline/
├── models/
│   ├── staging/               # Raw → clean
│   ├── intermediate/          # Business logic + joins
│   └── marts/                 # Final reporting tables
├── seeds/                     # Source CSV data
├── tests/                     # Custom data quality tests
├── macros/                    # Reusable SQL macros
├── dashboard.py               # Streamlit dashboard (Streamlit Cloud)
├── requirements.txt           # Streamlit Cloud dependencies
├── dbt_project.yml            # dbt config
└── README.md
```

---

## 💡 Design Decisions

**Why DuckDB locally but not in the dashboard?**

DuckDB is perfect for running dbt pipelines locally as it's fast, free, and
requires no setup. However, Streamlit Cloud doesn't persist files between
sessions, so the dashboard replicates the mart logic directly in Python/Pandas.
This mirrors a real-world pattern where a data pipeline runs on a schedule and
a separate BI layer reads from it.

**Why rule-based fraud scoring?**

The fraud scoring model is intentionally rule-based to reflect how fraud teams
actually work in insurance and banking as explainable rules that compliance teams
can audit, rather than a black-box ML model.
