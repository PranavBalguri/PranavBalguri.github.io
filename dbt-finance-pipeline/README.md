# 💰 Financial Reporting Pipeline — dbt + DuckDB

A production-style analytics engineering project modelling financial transactions,
P&L reporting, and fraud risk indicators — built with **dbt Core** and **DuckDB**.

> Built by Pranav Rao Balguri | [LinkedIn](https://www.linkedin.com/in/pranavraobalguri) | [Portfolio](https://pranavbalguri.github.io)

---

## 🏗️ Project Overview

This pipeline transforms raw financial transaction data into clean, reliable
reporting layers used by finance and risk teams.

```
Raw Data (CSV seeds)
    └── Staging Layer       → cleaned, typed, renamed
        └── Intermediate    → business logic, joins
            └── Marts       → final reporting tables (P&L, fraud risk, KPIs)
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

### Step 1 — Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later
3. Install it — **tick "Add Python to PATH"** during install
4. Open Terminal (Mac) or Command Prompt (Windows) and run:
   ```bash
   python --version
   ```
   You should see `Python 3.11.x`

### Step 2 — Install dbt + DuckDB

```bash
pip install dbt-duckdb
```

Verify it worked:
```bash
dbt --version
```

### Step 3 — Clone this project

```bash
git clone https://github.com/PranavBalguri/dbt-finance-pipeline.git
cd dbt-finance-pipeline
```

### Step 4 — Set up your profile

Create a file at `~/.dbt/profiles.yml` with this content:

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
dbt seed

# Run all models
dbt run

# Test data quality
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

Then open http://localhost:8080 to see your full data lineage graph!

---

## 📊 Key Metrics Produced

- **Daily P&L** by business line and product category
- **Month-to-date revenue** vs prior period
- **Fraud risk score** per account (rule-based, based on transaction patterns)
- **Account health indicators** (dormancy, velocity, anomaly flags)

---

## 🧪 Data Quality Tests

- Not null checks on all key fields
- Unique checks on transaction IDs and account IDs  
- Accepted value checks on transaction types and status
- Custom test: no future-dated transactions
- Custom test: fraud score must be between 0 and 100

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| dbt Core | Transformation, testing, documentation |
| DuckDB | Local analytical database (free, no cloud needed) |
| Python | Runtime for dbt |
| SQL | All transformation logic |
| Git | Version control |

---

## 📁 Project Structure

```
dbt_finance_pipeline/
├── models/
│   ├── staging/          # Raw → clean
│   ├── intermediate/     # Business logic
│   └── marts/            # Final reporting tables
├── seeds/                # Source CSV data
├── tests/                # Custom data quality tests
├── macros/               # Reusable SQL macros
├── dbt_project.yml       # Project config
└── README.md
```
