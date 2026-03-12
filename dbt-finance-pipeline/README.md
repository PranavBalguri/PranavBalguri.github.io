# 💰 Financial Reporting Pipeline — dbt + DuckDB + Streamlit

A production-style analytics engineering project modelling financial transactions,
P&L reporting, and fraud risk indicators — built with **dbt Core**, **DuckDB**, and **Streamlit**.

---

## 🏗️ Project Overview

This pipeline transforms raw financial transaction data into clean, reliable
reporting layers used by finance and risk teams — with an interactive Streamlit
dashboard to visualise the results.

```
Raw Data (CSV seeds)
    └── Staging Layer       → cleaned, typed, renamed
        └── Intermediate    → business logic, joins
            └── Marts       → final reporting tables (P&L, fraud risk, KPIs)
                └── Dashboard (Streamlit) → interactive visualisations
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

## 🚀 Setup Instructions (From Zero)

### Step 1 — Install Python 3.11

1. Go to https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe (Windows)
2. Run the installer — **tick "Add Python to PATH"** before clicking Install
3. Verify:
```bash
python --version
```

> ⚠️ Use Python 3.11 — dbt is not yet compatible with Python 3.13+

### Step 2 — Install dependencies

```bash
pip install dbt-core dbt-duckdb streamlit plotly pandas
```

### Step 3 — Clone this project

```bash
git clone https://github.com/PranavBalguri/PranavBalguri.github.io.git
cd PranavBalguri.github.io/dbt-finance-pipeline
```

### Step 4 — Set up your dbt profile

Create `~/.dbt/profiles.yml`:

```yaml
dbt_finance_pipeline:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ./finance.duckdb
```

### Step 5 — Run the dbt pipeline

```bash
# Load seed data
dbt seed --profiles-dir .

# Run all models
dbt run --profiles-dir .

# Run data quality tests
dbt test --profiles-dir .

# View lineage graph
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

Open http://localhost:8080 to see your full data lineage graph!

### Step 6 — Launch the Streamlit dashboard

```bash
streamlit run dashboard.py
```

Open http://localhost:8501 to see the interactive dashboard!

---

## 📊 Dashboard Features

The Streamlit dashboard (`dashboard.py`) reads directly from the live DuckDB
database and provides 4 interactive tabs:

| Tab | What it shows |
|---|---|
| 📈 P&L Analysis | Daily revenue by business line, inflow/outflow donut chart, full P&L table |
| 🚨 Fraud Risk | Risk score bar chart, colour-coded account risk table, HIGH/MEDIUM/LOW summary |
| 👤 Accounts | Scatter plot of account age vs volume, engagement tier breakdown |
| 📋 Raw Transactions | Filterable transaction table by status, business line, and direction |

### Key Metrics

- **Total volume** — sum of all transaction values
- **Estimated revenue** — fee/interest model per business line
- **Fraud risk scores** — rule-based 0–100 scoring per account
- **Month-to-date P&L** — cumulative revenue using window functions

---

## 🧪 Data Quality Tests (20 passing)

- Not null checks on all key fields
- Unique checks on transaction IDs and account IDs
- Accepted value checks on transaction types and status
- Custom test: fraud score must be between 0 and 100

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| dbt Core | Transformation, testing, documentation |
| DuckDB | Local analytical database (free, no cloud needed) |
| Streamlit | Interactive dashboard |
| Plotly | Charts and visualisations |
| Python | Runtime |
| SQL | All transformation logic |
| Git | Version control |

---

## 📁 Project Structure

```
dbt-finance-pipeline/
├── models/
│   ├── staging/          # Raw → clean
│   ├── intermediate/     # Business logic
│   └── marts/            # Final reporting tables
├── seeds/                # Source CSV data
├── tests/                # Custom data quality tests
├── macros/               # Reusable SQL macros
├── dashboard.py          # Streamlit dashboard
├── requirements.txt      # Python dependencies
├── dbt_project.yml       # dbt config
└── README.md
```
