# Security Master Data Quality Dashboard

> A hedge fund reference data operations tool built with Streamlit and Claude AI

![Python](https://img.shields.io/badge/Python-3.11-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red) ![Claude](https://img.shields.io/badge/Claude-Sonnet-orange)

## Overview

This project simulates a **Reference Data Operations** workflow at an institutional hedge fund — the kind of tooling used by teams managing security master data across equities, bonds, and derivatives.

It demonstrates:
- **Data quality exception detection** across a security master dataset
- **Corporate action tracking** and upcoming event alerting
- **Exception lifecycle management** (open → investigate → resolve)
- **AI-powered natural language querying** via Claude API (Text-to-SQL pattern)

## Features

### 📋 Security Master View
- Full instrument universe across equities and bonds
- Live data quality scoring per security
- Highlighted rows for securities with active exceptions
- Search by name, ticker, ISIN, or security ID

### ⚠️ Exception Manager
- Pre-loaded exception log with severity levels (Critical / High / Medium / Low)
- Live auto-detection of DQ issues: missing ISINs, invalid currencies, stale prices
- Exception resolution workflow with notes and audit trail

### 📅 Corporate Actions
- Tracks dividends, stock splits, rights issues, bond maturities
- Flags unprocessed upcoming actions

### 🤖 AI Query Assistant (Claude-powered)
- Natural language querying over the security master and exceptions
- Claude converts questions to pandas code and executes against the data
- Example: *"Show all equities missing an ISIN"*

## Data Quality Rules

| Rule | Severity |
|------|----------|
| Missing ISIN (Equity) | High |
| Missing Currency | High |
| Invalid Currency Code | High |
| Missing Ticker | Medium |
| Stale Price (>30 days) | Medium |
| Manual Data Source | Medium |

## Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| Data | Pandas + CSV |
| AI | Anthropic Claude API |
| Language | Python 3.11 |

## Run Locally

```bash
git clone https://github.com/PranavBalguri/PranavBalguri.github.io
cd PranavBalguri.github.io/security-master-dq
pip install -r requirements.txt
streamlit run app.py
```

Add your Anthropic API key in the sidebar to enable the AI Query Assistant.

## Author

**Pranav Balguri** — Finance Data Analyst | Analytics Engineer  
[pranavbalguri.github.io](https://pranavbalguri.github.io) · RaKiTics
