# .github/workflows/checker.py
# ─────────────────────────────────────────────────────────────────────────────
# Weekly automated checker — runs via GitHub Actions every Monday 08:00 UTC
# Visits each company's IR page, looks for signs of new results,
# writes flags to data/alerts.json which the Streamlit app reads.
# ─────────────────────────────────────────────────────────────────────────────

import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import date

TODAY        = date.today()
CURRENT_YEAR = TODAY.year

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ─── COMPANY CHECK CONFIG ────────────────────────────────────────────────────
# check_url      : Primary page to scan for new results keywords
# backup_url     : Fallback if primary fails
# keywords       : Phrases that indicate NEW results have been published
# current_period : What we already have — used to derive next expected period
# results_months : Months we expect results (skip check outside these months
#                  unless running in DEV_MODE)

WATCH_LIST = [
    {
        "name"           : "Admiral Group",
        "current_period" : "FY2024",
        "check_url"      : "https://admiralgroup.co.uk/investor-relations/results-reports-and-presentations",
        "backup_url"     : "https://admiralgroup.co.uk/news-releases",
        "keywords"       : [
            "full year 2025", "fy2025", "fy 2025",
            "full year results 2025", "2025 annual results",
            "preliminary results 2025",
        ],
        "results_months" : [2, 3],
    },
    {
        "name"           : "Aviva",
        "current_period" : "FY2024",
        "check_url"      : "https://www.aviva.com/investors/results-presentations-reports/",
        "backup_url"     : "https://www.aviva.com/newsroom/news-releases/",
        "keywords"       : [
            "full year 2025", "fy2025", "2025 results",
            "results announcement 2025", "annual results 2025",
        ],
        "results_months" : [2, 3],
    },
    {
        "name"           : "Allianz UK",
        "current_period" : "FY2024",
        "check_url"      : "https://www.allianz.co.uk/news-and-insight/news.html",
        "backup_url"     : None,
        "keywords"       : [
            "full year 2025", "2025 results", "fy2025",
            "annual results 2025", "trading roundup 2025",
        ],
        "results_months" : [2, 3],
    },
    {
        "name"           : "Ageas",
        "current_period" : "FY2024",
        "check_url"      : "https://www.ageas.com/en/newsroom",
        "backup_url"     : "https://www.ageas.com/en/investors/financial-results",
        "keywords"       : [
            "full-year results 2025", "full year results 2025",
            "fy2025", "2025 results", "annual results 2025",
        ],
        "results_months" : [2, 3],
    },
    {
        "name"           : "Sabre Insurance",
        "current_period" : "FY2024",
        "check_url"      : "https://sabreplc.co.uk/investors/results-centre/",
        "backup_url"     : None,
        "keywords"       : [
            "full year 2025", "fy2025", "2025 results",
            "annual results 2025", "preliminary results 2025",
        ],
        "results_months" : [2, 3, 4],
    },
]


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def is_dev_mode() -> bool:
    return os.environ.get("DEV_MODE", "false").lower() == "true"


def fetch_text(url: str) -> str:
    """Fetch a URL and return visible text, lower-cased. Returns '' on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator=" ").lower()
    except Exception as e:
        print(f"    ⚠  Could not fetch {url}: {e}")
        return ""


def check_company(entry: dict) -> tuple[bool, str]:
    """
    Returns (alert: bool, message: str)

    Logic:
    1. Skip if outside results_months (unless DEV_MODE)
    2. Fetch primary URL (fall back to backup)
    3. Search for keywords that signal NEW (next-period) results
    4. Return alert=True + message if found
    """
    name    = entry["name"]
    current = entry["current_period"]          # e.g. "FY2024"
    yr_num  = int(re.search(r"\d{4}", current).group())
    next_yr = yr_num + 1

    # Skip check outside results season (saves unnecessary HTTP requests)
    if TODAY.month not in entry["results_months"] and not is_dev_mode():
        print(f"  ⏭  {name}: outside results months — skip")
        return False, ""

    print(f"  🔍 Checking {name}...")

    text = fetch_text(entry["check_url"])
    if not text and entry.get("backup_url"):
        print(f"     Primary failed, trying backup...")
        text = fetch_text(entry["backup_url"])

    if not text:
        print(f"     ❌ Could not load any page for {name}")
        return False, ""

    # Check for keyword matches
    hits = [kw for kw in entry["keywords"] if kw in text]

    # Also check plain year reference near "result" or "profit"
    if not hits:
        pattern = rf"\b{next_yr}\b"
        if re.search(pattern, text):
            nearby = re.findall(
                rf".{{0,60}}{next_yr}.{{0,60}}", text
            )
            profit_nearby = [s for s in nearby if any(
                w in s for w in ["result", "profit", "turnover", "premium", "revenue"]
            )]
            if profit_nearby:
                hits.append(f"{next_yr} near financial keyword")

    if hits:
        msg = (
            f"Possible FY{next_yr} results detected for {name}. "
            f"Signals: {', '.join(hits[:3])}. "
            f"Please check {entry['check_url']} and update data/results.py."
        )
        print(f"     🚨 ALERT: {msg}")
        return True, msg

    print(f"     ✅ {name}: no new results found (still on {current})")
    return False, ""


# ─── MAIN ────────────────────────────────────────────────────────────────────

def run():
    print(f"\n📅 Results checker — {TODAY}\n{'─'*50}")

    # Load existing alerts
    alerts_path = "data/alerts.json"
    try:
        with open(alerts_path) as f:
            alerts = json.load(f)
    except FileNotFoundError:
        alerts = {}

    changed = False

    for entry in WATCH_LIST:
        name           = entry["name"]
        current_status = alerts.get(name, {}).get("status", "current")

        # Don't re-check if already flagged or snoozed — wait for human action
        if current_status in ("alert", "snoozed"):
            print(f"  ⏸  {name}: status is '{current_status}' — skipping until resolved")
            continue

        alert, message = check_company(entry)

        if name not in alerts:
            alerts[name] = {}

        alerts[name]["last_checked"] = TODAY.isoformat()

        if alert:
            alerts[name]["status"]        = "alert"
            alerts[name]["alert_message"] = message
            changed = True
        else:
            alerts[name]["status"]        = "current"
            alerts[name]["alert_message"] = ""

    # Write back
    with open(alerts_path, "w") as f:
        json.dump(alerts, f, indent=2)

    print(f"\n{'─'*50}")
    print(f"{'🔔 alerts.json updated' if changed else '✅ No changes — all current'}")
    print(f"Written to {alerts_path}\n")


if __name__ == "__main__":
    run()
