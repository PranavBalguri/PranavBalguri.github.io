"""
app.py — UK Insurance Group FY Results Dashboard
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data.results import COMPANIES, LAST_UPDATED, LATEST_PERIOD, NOTE_IFRS17

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UK Insurance Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── MINIMAL CUSTOM CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    /* cleaner metric cards */
    [data-testid="metric-container"] {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px 16px;
    }
    /* source link styling */
    .source-tag {
        font-size: 11px;
        color: #6c757d;
        font-style: italic;
    }
    /* section divider */
    .section-title {
        font-size: 13px;
        font-weight: 600;
        color: #495057;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def load_alerts() -> dict:
    path = Path("data/alerts.json")
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def build_flat_df() -> pd.DataFrame:
    """Flatten COMPANIES + HISTORY into a single DataFrame."""
    rows = []
    for co in COMPANIES:
        for yr in co["history"]:
            rows.append({
                "Company"      : co["company"],
                "Ticker"       : co["ticker"],
                "Segment"      : co["segment"],
                "Color"        : co["color"],
                "Year"         : yr["year"],
                "Revenue (£bn)": yr["revenue_bn"],
                "Profit (£m)"  : yr["profit_m"],
                "Profit Label" : yr["profit_label"],
                "COR (%)"      : yr["cor_pct"],
                "Solvency (%)" : yr["solvency_pct"],
                "Source URL"   : yr["source_url"],
                "Source Label" : yr["source_label"],
                "Results Date" : yr["results_date"],
            })
    return pd.DataFrame(rows)


def fmt_profit(row) -> str:
    label = row["Profit Label"]
    val   = row["Profit (£m)"]
    if label == "Net Operating Result":
        # Ageas: show EUR equivalent
        eur = round(val / 0.85 * 1000) / 1000
        return f"€{eur:.2f}bn NOR"
    return f"£{val:,.0f}m"


def latest_row(df: pd.DataFrame, company: str) -> pd.Series:
    return df[(df["Company"] == company) & (df["Year"] == LATEST_PERIOD)].iloc[0]


# ─── ALERT BANNER ────────────────────────────────────────────────────────────

def show_alerts():
    alerts = load_alerts()
    active = [(n, i) for n, i in alerts.items() if i.get("status") == "alert"]
    if not active:
        return
    st.warning(
        f"🔔 **New results may be available for "
        f"{', '.join(n for n, _ in active)}** — data may need updating.",
        icon="⚠️",
    )
    for name, info in active:
        with st.expander(f"Action required — {name}"):
            st.write(info.get("alert_message", "New results detected."))
            co = next((c for c in COMPANIES if c["company"] == name), None)
            if co:
                st.markdown(f"👉 **[Go to IR page →]({co['history'][0]['source_url']})**")
            st.code(
                "1. Visit the IR page above\n"
                "2. Note the new headline numbers\n"
                "3. Open data/results.py on GitHub → edit → add new year entry\n"
                "4. Set alerts.json status back to 'current'\n"
                "5. Commit — dashboard refreshes in ~60 seconds",
                language="text",
            )


# ─── MAIN APP ─────────────────────────────────────────────────────────────────

df = build_flat_df()
df_latest = df[df["Year"] == LATEST_PERIOD].copy()
years = sorted(df["Year"].unique())
companies = [c["company"] for c in COMPANIES]
color_map = {c["company"]: c["color"] for c in COMPANIES}

show_alerts()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🇬🇧 UK Insurance — Group Results Dashboard")
st.caption(
    f"**Showing:** {LATEST_PERIOD} latest  |  "
    f"**3-year trend:** FY2022 – FY2024  |  "
    f"**Last updated:** {LAST_UPDATED}  |  "
    f"Source: Official company IR press releases"
)
st.divider()

# ── Tab layout ────────────────────────────────────────────────────────────────
tab_snapshot, tab_trends, tab_table, tab_sources, tab_about = st.tabs([
    "📌 Snapshot",
    "📈 3-Year Trends",
    "🗂 Full Table",
    "🔗 Sources",
    "ℹ️ About",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SNAPSHOT (latest year KPI cards + two charts)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_snapshot:

    st.markdown(f"<p class='section-title'>{LATEST_PERIOD} Key Metrics</p>", unsafe_allow_html=True)

    # KPI cards — one per company
    cols = st.columns(5)
    for col, co in zip(cols, COMPANIES):
        row = latest_row(df, co["company"])
        with col:
            st.metric(
                label=co["company"],
                value=f"£{row['Revenue (£bn)']:.2f}bn",
                delta=None,
            )
            st.caption(
                f"**{row['Profit Label']}:** {fmt_profit(row)}\n\n"
                f"**COR:** {row['COR (%)']:.1f}%"
                if row["COR (%)"] else
                f"**{row['Profit Label']}:** {fmt_profit(row)}"
            )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<p class='section-title'>Revenue / GWP / Inflows — FY2024 (£bn)</p>", unsafe_allow_html=True)
        fig = px.bar(
            df_latest.sort_values("Revenue (£bn)", ascending=True),
            x="Revenue (£bn)",
            y="Company",
            orientation="h",
            color="Company",
            color_discrete_map=color_map,
            text="Revenue (£bn)",
        )
        fig.update_traces(texttemplate="£%{x:.2f}bn", textposition="outside")
        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="",
            plot_bgcolor="white",
            margin=dict(l=0, r=60, t=10, b=10),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<p class='section-title'>Combined Operating Ratio — FY2024 (lower = better)</p>", unsafe_allow_html=True)
        df_cor = df_latest[df_latest["COR (%)"].notna()].sort_values("COR (%)")
        fig2 = px.bar(
            df_cor,
            x="COR (%)",
            y="Company",
            orientation="h",
            color="COR (%)",
            color_continuous_scale=["#2A9D8F", "#E9C46A", "#E63946"],
            range_color=[82, 100],
            text="COR (%)",
        )
        fig2.update_traces(texttemplate="%{x:.1f}%", textposition="outside")
        fig2.add_vline(x=100, line_dash="dash", line_color="#adb5bd",
                       annotation_text="100% breakeven", annotation_position="top right")
        fig2.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title="",
            plot_bgcolor="white",
            margin=dict(l=0, r=60, t=10, b=10),
            height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # IFRS note
    st.info(NOTE_IFRS17, icon="ℹ️")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — 3-YEAR TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_trends:

    st.markdown("<p class='section-title'>Revenue / GWP / Inflows (£bn) — FY2022 to FY2024</p>", unsafe_allow_html=True)

    fig3 = px.line(
        df,
        x="Year",
        y="Revenue (£bn)",
        color="Company",
        color_discrete_map=color_map,
        markers=True,
        line_shape="linear",
    )
    fig3.update_traces(line_width=2.5, marker_size=8)
    fig3.update_layout(
        plot_bgcolor="white",
        yaxis_title="£bn",
        xaxis_title="",
        legend_title="",
        height=380,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<p class='section-title'>Profit (£m) — FY2022 to FY2024</p>", unsafe_allow_html=True)
    st.caption("Admiral & Sabre = PBT · Aviva & Allianz = Operating Profit · Ageas = Net Operating Result (GBP equivalent)")

    fig4 = px.bar(
        df,
        x="Year",
        y="Profit (£m)",
        color="Company",
        barmode="group",
        color_discrete_map=color_map,
    )
    fig4.update_layout(
        plot_bgcolor="white",
        yaxis_title="£m",
        xaxis_title="",
        legend_title="",
        height=380,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<p class='section-title'>Combined Operating Ratio (%) — FY2022 to FY2024</p>", unsafe_allow_html=True)
    st.caption("Allianz UK not solvency-rated (subsidiary). Admiral COR not separately disclosed at group level.")

    df_cor_trend = df[df["COR (%)"].notna()].copy()
    fig5 = px.line(
        df_cor_trend,
        x="Year",
        y="COR (%)",
        color="Company",
        color_discrete_map=color_map,
        markers=True,
    )
    fig5.add_hline(y=100, line_dash="dash", line_color="#adb5bd",
                   annotation_text="100% = breakeven")
    fig5.update_traces(line_width=2.5, marker_size=8)
    fig5.update_layout(
        plot_bgcolor="white",
        yaxis_title="%",
        xaxis_title="",
        legend_title="",
        height=360,
        margin=dict(l=0, r=0, t=10, b=10),
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.info(NOTE_IFRS17, icon="ℹ️")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FULL TABLE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_table:

    st.markdown("<p class='section-title'>All figures — FY2022 to FY2024</p>", unsafe_allow_html=True)

    display = df[[
        "Company", "Year", "Revenue (£bn)", "Profit Label",
        "Profit (£m)", "COR (%)", "Solvency (%)", "Results Date"
    ]].copy()

    display["Revenue (£bn)"] = display["Revenue (£bn)"].apply(lambda x: f"£{x:.2f}bn")
    display["Profit (£m)"]   = display["Profit (£m)"].apply(lambda x: f"£{x:,.0f}m")
    display["COR (%)"]       = display["COR (%)"].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "—"
    )
    display["Solvency (%)"]  = display["Solvency (%)"].apply(
        lambda x: f"{x:.0f}%" if pd.notna(x) else "—"
    )

    st.dataframe(
        display.rename(columns={"Profit Label": "Profit Metric"}),
        use_container_width=True,
        hide_index=True,
        height=460,
    )

    st.caption(
        "Profit metric varies by company: Admiral & Sabre = PBT · "
        "Aviva & Allianz UK = Operating Profit · Ageas = Net Operating Result (converted to GBP at €1 = £0.85)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SOURCES
# ═══════════════════════════════════════════════════════════════════════════════
with tab_sources:

    st.markdown("<p class='section-title'>Every number traced to its official source</p>", unsafe_allow_html=True)
    st.caption(
        "All data sourced directly from official company investor relations press releases "
        "or RNS filings. No third-party data vendors. No estimates."
    )

    for co in COMPANIES:
        with st.expander(f"**{co['company']}** — {co['ticker']} — {co['segment']}"):
            for yr in co["history"]:
                st.markdown(
                    f"**{yr['year']}** &nbsp;·&nbsp; "
                    f"Published: {yr['results_date']} &nbsp;·&nbsp; "
                    f"[{yr['source_label']} ↗]({yr['source_url']})"
                )
            st.divider()

    st.info(NOTE_IFRS17, icon="ℹ️")
    st.caption(
        "Dashboard auto-refreshes when data/results.py is updated on GitHub. "
        "For questions contact Pranav Balguri."
    )
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_about:

    st.markdown("<p class='section-title'>About this dashboard</p>",
                unsafe_allow_html=True)

    st.markdown("""
    This dashboard tracks FY2022–FY2024 financial results for five major
    UK insurance groups, built for peer benchmarking and trend analysis.
    """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Companies covered**")
        for co in COMPANIES:
            st.markdown(f"- {co['company']} — `{co['ticker']}`")

    with col2:
        st.markdown("**KPIs tracked**")
        st.markdown("""
        - Revenue / GWP / Inflows (£bn)
        - Profit — PBT / Operating / NOR (£m)
        - Combined Operating Ratio (%)
        - Solvency II ratio (%)
        """)

    st.divider()

    st.markdown("**Data & Sources**")
    st.markdown("""
    All figures sourced directly from official company investor relations
    press releases or RNS regulatory filings. No third-party data vendors.
    No estimates. Every number links to its original document in the
    **Sources** tab.
    """)

    st.info(NOTE_IFRS17, icon="ℹ️")

    st.divider()

    st.markdown("**Built by**")
    st.markdown("""
    Pranav Balguri — Data Analytics Engineer  
    [GitHub →](https://github.com/PranavBalguri)
    """)
