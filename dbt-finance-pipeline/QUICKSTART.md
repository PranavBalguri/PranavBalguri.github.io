# ⚡ Quickstart — Run This Project in 15 Minutes

Follow these steps exactly. You'll have a working dbt pipeline running locally.

---

## Step 1 — Install Python (5 mins)

1. Go to: https://www.python.org/downloads/
2. Click the big yellow **"Download Python 3.12.x"** button
3. Run the installer
4. ✅ IMPORTANT: Tick **"Add Python to PATH"** before clicking Install
5. Click Install Now

**Check it worked** — open Command Prompt (Windows) or Terminal (Mac) and type:
```
python --version
```
You should see: `Python 3.12.x`

---

## Step 2 — Install dbt + DuckDB (2 mins)

In the same Command Prompt / Terminal, paste this:
```
pip install dbt-duckdb
```

Wait for it to finish, then check:
```
dbt --version
```
You should see dbt version info printed.

---

## Step 3 — Download the project (1 min)

Option A — If you have Git installed:
```
git clone https://github.com/PranavBalguri/dbt-finance-pipeline.git
cd dbt-finance-pipeline
```

Option B — Download ZIP from GitHub and unzip it, then:
```
cd dbt-finance-pipeline
```

---

## Step 4 — Set up your dbt profile (2 mins)

Create a folder called `.dbt` in your home directory, then create a file
called `profiles.yml` inside it.

**Windows path:** `C:\Users\YourName\.dbt\profiles.yml`
**Mac/Linux path:** `~/.dbt/profiles.yml`

Paste this into the file:
```yaml
dbt_finance_pipeline:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ./finance.duckdb
```

---

## Step 5 — Run the pipeline! (2 mins)

Make sure you're inside the project folder, then run these one by one:

```bash
# 1. Load the sample data
dbt seed

# 2. Build all models
dbt run

# 3. Run data quality tests
dbt test

# 4. Generate and view documentation
dbt docs generate
dbt docs serve
```

After `dbt docs serve`, open your browser and go to:
**http://localhost:8080**

You'll see the full **data lineage graph** — this is what you show in interviews! 🎉

---

## What you'll see

After running, you'll have these tables in your local `finance.duckdb` database:

| Table | Rows | What it shows |
|---|---|---|
| `stg_transactions` | 40 | Cleaned transactions |
| `stg_accounts` | 10 | Cleaned account data |
| `fct_daily_pnl` | ~20 | Daily P&L by business line |
| `fct_fraud_indicators` | 10 | Fraud risk score per account |
| `dim_accounts` | 10 | Account dimension with stats |

---

## Viewing your data

Install DBeaver (free): https://dbeaver.io/download/

Connect to DuckDB → point it at your `finance.duckdb` file → explore your tables!

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: financial reporting pipeline"
git remote add origin https://github.com/PranavBalguri/dbt-finance-pipeline.git
git push -u origin main
```

Then link it from your portfolio site at https://pranavbalguri.github.io 🚀
