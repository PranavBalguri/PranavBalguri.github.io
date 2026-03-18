# 🇬🇧 UK Insurance Group — FY Results Dashboard

An analyst-built dashboard tracking FY2022–FY2024 financial results for five major UK insurance groups.

**Live app →** *(add your Streamlit Cloud URL here after deployment)*

---

## Companies Covered

| Company | Ticker | Segment |
|---|---|---|
| Admiral Group | ADM.L | Personal Lines Motor |
| Aviva | AV.L | Composite (GI + Life + Wealth) |
| Allianz UK | Subsidiary of ALV.DE | Commercial & Personal Lines |
| Ageas | AGS.BR | Personal Lines (Motor & Home) |
| Sabre Insurance | SBRE.L | Specialist Motor (non-standard) |

---

## What the Dashboard Shows

- **Snapshot tab** — Latest year KPI cards, Revenue bar chart, COR comparison
- **3-Year Trends tab** — Revenue, Profit, and COR trend lines FY2022–FY2024
- **Full Table tab** — All figures in one place
- **Sources tab** — Every number linked to its official press release

---

## Data & Sources

All figures are sourced directly from official company investor relations press releases or RNS regulatory filings. No third-party data vendors. No estimates.

| Company | Source |
|---|---|
| Admiral | [admiralgroup.co.uk/investor-relations](https://admiralgroup.co.uk/investor-relations/results-reports-and-presentations) |
| Aviva | [aviva.com/investors](https://www.aviva.com/investors/results-presentations-reports/) |
| Allianz UK | [allianz.co.uk/news-and-insight](https://www.allianz.co.uk/news-and-insight/news.html) |
| Ageas | [ageas.com/en/investors](https://www.ageas.com/en/investors/financial-results) |
| Sabre | [sabreplc.co.uk/investors](https://sabreplc.co.uk/investors/results-centre/) |

> **IFRS 17 Note:** Aviva, Ageas and Allianz UK adopted IFRS 17 in 2023 (restating FY2022 comparatives). FY2022 data reflects restated figures where published. Pre-2022 data excluded to preserve comparability across all five companies.

---

## How to Update (takes ~10 minutes per results season)

1. Visit the company's IR page (links in Sources tab)
2. Open `data/results.py` on GitHub → click pencil icon
3. Add a new `year` entry at the top of that company's `history` list
4. Open `data/alerts.json` → set that company's `status` back to `"current"`
5. Commit both files → dashboard refreshes in ~60 seconds

---

## Project Structure

```
uk-insurance-results/
├── app.py                        # Streamlit dashboard
├── requirements.txt              # Python dependencies
├── data/
│   ├── results.py                # ← Edit this when new results come out
│   └── alerts.json               # Auto-managed alert flags
└── .github/
    └── workflows/
        └── check_results.yml     # Weekly automated checker (every Monday 8am)
```

---

## Local Setup (optional)

```bash
git clone https://github.com/YOUR_USERNAME/uk-insurance-results
cd uk-insurance-results
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub (public)
2. Go to [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub
3. New app → select this repo → `app.py` → Deploy
4. Share the URL

---

*Data from official company IR pages only.*
