# data/results.py
# ─────────────────────────────────────────────────────────────────────────────
# UK Insurance Group — FY Results Data (FY2022 to FY2024)
#
# HOW TO UPDATE:
#   1. When new results are published, update the relevant company block below
#   2. Add a new year entry to the HISTORY list for that company
#   3. Update LAST_UPDATED at the top
#   4. Commit both this file and data/alerts.json to GitHub
#   5. Streamlit Cloud auto-refreshes within ~60 seconds
#
# SOURCE LINKS (one per company — verified official press releases):
#   Admiral  → https://admiralgroup.co.uk/investor-relations/results-reports-and-presentations
#   Aviva    → https://www.aviva.com/investors/results-presentations-reports/
#   Allianz  → https://www.allianz.co.uk/news-and-insight/news.html
#   Ageas    → https://www.ageas.com/en/investors/financial-results
#   Sabre    → https://sabreplc.co.uk/investors/results-centre/
# ─────────────────────────────────────────────────────────────────────────────

LAST_UPDATED  = "March 2025"
LATEST_PERIOD = "FY2024"
NOTE_IFRS17   = (
    "⚠️  Aviva and Ageas adopted IFRS 17 in 2023 (restating FY2022). "
    "Allianz UK adopted IFRS 9 & 17 in 2023. FY2022 figures reflect restated "
    "comparatives where published; pre-2022 data excluded to preserve comparability."
)

# ─── COMPANY DEFINITIONS ─────────────────────────────────────────────────────
# Each company has:
#   - static metadata (never changes)
#   - HISTORY: list of dicts, one per financial year, newest first
#
# Metric keys used across all years:
#   revenue_bn   : Total revenue / GWP / Inflows (£bn). Use GBP; convert EUR at 0.85
#   profit_m     : Best available profit figure (PBT preferred; Op Profit if no PBT)
#   profit_label : Short label for what profit_m represents
#   cor_pct      : Combined Operating Ratio (%). None if not disclosed.
#   solvency_pct : Solvency II ratio (%). None if not disclosed / subsidiary.
#   source_url   : Direct URL to the press release for that year
#   source_label : Human-readable label shown in Sources tab
#   results_date : Date results published
# ─────────────────────────────────────────────────────────────────────────────

COMPANIES = [
    {
        # ── ADMIRAL GROUP PLC ─────────────────────────────────────────────────
        "company"  : "Admiral Group",
        "ticker"   : "ADM.L",
        "segment"  : "Personal Lines Motor",
        "currency" : "GBP",
        "color"    : "#E63946",
        "history"  : [
            {
                "year"         : "FY2024",
                "revenue_bn"   : 6.15,
                "profit_m"     : 839.2,
                "profit_label" : "Profit Before Tax",
                "cor_pct"      : None,
                "solvency_pct" : 203.0,
                "source_url"   : "https://admiralgroup.co.uk/news-releases/news-release-details/admiral-fy24-admiral-group-reports-excellent-2024-performance",
                "source_label" : "Admiral FY2024 Press Release — 6 Mar 2025",
                "results_date" : "6 Mar 2025",
            },
            {
                "year"         : "FY2023",
                "revenue_bn"   : 4.81,
                "profit_m"     : 442.8,
                "profit_label" : "Profit Before Tax",
                "cor_pct"      : None,
                "solvency_pct" : 200.0,
                "source_url"   : "https://admiralgroup.co.uk/news-releases/news-release-details/admiral-group-reports-solid-profits-and-strong-growth-turnover",
                "source_label" : "Admiral FY2023 Press Release — 7 Mar 2024",
                "results_date" : "7 Mar 2024",
            },
            {
                "year"         : "FY2022",
                "revenue_bn"   : 3.68,
                "profit_m"     : 361.2,
                "profit_label" : "Profit Before Tax",
                "cor_pct"      : None,
                "solvency_pct" : 180.0,
                "source_url"   : "https://admiralgroup.co.uk/news-releases/news-release-details/admiral-group-plc-reports-resilient-2022-full-year-results",
                "source_label" : "Admiral FY2022 Press Release — 8 Mar 2023",
                "results_date" : "8 Mar 2023",
            },
        ],
    },
    {
        # ── AVIVA PLC ─────────────────────────────────────────────────────────
        "company"  : "Aviva",
        "ticker"   : "AV.L",
        "segment"  : "Composite (GI + Life + Wealth)",
        "currency" : "GBP",
        "color"    : "#2A9D8F",
        "history"  : [
            {
                "year"         : "FY2024",
                "revenue_bn"   : 20.7,
                "profit_m"     : 1767.0,
                "profit_label" : "Group Operating Profit",
                "cor_pct"      : 96.3,
                "solvency_pct" : 203.0,
                "source_url"   : "https://www.aviva.com/newsroom/news-releases/2025/02/FY2024-results-announcement/",
                "source_label" : "Aviva FY2024 Results Announcement — 27 Feb 2025",
                "results_date" : "27 Feb 2025",
            },
            {
                "year"         : "FY2023",
                "revenue_bn"   : 18.4,
                "profit_m"     : 1467.0,
                "profit_label" : "Group Operating Profit",
                "cor_pct"      : 96.2,
                "solvency_pct" : 207.0,
                "source_url"   : "https://www.aviva.com/newsroom/news-releases/2024/03/FY2023-results-announcement/",
                "source_label" : "Aviva FY2023 Results Announcement — 7 Mar 2024",
                "results_date" : "7 Mar 2024",
            },
            {
                "year"         : "FY2022",
                "revenue_bn"   : 16.0,
                "profit_m"     : 1350.0,
                "profit_label" : "Group Operating Profit",
                "cor_pct"      : 94.6,
                "solvency_pct" : 212.0,
                "source_url"   : "https://www.aviva.com/newsroom/news-releases/2023/03/FY2022-results-announcement/",
                "source_label" : "Aviva FY2022 Results Announcement — 9 Mar 2023",
                "results_date" : "9 Mar 2023",
            },
        ],
    },
    {
        # ── ALLIANZ UK ────────────────────────────────────────────────────────
        "company"  : "Allianz UK",
        "ticker"   : "Subsidiary of ALV.DE",
        "segment"  : "Commercial & Personal Lines",
        "currency" : "GBP",
        "color"    : "#E9C46A",
        "history"  : [
            {
                "year"         : "FY2024",
                "revenue_bn"   : 4.66,
                "profit_m"     : 367.8,
                "profit_label" : "Operating Profit",
                "cor_pct"      : 95.0,
                "solvency_pct" : None,
                "source_url"   : "https://www.allianz.co.uk/news-and-insight/news/total-business-volumes-increase-for-allianz-group-in-the-uk.html",
                "source_label" : "Allianz UK FY2024 Press Release — 3 Mar 2025",
                "results_date" : "3 Mar 2025",
            },
            {
                "year"         : "FY2023",
                "revenue_bn"   : 4.26,
                "profit_m"     : 241.6,
                "profit_label" : "Operating Profit",
                "cor_pct"      : 96.9,
                "solvency_pct" : None,
                "source_url"   : "https://www.allianz.co.uk/news-and-insight/news/allianz-trading-roundup-2023.html",
                "source_label" : "Allianz UK FY2023 Press Release — Mar 2024",
                "results_date" : "Mar 2024",
            },
            {
                "year"         : "FY2022",
                "revenue_bn"   : 3.97,
                "profit_m"     : 146.4,
                "profit_label" : "Operating Profit",
                "cor_pct"      : 98.4,
                "solvency_pct" : None,
                "source_url"   : "https://www.allianz.co.uk/news-and-insight/news/allianz-trading-roundup-2022.html",
                "source_label" : "Allianz UK FY2022 Press Release — Mar 2023",
                "results_date" : "Mar 2023",
            },
        ],
    },
    {
        # ── AGEAS (GROUP) ─────────────────────────────────────────────────────
        "company"  : "Ageas",
        "ticker"   : "AGS.BR",
        "segment"  : "Personal Lines (Motor & Home)",
        "currency" : "EUR→GBP",
        "color"    : "#457B9D",
        "history"  : [
            {
                "year"         : "FY2024",
                "revenue_bn"   : 15.3,
                "profit_m"     : 1054.0,   # €1.24bn × 0.85
                "profit_label" : "Net Operating Result",
                "cor_pct"      : 93.3,
                "solvency_pct" : 218.0,
                "source_url"   : "https://www.ageas.com/en/newsroom/ageas-reports-full-year-results-2024",
                "source_label" : "Ageas FY2024 Press Release — 27 Feb 2025",
                "results_date" : "27 Feb 2025",
            },
            {
                "year"         : "FY2023",
                "revenue_bn"   : 14.5,     # €17.1bn × 0.85
                "profit_m"     : 991.1,    # €1.166bn × 0.85
                "profit_label" : "Net Operating Result",
                "cor_pct"      : 93.3,
                "solvency_pct" : 217.0,
                "source_url"   : "https://www.ageas.com/en/newsroom/ageas-reports-full-year-results-2023",
                "source_label" : "Ageas FY2023 Press Release — 28 Feb 2024",
                "results_date" : "28 Feb 2024",
            },
            {
                "year"         : "FY2022",
                "revenue_bn"   : 13.3,     # approx €15.6bn × 0.85
                "profit_m"     : 884.0,    # approx €1.04bn × 0.85
                "profit_label" : "Net Operating Result",
                "cor_pct"      : 94.1,
                "solvency_pct" : 218.0,
                "source_url"   : "https://www.ageas.com/en/investors/financial-results",
                "source_label" : "Ageas FY2022 Press Release — Feb 2023",
                "results_date" : "Feb 2023",
            },
        ],
    },
    {
        # ── SABRE INSURANCE GROUP PLC ─────────────────────────────────────────
        "company"  : "Sabre Insurance",
        "ticker"   : "SBRE.L",
        "segment"  : "Specialist Motor (non-standard)",
        "currency" : "GBP",
        "color"    : "#6A0572",
        "history"  : [
            {
                "year"         : "FY2024",
                "revenue_bn"   : 0.236,
                "profit_m"     : 48.6,
                "profit_label" : "Profit Before Tax",
                "cor_pct"      : 84.2,
                "solvency_pct" : 171.2,
                "source_url"   : "https://sabreplc.co.uk/investors/results-centre/",
                "source_label" : "Sabre FY2024 RNS Results — 18 Mar 2025",
                "results_date" : "18 Mar 2025",
            },
            {
                "year"         : "FY2023",
                "revenue_bn"   : 0.225,
                "profit_m"     : 23.6,
                "profit_label" : "Profit Before Tax",
                "cor_pct"      : 86.3,
                "solvency_pct" : 205.3,
                "source_url"   : "https://sabreplc.co.uk/investors/results-centre-2023/",
                "source_label" : "Sabre FY2023 RNS Results — 19 Mar 2024",
                "results_date" : "19 Mar 2024",
            },
            {
                "year"         : "FY2022",
                "revenue_bn"   : 0.171,
                "profit_m"     : 14.0,
                "profit_label" : "Profit Before Tax",
                "cor_pct"      : 93.4,
                "solvency_pct" : None,
                "source_url"   : "https://sabreplc.co.uk/investors/results-centre-archive/",
                "source_label" : "Sabre FY2022 RNS Results — Mar 2023",
                "results_date" : "Mar 2023",
            },
        ],
    },
]
