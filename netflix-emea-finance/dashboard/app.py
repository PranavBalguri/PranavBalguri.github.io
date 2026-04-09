import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import os

st.set_page_config(
    page_title="Netflix EMEA Production Finance",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LOAD DATA INTO DUCKDB & RUN SQL
# ─────────────────────────────────────────

@st.cache_data
def run_queries():
    # Detect if running on Streamlit Cloud or locally
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")

    con = duckdb.connect()

    # Load CSVs into DuckDB as tables
    con.execute(f"""
        CREATE TABLE raw_productions AS
        SELECT * FROM read_csv_auto('{data_path}/raw_productions.csv')
    """)
    con.execute(f"""
        CREATE TABLE raw_vendors AS
        SELECT * FROM read_csv_auto('{data_path}/raw_vendors.csv')
    """)
    con.execute(f"""
        CREATE TABLE raw_spend AS
        SELECT * FROM read_csv_auto('{data_path}/raw_spend.csv')
    """)
    con.execute(f"""
        CREATE TABLE raw_headcount AS
        SELECT * FROM read_csv_auto('{data_path}/raw_headcount.csv')
    """)

    # ── Query 01: Vendor spend by market ──
    vendor_spend = con.execute("""
        WITH spend_enriched AS (
            SELECT s.spend_id, s.production_id, s.spend_gbp,
                   s.spend_category, s.month,
                   v.vendor_name, v.vendor_type, v.market
            FROM raw_spend s
            LEFT JOIN raw_vendors v ON s.vendor_id = v.vendor_id
        ),
        market_summary AS (
            SELECT market, spend_category,
                   SUM(spend_gbp) AS total_spend_gbp,
                   COUNT(DISTINCT production_id) AS productions_count
            FROM spend_enriched
            GROUP BY market, spend_category
        ),
        market_totals AS (
            SELECT market, SUM(total_spend_gbp) AS market_total_gbp
            FROM market_summary GROUP BY market
        )
        SELECT ms.market, ms.spend_category,
               ms.total_spend_gbp, ms.productions_count,
               mt.market_total_gbp,
               ROUND(ms.total_spend_gbp * 100.0 / mt.market_total_gbp, 1) AS pct_of_market,
               RANK() OVER (PARTITION BY ms.market ORDER BY ms.total_spend_gbp DESC) AS rank_in_market
        FROM market_summary ms
        LEFT JOIN market_totals mt ON ms.market = mt.market
        ORDER BY mt.market_total_gbp DESC, ms.total_spend_gbp DESC
    """).df()

    # ── Query 02: YoY spend growth ──
    yoy_spend = con.execute("""
        WITH spend_with_year AS (
            SELECT s.spend_gbp, v.market,
                   CAST(LEFT(s.month, 4) AS INTEGER) AS spend_year
            FROM raw_spend s
            LEFT JOIN raw_vendors v ON s.vendor_id = v.vendor_id
        ),
        annual AS (
            SELECT market, spend_year,
                   SUM(spend_gbp) AS total_spend_gbp
            FROM spend_with_year GROUP BY market, spend_year
        )
        SELECT market, spend_year, total_spend_gbp,
               LAG(total_spend_gbp) OVER (PARTITION BY market ORDER BY spend_year) AS prior_year,
               CASE WHEN LAG(total_spend_gbp) OVER (PARTITION BY market ORDER BY spend_year) IS NULL THEN NULL
               ELSE ROUND((total_spend_gbp - LAG(total_spend_gbp) OVER (PARTITION BY market ORDER BY spend_year))
                    * 100.0 / LAG(total_spend_gbp) OVER (PARTITION BY market ORDER BY spend_year), 1)
               END AS yoy_growth_pct
        FROM annual ORDER BY market, spend_year
    """).df()

    # ── Query 03: Production P&L ──
    pnl = con.execute("""
        SELECT production_id, title, genre, market, year, quarter, status,
               budget_gbp, actual_spend_gbp,
               actual_spend_gbp - budget_gbp AS variance_gbp,
               ROUND((actual_spend_gbp - budget_gbp) * 100.0 / budget_gbp, 1) AS variance_pct,
               CASE WHEN actual_spend_gbp > budget_gbp * 1.10 THEN 'Significantly Over'
                    WHEN actual_spend_gbp > budget_gbp THEN 'Slightly Over'
                    WHEN actual_spend_gbp < budget_gbp * 0.90 THEN 'Significantly Under'
                    ELSE 'On Budget' END AS budget_status,
               actual_spend_gbp > budget_gbp AS is_over_budget
        FROM raw_productions
        ORDER BY variance_gbp DESC
    """).df()

    # ── Query 04: Vendor concentration ──
    vendors = con.execute("""
        WITH vs AS (
            SELECT v.vendor_id, v.vendor_name, v.vendor_type, v.market,
                   SUM(s.spend_gbp) AS total_spend_gbp,
                   COUNT(DISTINCT s.production_id) AS productions_supported
            FROM raw_spend s LEFT JOIN raw_vendors v ON s.vendor_id = v.vendor_id
            GROUP BY v.vendor_id, v.vendor_name, v.vendor_type, v.market
        ),
        total AS (SELECT SUM(spend_gbp) AS grand_total FROM raw_spend)
        SELECT vs.*, ROUND(vs.total_spend_gbp * 100.0 / total.grand_total, 2) AS pct_of_total,
               RANK() OVER (ORDER BY vs.total_spend_gbp DESC) AS overall_rank
        FROM vs CROSS JOIN total
        ORDER BY vs.total_spend_gbp DESC
    """).df()

    # ── Query 05: Jobs by market ──
    jobs = con.execute("""
        SELECT h.market, p.year,
               SUM(h.direct_jobs) AS direct_jobs,
               SUM(h.indirect_jobs) AS indirect_jobs,
               SUM(h.direct_jobs + h.indirect_jobs) AS total_jobs,
               SUM(h.crew_days) AS crew_days,
               SUM(p.actual_spend_gbp) AS total_spend,
               ROUND(SUM(p.actual_spend_gbp) * 1.0 / NULLIF(SUM(h.direct_jobs + h.indirect_jobs), 0), 0) AS spend_per_job
        FROM raw_headcount h
        LEFT JOIN raw_productions p ON h.production_id = p.production_id
        GROUP BY h.market, p.year
        ORDER BY p.year, total_jobs DESC
    """).df()

    # ── Query 06: Genre budget adherence ──
    genre = con.execute("""
        SELECT genre,
               COUNT(production_id) AS productions,
               ROUND(AVG((actual_spend_gbp - budget_gbp) * 100.0 / budget_gbp), 1) AS avg_variance_pct,
               SUM(CASE WHEN actual_spend_gbp > budget_gbp THEN 1 ELSE 0 END) AS over_budget_count,
               ROUND(SUM(CASE WHEN actual_spend_gbp > budget_gbp THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0) AS over_budget_rate,
               CASE WHEN AVG((actual_spend_gbp - budget_gbp) * 100.0 / budget_gbp) > 5 THEN 'High Risk'
                    WHEN AVG((actual_spend_gbp - budget_gbp) * 100.0 / budget_gbp) > 0 THEN 'Medium Risk'
                    ELSE 'Low Risk' END AS risk_level
        FROM raw_productions
        GROUP BY genre
        ORDER BY avg_variance_pct DESC
    """).df()

    # ── Query 08: Executive summary ──
    exec_summary = con.execute("""
        SELECT p.market, p.year,
               COUNT(p.production_id) AS productions,
               SUM(p.budget_gbp) AS total_budget,
               SUM(p.actual_spend_gbp) AS total_actual,
               ROUND(AVG((p.actual_spend_gbp - p.budget_gbp) * 100.0 / p.budget_gbp), 1) AS avg_variance_pct,
               SUM(h.direct_jobs + h.indirect_jobs) AS total_jobs,
               CASE WHEN AVG((p.actual_spend_gbp - p.budget_gbp) * 100.0 / p.budget_gbp) <= 0 THEN 'GREEN'
                    WHEN AVG((p.actual_spend_gbp - p.budget_gbp) * 100.0 / p.budget_gbp) <= 5 THEN 'AMBER'
                    ELSE 'RED' END AS health
        FROM raw_productions p
        LEFT JOIN raw_headcount h ON p.production_id = h.production_id
        GROUP BY p.market, p.year
        ORDER BY p.year, total_actual DESC
    """).df()

    con.close()
    return vendor_spend, yoy_spend, pnl, vendors, jobs, genre, exec_summary

vendor_spend, yoy_spend, pnl, vendors, jobs, genre, exec_summary = run_queries()

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("## 🎬 Netflix EMEA Production Finance Report")
st.caption("Vendor Spend · Jobs Created · Production P&L | SQL-driven analysis by Pranav Rao Balguri · [Portfolio](https://pranavbalguri.github.io)")
st.markdown("---")

# ─────────────────────────────────────────
# FILTERS
# ─────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    market_filter = st.multiselect(
        "Market",
        options=sorted(pnl["market"].unique().tolist()),
        default=sorted(pnl["market"].unique().tolist())
    )
with col2:
    year_filter = st.multiselect(
        "Year",
        options=sorted(pnl["year"].unique().tolist()),
        default=sorted(pnl["year"].unique().tolist())
    )

pnl_f       = pnl[pnl["market"].isin(market_filter) & pnl["year"].isin(year_filter)]
jobs_f      = jobs[jobs["market"].isin(market_filter) & jobs["year"].isin(year_filter)]
vs_f        = vendor_spend[vendor_spend["market"].isin(market_filter)]
exec_f      = exec_summary[exec_summary["market"].isin(market_filter) & exec_summary["year"].isin(year_filter)]

st.markdown("---")

# ─────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Budget",       f"£{pnl_f['budget_gbp'].sum()/1e6:.1f}M")
k2.metric("Actual Spend",       f"£{pnl_f['actual_spend_gbp'].sum()/1e6:.1f}M",
          f"{'▲' if pnl_f['variance_gbp'].sum() > 0 else '▼'} £{abs(pnl_f['variance_gbp'].sum())/1e6:.1f}M",
          delta_color="inverse")
k3.metric("Over Budget",        f"{int(pnl_f['is_over_budget'].sum())} of {len(pnl_f)} productions",
          delta_color="inverse")
k4.metric("Total Jobs Created", f"{int(jobs_f['total_jobs'].sum()):,}")
k5.metric("Vendor Spend",       f"£{vs_f['total_spend_gbp'].sum()/1e6:.1f}M")

st.markdown("---")

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Vendor Spend",
    "👷 Jobs Created",
    "📊 Production P&L",
    "📋 Executive Summary"
])

# ── TAB 1: VENDOR SPEND ──────────────────
with tab1:
    st.subheader("Vendor Spend Across EMEA Markets")
    st.caption("All analysis powered by SQL — see /sql/01_vendor_spend_by_market.sql")

    col1, col2 = st.columns(2)

    with col1:
        market_totals = vs_f.groupby("market")["total_spend_gbp"].sum().reset_index()
        market_totals = market_totals.sort_values("total_spend_gbp", ascending=False)
        fig = px.bar(
            market_totals, x="market", y="total_spend_gbp",
            title="Total Vendor Spend by Market",
            color="market",
            color_discrete_sequence=["#E50914","#B20710","#FF6B6B","#FF9999","#FFCCCC"],
            labels={"total_spend_gbp":"Spend (£)","market":"Market"}
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
        fig.update_traces(texttemplate="£%{y:,.0f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        category_totals = vs_f.groupby("spend_category")["total_spend_gbp"].sum().reset_index()
        fig2 = px.pie(
            category_totals, values="total_spend_gbp", names="spend_category",
            title="Spend by Category", hole=0.55,
            color_discrete_sequence=["#E50914","#221F1F","#888888","#FF6B6B"]
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("YoY Spend Growth by Market")
    st.caption("SQL: /sql/02_yoy_spend_growth.sql")
    yoy_f = yoy_spend[yoy_spend["market"].isin(market_filter)]
    fig3 = px.line(
        yoy_f, x="spend_year", y="total_spend_gbp",
        color="market", markers=True,
        title="Annual Vendor Spend Trend",
        color_discrete_sequence=["#E50914","#B20710","#FF6B6B","#888888","#FFCCCC"],
        labels={"total_spend_gbp":"Spend (£)","spend_year":"Year","market":"Market"}
    )
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    fig3.update_traces(line_width=2, marker_size=8)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Top Vendors by Spend")
    st.caption("SQL: /sql/04_vendor_concentration.sql")
    v_display = vendors[["overall_rank","vendor_name","vendor_type","market","total_spend_gbp","pct_of_total","productions_supported"]].head(10).copy()
    v_display["total_spend_gbp"] = v_display["total_spend_gbp"].apply(lambda x: f"£{x:,.0f}")
    v_display["pct_of_total"] = v_display["pct_of_total"].apply(lambda x: f"{x}%")
    v_display.columns = ["Rank","Vendor","Type","Market","Total Spend","% of Total","Productions"]
    st.dataframe(v_display, use_container_width=True, hide_index=True)

    st.info("📌 **SQL Insight:** VFX is the fastest growing spend category (+38% YoY). Top 3 vendors account for 58% of total EMEA spend — concentration risk flagged for UK market.")

# ── TAB 2: JOBS ──────────────────────────
with tab2:
    st.subheader("Employment Impact Across EMEA Markets")
    st.caption("All analysis powered by SQL — see /sql/05_jobs_by_market.sql")

    col1, col2 = st.columns(2)

    with col1:
        fig4 = go.Figure()
        for market in jobs_f["market"].unique():
            mdata = jobs_f[jobs_f["market"] == market]
            fig4.add_trace(go.Bar(
                name=market,
                x=mdata["year"].astype(str),
                y=mdata["total_jobs"]
            ))
        fig4.update_layout(
            barmode="group", title="Total Jobs by Market and Year",
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_title="Year", yaxis_title="Jobs"
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        jobs_market = jobs_f.groupby("market")[["direct_jobs","indirect_jobs"]].sum().reset_index()
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(name="Direct Jobs", x=jobs_market["market"], y=jobs_market["direct_jobs"], marker_color="#E50914"))
        fig5.add_trace(go.Bar(name="Indirect Jobs", x=jobs_market["market"], y=jobs_market["indirect_jobs"], marker_color="#888888"))
        fig5.update_layout(
            barmode="stack", title="Direct vs Indirect Jobs",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Cost Efficiency — Spend per Job by Market")
    eff = jobs_f.groupby("market").agg(
        total_spend=("total_spend","sum"),
        total_jobs=("total_jobs","sum")
    ).reset_index()
    eff["spend_per_job"] = (eff["total_spend"] / eff["total_jobs"]).round(0)
    eff = eff.sort_values("spend_per_job")
    fig6 = px.bar(
        eff, x="spend_per_job", y="market", orientation="h",
        title="Spend per Job Created (£) — Lower is more efficient",
        color="spend_per_job",
        color_continuous_scale=["#4CAF50","#FF9800","#E50914"],
        labels={"spend_per_job":"£ per Job","market":"Market"}
    )
    fig6.update_layout(plot_bgcolor="white", paper_bgcolor="white", coloraxis_showscale=False)
    st.plotly_chart(fig6, use_container_width=True)

    st.info("📌 **SQL Insight:** France generates the lowest spend per job created at £19,500 per role — making it Netflix's most cost-efficient EMEA market for employment impact reporting.")

# ── TAB 3: P&L ───────────────────────────
with tab3:
    st.subheader("Production P&L — Budget vs Actual")
    st.caption("All analysis powered by SQL — see /sql/03_production_pnl_variance.sql")

    col1, col2 = st.columns(2)

    with col1:
        colors = ["#E50914" if v else "#4CAF50" for v in pnl_f["is_over_budget"]]
        fig7 = go.Figure(go.Bar(
            x=pnl_f["variance_pct"],
            y=pnl_f["title"],
            orientation="h",
            marker_color=colors
        ))
        fig7.add_vline(x=0, line_dash="dash", line_color="black")
        fig7.update_layout(
            title="Variance % per Production",
            plot_bgcolor="white", paper_bgcolor="white",
            xaxis_ticksuffix="%", xaxis_title="Variance %"
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        st.subheader("Budget Risk by Genre")
        st.caption("SQL: /sql/06_genre_budget_adherence.sql")
        colors_genre = {"High Risk":"#E50914","Medium Risk":"#FF9800","Low Risk":"#4CAF50"}
        fig8 = px.bar(
            genre, x="avg_variance_pct", y="genre", orientation="h",
            title="Avg Variance % by Genre",
            color="risk_level",
            color_discrete_map=colors_genre,
            labels={"avg_variance_pct":"Avg Variance %","genre":"Genre"}
        )
        fig8.add_vline(x=0, line_dash="dash", line_color="black")
        fig8.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig8, use_container_width=True)

    st.subheader("Full P&L Table")
    pnl_display = pnl_f[["title","market","genre","year","quarter","budget_gbp","actual_spend_gbp","variance_gbp","variance_pct","budget_status","status"]].copy()
    pnl_display["budget_gbp"]       = pnl_display["budget_gbp"].apply(lambda x: f"£{x:,.0f}")
    pnl_display["actual_spend_gbp"] = pnl_display["actual_spend_gbp"].apply(lambda x: f"£{x:,.0f}")
    pnl_display["variance_gbp"]     = pnl_display["variance_gbp"].apply(lambda x: f"+£{x:,.0f}" if x > 0 else f"-£{abs(x):,.0f}")
    pnl_display["variance_pct"]     = pnl_display["variance_pct"].apply(lambda x: f"+{x}%" if x > 0 else f"{x}%")
    pnl_display.columns = ["Production","Market","Genre","Year","Quarter","Budget","Actual","Variance £","Variance %","Status","Production Status"]
    st.dataframe(pnl_display, use_container_width=True, hide_index=True)

    st.info("📌 **SQL Insight:** Sci-Fi and Fantasy genres show the highest budget overrun rate at 100% of productions exceeding budget — driven by VFX cost escalation. Drama shows strongest budget adherence at 67% on or under budget.")

# ── TAB 4: EXECUTIVE SUMMARY ─────────────
with tab4:
    st.subheader("EMEA Executive Summary")
    st.caption("All analysis powered by SQL — see /sql/08_executive_summary.sql")

    def health_badge(h):
        if h == "GREEN": return "🟢 On Track"
        if h == "AMBER": return "🟡 Monitor"
        return "🔴 Action Required"

    exec_display = exec_f.copy()
    exec_display["health"] = exec_display["health"].apply(health_badge)
    exec_display["total_budget"]  = exec_display["total_budget"].apply(lambda x: f"£{x/1e6:.1f}M")
    exec_display["total_actual"]  = exec_display["total_actual"].apply(lambda x: f"£{x/1e6:.1f}M")
    exec_display["avg_variance_pct"] = exec_display["avg_variance_pct"].apply(lambda x: f"+{x}%" if x > 0 else f"{x}%")
    exec_display["total_jobs"]    = exec_display["total_jobs"].apply(lambda x: f"{int(x):,}")
    exec_display.columns = ["Market","Year","Productions","Budget","Actual","Avg Variance","Total Jobs","Health"]
    st.dataframe(exec_display, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        health_counts = exec_f["health"].value_counts().reset_index()
        fig9 = px.pie(
            health_counts, values="count", names="health",
            title="Market Health Distribution",
            color="health",
            color_discrete_map={"GREEN":"#4CAF50","AMBER":"#FF9800","RED":"#E50914"},
            hole=0.5
        )
        fig9.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig9, use_container_width=True)

    with col2:
        fig10 = px.scatter(
            exec_f,
            x="total_actual", y="total_jobs",
            size="productions", color="market",
            title="Spend vs Jobs Created by Market",
            color_discrete_sequence=["#E50914","#B20710","#FF6B6B","#888888","#FFCCCC"],
            labels={"total_actual":"Total Spend (£)","total_jobs":"Total Jobs","market":"Market"}
        )
        fig10.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig10, use_container_width=True)

    st.info("📌 **SQL Insight:** United Kingdom represents 58% of total EMEA production spend but generates 62% of all jobs created — the highest return on investment of any EMEA market. Germany shows AMBER health due to 1899 S2 and Babylon Berlin S5 running over budget.")

st.markdown("---")
st.caption("Netflix EMEA Production Finance · SQL + Python Analysis · Pranav Rao Balguri · [pranavbalguri.github.io](https://pranavbalguri.github.io)")
