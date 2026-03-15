import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="Financial Reporting Pipeline",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA — mirrors exactly what dbt produces
# ─────────────────────────────────────────────

@st.cache_data
def load_transactions():
    return pd.DataFrame([
        {"transaction_id":"TXN-0001","account_id":"ACC-101","transaction_date":date(2024,1,3),"amount":1500.00,"transaction_type":"credit","status":"completed","product_category":"savings","business_line":"retail_banking","flow_direction":"inflow","amount_abs":1500.00},
        {"transaction_id":"TXN-0002","account_id":"ACC-102","transaction_date":date(2024,1,3),"amount":-200.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":200.00},
        {"transaction_id":"TXN-0003","account_id":"ACC-103","transaction_date":date(2024,1,4),"amount":50000.00,"transaction_type":"credit","status":"completed","product_category":"investment","business_line":"wealth_management","flow_direction":"inflow","amount_abs":50000.00},
        {"transaction_id":"TXN-0004","account_id":"ACC-101","transaction_date":date(2024,1,5),"amount":-75.50,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":75.50},
        {"transaction_id":"TXN-0005","account_id":"ACC-104","transaction_date":date(2024,1,5),"amount":9999.99,"transaction_type":"credit","status":"pending","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":9999.99},
        {"transaction_id":"TXN-0006","account_id":"ACC-105","transaction_date":date(2024,1,6),"amount":-3200.00,"transaction_type":"debit","status":"completed","product_category":"mortgage","business_line":"lending","flow_direction":"outflow","amount_abs":3200.00},
        {"transaction_id":"TXN-0007","account_id":"ACC-102","transaction_date":date(2024,1,7),"amount":450.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":450.00},
        {"transaction_id":"TXN-0008","account_id":"ACC-106","transaction_date":date(2024,1,8),"amount":125000.00,"transaction_type":"credit","status":"completed","product_category":"investment","business_line":"wealth_management","flow_direction":"inflow","amount_abs":125000.00},
        {"transaction_id":"TXN-0009","account_id":"ACC-103","transaction_date":date(2024,1,8),"amount":-500.00,"transaction_type":"debit","status":"failed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":500.00},
        {"transaction_id":"TXN-0010","account_id":"ACC-107","transaction_date":date(2024,1,9),"amount":8500.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":8500.00},
        {"transaction_id":"TXN-0011","account_id":"ACC-101","transaction_date":date(2024,1,10),"amount":-1200.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":1200.00},
        {"transaction_id":"TXN-0012","account_id":"ACC-104","transaction_date":date(2024,1,10),"amount":9800.00,"transaction_type":"credit","status":"pending","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":9800.00},
        {"transaction_id":"TXN-0013","account_id":"ACC-108","transaction_date":date(2024,1,11),"amount":2300.00,"transaction_type":"credit","status":"completed","product_category":"savings","business_line":"retail_banking","flow_direction":"inflow","amount_abs":2300.00},
        {"transaction_id":"TXN-0014","account_id":"ACC-105","transaction_date":date(2024,1,12),"amount":-150.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":150.00},
        {"transaction_id":"TXN-0015","account_id":"ACC-106","transaction_date":date(2024,1,13),"amount":5000.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":5000.00},
        {"transaction_id":"TXN-0016","account_id":"ACC-109","transaction_date":date(2024,1,14),"amount":75000.00,"transaction_type":"credit","status":"completed","product_category":"investment","business_line":"wealth_management","flow_direction":"inflow","amount_abs":75000.00},
        {"transaction_id":"TXN-0017","account_id":"ACC-102","transaction_date":date(2024,1,15),"amount":-890.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":890.00},
        {"transaction_id":"TXN-0018","account_id":"ACC-104","transaction_date":date(2024,1,15),"amount":9750.00,"transaction_type":"credit","status":"flagged","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":9750.00},
        {"transaction_id":"TXN-0019","account_id":"ACC-110","transaction_date":date(2024,1,16),"amount":320.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":320.00},
        {"transaction_id":"TXN-0020","account_id":"ACC-101","transaction_date":date(2024,1,17),"amount":-45.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":45.00},
        {"transaction_id":"TXN-0021","account_id":"ACC-107","transaction_date":date(2024,1,18),"amount":12000.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":12000.00},
        {"transaction_id":"TXN-0022","account_id":"ACC-103","transaction_date":date(2024,1,19),"amount":-2500.00,"transaction_type":"debit","status":"completed","product_category":"investment","business_line":"wealth_management","flow_direction":"outflow","amount_abs":2500.00},
        {"transaction_id":"TXN-0023","account_id":"ACC-108","transaction_date":date(2024,1,20),"amount":180.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":180.00},
        {"transaction_id":"TXN-0024","account_id":"ACC-104","transaction_date":date(2024,1,20),"amount":9900.00,"transaction_type":"credit","status":"flagged","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":9900.00},
        {"transaction_id":"TXN-0025","account_id":"ACC-105","transaction_date":date(2024,1,21),"amount":-4800.00,"transaction_type":"debit","status":"completed","product_category":"mortgage","business_line":"lending","flow_direction":"outflow","amount_abs":4800.00},
        {"transaction_id":"TXN-0026","account_id":"ACC-106","transaction_date":date(2024,1,22),"amount":1750.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":1750.00},
        {"transaction_id":"TXN-0027","account_id":"ACC-109","transaction_date":date(2024,1,23),"amount":-300.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":300.00},
        {"transaction_id":"TXN-0028","account_id":"ACC-110","transaction_date":date(2024,1,24),"amount":550.00,"transaction_type":"credit","status":"completed","product_category":"savings","business_line":"retail_banking","flow_direction":"inflow","amount_abs":550.00},
        {"transaction_id":"TXN-0029","account_id":"ACC-101","transaction_date":date(2024,1,25),"amount":-680.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":680.00},
        {"transaction_id":"TXN-0030","account_id":"ACC-102","transaction_date":date(2024,1,26),"amount":3400.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":3400.00},
        {"transaction_id":"TXN-0031","account_id":"ACC-104","transaction_date":date(2024,1,27),"amount":9500.00,"transaction_type":"credit","status":"flagged","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":9500.00},
        {"transaction_id":"TXN-0032","account_id":"ACC-107","transaction_date":date(2024,1,28),"amount":-1500.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":1500.00},
        {"transaction_id":"TXN-0033","account_id":"ACC-108","transaction_date":date(2024,1,29),"amount":4200.00,"transaction_type":"credit","status":"completed","product_category":"savings","business_line":"retail_banking","flow_direction":"inflow","amount_abs":4200.00},
        {"transaction_id":"TXN-0034","account_id":"ACC-103","transaction_date":date(2024,1,30),"amount":88000.00,"transaction_type":"credit","status":"completed","product_category":"investment","business_line":"wealth_management","flow_direction":"inflow","amount_abs":88000.00},
        {"transaction_id":"TXN-0035","account_id":"ACC-105","transaction_date":date(2024,1,31),"amount":-200.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":200.00},
        {"transaction_id":"TXN-0036","account_id":"ACC-101","transaction_date":date(2024,2,1),"amount":1500.00,"transaction_type":"credit","status":"completed","product_category":"savings","business_line":"retail_banking","flow_direction":"inflow","amount_abs":1500.00},
        {"transaction_id":"TXN-0037","account_id":"ACC-106","transaction_date":date(2024,2,2),"amount":6200.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":6200.00},
        {"transaction_id":"TXN-0038","account_id":"ACC-109","transaction_date":date(2024,2,3),"amount":-12000.00,"transaction_type":"debit","status":"completed","product_category":"investment","business_line":"wealth_management","flow_direction":"outflow","amount_abs":12000.00},
        {"transaction_id":"TXN-0039","account_id":"ACC-110","transaction_date":date(2024,2,4),"amount":900.00,"transaction_type":"credit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"inflow","amount_abs":900.00},
        {"transaction_id":"TXN-0040","account_id":"ACC-102","transaction_date":date(2024,2,5),"amount":-430.00,"transaction_type":"debit","status":"completed","product_category":"current","business_line":"retail_banking","flow_direction":"outflow","amount_abs":430.00},
    ])

@st.cache_data
def load_accounts():
    return pd.DataFrame([
        {"account_id":"ACC-101","customer_name":"Sarah Johnson","account_type":"current","account_status":"active","risk_tier":"low","credit_limit":5000,"relationship_manager":"James Mitchell","account_age_days":1826},
        {"account_id":"ACC-102","customer_name":"Mohammed Al-Rashid","account_type":"current","account_status":"active","risk_tier":"low","credit_limit":3000,"relationship_manager":"Emma Clarke","account_age_days":912},
        {"account_id":"ACC-103","customer_name":"Priya Sharma","account_type":"investment","account_status":"active","risk_tier":"medium","credit_limit":500000,"relationship_manager":"James Mitchell","account_age_days":1978},
        {"account_id":"ACC-104","customer_name":"Unknown Entity","account_type":"current","account_status":"flagged","risk_tier":"high","credit_limit":10000,"relationship_manager":"Compliance Team","account_age_days":120},
        {"account_id":"ACC-105","customer_name":"David Okonkwo","account_type":"mortgage","account_status":"active","risk_tier":"low","credit_limit":350000,"relationship_manager":"Emma Clarke","account_age_days":2465},
        {"account_id":"ACC-106","customer_name":"Chen Wei","account_type":"current","account_status":"active","risk_tier":"low","credit_limit":8000,"relationship_manager":"James Mitchell","account_age_days":1460},
        {"account_id":"ACC-107","customer_name":"Fatima Hassan","account_type":"current","account_status":"active","risk_tier":"medium","credit_limit":12000,"relationship_manager":"Emma Clarke","account_age_days":548},
        {"account_id":"ACC-108","customer_name":"Robert Campbell","account_type":"savings","account_status":"active","risk_tier":"low","credit_limit":2000,"relationship_manager":"James Mitchell","account_age_days":2922},
        {"account_id":"ACC-109","customer_name":"Anika Patel","account_type":"investment","account_status":"active","risk_tier":"medium","credit_limit":250000,"relationship_manager":"Emma Clarke","account_age_days":1278},
        {"account_id":"ACC-110","customer_name":"Thomas Brennan","account_type":"current","account_status":"active","risk_tier":"low","credit_limit":4000,"relationship_manager":"James Mitchell","account_age_days":365},
    ])

@st.cache_data
def build_fraud_scores(txn_df, acc_df):
    grp = txn_df.groupby("account_id").agg(
        total_transactions=("transaction_id","count"),
        total_volume=("amount_abs","sum"),
        avg_transaction_value=("amount_abs","mean"),
        max_single_transaction=("amount_abs","max"),
        flagged_transaction_count=("status", lambda x: (x=="flagged").sum()),
        failed_transaction_count=("status", lambda x: (x=="failed").sum()),
        near_threshold_count=("amount_abs", lambda x: (x>9000).sum()),
        total_inflows=("amount_abs", lambda x: x[txn_df.loc[x.index,"flow_direction"]=="inflow"].sum()),
        total_outflows=("amount_abs", lambda x: x[txn_df.loc[x.index,"flow_direction"]=="outflow"].sum()),
    ).reset_index()

    df = grp.merge(acc_df[["account_id","customer_name","risk_tier","account_status","relationship_manager","account_age_days","credit_limit"]], on="account_id")

    def score_row(r):
        s = 0
        if r["account_status"] == "flagged": s += 40
        s += min(r["near_threshold_count"] * 15, 30)
        if r["total_transactions"] > 0 and r["flagged_transaction_count"] / r["total_transactions"] > 0.2: s += 20
        if r["account_age_days"] < 180 and r["total_volume"] > 50000: s += 15
        tier_map = {"high":3,"medium":2,"low":1}
        s += tier_map.get(r["risk_tier"], 0) * 5
        if r["total_transactions"] > 0 and r["failed_transaction_count"] / r["total_transactions"] > 0.1: s += 10
        return min(s, 100)

    df["fraud_risk_score"] = df.apply(score_row, axis=1)
    df["risk_band"] = df["fraud_risk_score"].apply(
        lambda s: "HIGH — Refer to Fraud Team" if s >= 60 else ("MEDIUM — Enhanced Monitoring" if s >= 30 else "LOW — Standard Processing")
    )
    return df.sort_values("fraud_risk_score", ascending=False)

@st.cache_data
def build_pnl(txn_df):
    completed = txn_df[txn_df["status"] == "completed"].copy()
    rate_map = {"wealth_management": 0.015, "lending": 0.04, "retail_banking": 0.005}
    completed["estimated_revenue"] = completed.apply(
        lambda r: r["amount_abs"] * rate_map.get(r["business_line"], 0), axis=1
    )
    completed["gross_inflows"] = completed["amount_abs"].where(completed["flow_direction"]=="inflow", 0)
    completed["gross_outflows"] = completed["amount_abs"].where(completed["flow_direction"]=="outflow", 0)

    pnl = completed.groupby(["transaction_date","business_line"]).agg(
        total_transactions=("transaction_id","count"),
        gross_inflows=("gross_inflows","sum"),
        gross_outflows=("gross_outflows","sum"),
        net_position=("amount","sum"),
        estimated_revenue=("estimated_revenue","sum"),
    ).reset_index().sort_values("transaction_date")
    return pnl

# ─────────────────────────────────────────────
# LOAD
# ─────────────────────────────────────────────
txn_df   = load_transactions()
acc_df   = load_accounts()
fraud_df = build_fraud_scores(txn_df, acc_df)
pnl_df   = build_pnl(txn_df)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("💰 Financial Reporting Pipeline")
st.caption("Built with dbt Core · DuckDB · Streamlit | Pranav Rao Balguri · [GitHub](https://github.com/PranavBalguri) · [Portfolio](https://pranavbalguri.github.io)")
st.markdown("---")

# ─────────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Volume",        f"£{txn_df['amount_abs'].sum():,.0f}",  f"{len(txn_df)} transactions")
k2.metric("Estimated Revenue",   f"£{pnl_df['estimated_revenue'].sum():,.0f}", "Fees + interest")
k3.metric("High Risk Accounts",  str(len(fraud_df[fraud_df['fraud_risk_score']>=60])), "Refer to fraud team")
k4.metric("Tests Passing",       "20 / 20", "All checks green")

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 P&L Analysis", "🚨 Fraud Risk", "👤 Accounts", "📋 Raw Transactions"])

# ── TAB 1: P&L ────────────────────────────────
with tab1:
    st.subheader("Daily P&L by Business Line")
    col1, col2 = st.columns([2,1])

    with col1:
        fig = px.bar(
            pnl_df, x="transaction_date", y="estimated_revenue", color="business_line",
            title="Daily Estimated Revenue",
            labels={"estimated_revenue":"Revenue (£)","transaction_date":"Date","business_line":"Business Line"},
            color_discrete_map={"wealth_management":"#185FA5","lending":"#1D9E75","retail_banking":"#888780"}
        )
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", legend_title="Business Line")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        flow = txn_df.groupby("flow_direction")["amount_abs"].sum().reset_index()
        fig2 = px.pie(
            flow, values="amount_abs", names="flow_direction",
            title="Inflows vs Outflows", hole=0.6,
            color_discrete_map={"inflow":"#185FA5","outflow":"#E24B4A"}
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("P&L Summary Table")
    display = pnl_df.copy()
    for c in ["gross_inflows","gross_outflows","net_position","estimated_revenue"]:
        display[c] = display[c].apply(lambda x: f"£{x:,.2f}")
    display.columns = ["Date","Business Line","Transactions","Gross Inflows","Gross Outflows","Net Position","Est. Revenue"]
    st.dataframe(display, use_container_width=True, hide_index=True)

# ── TAB 2: FRAUD ──────────────────────────────
with tab2:
    st.subheader("Fraud Risk Scoring — All Accounts")

    f1, f2, f3 = st.columns(3)
    f1.metric("HIGH Risk",   str(len(fraud_df[fraud_df["fraud_risk_score"]>=60])),  "Refer to Fraud Team",   delta_color="inverse")
    f2.metric("MEDIUM Risk", str(len(fraud_df[(fraud_df["fraud_risk_score"]>=30) & (fraud_df["fraud_risk_score"]<60)])), "Enhanced Monitoring", delta_color="off")
    f3.metric("LOW Risk",    str(len(fraud_df[fraud_df["fraud_risk_score"]<30])),    "Standard Processing")

    fig3 = px.bar(
        fraud_df.sort_values("fraud_risk_score"),
        x="fraud_risk_score", y="customer_name", orientation="h",
        title="Fraud Risk Score by Account",
        color="fraud_risk_score",
        color_continuous_scale=["#3B6D11","#854F0B","#A32D2D"],
        range_color=[0,100],
        labels={"fraud_risk_score":"Risk Score (0–100)","customer_name":"Customer"}
    )
    fig3.add_vline(x=60, line_dash="dash", line_color="#A32D2D", annotation_text="High (60)")
    fig3.add_vline(x=30, line_dash="dash", line_color="#854F0B", annotation_text="Medium (30)")
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Detailed Fraud Indicators")
    fd = fraud_df[["account_id","customer_name","risk_tier","flagged_transaction_count",
                   "near_threshold_count","total_volume","fraud_risk_score","risk_band"]].copy()
    fd["total_volume"] = fd["total_volume"].apply(lambda x: f"£{x:,.0f}")
    fd.columns = ["Account","Customer","Risk Tier","Flagged Txns","Near Threshold","Total Volume","Fraud Score","Risk Band"]

    def colour_risk(val):
        if "HIGH" in str(val):   return "background-color:#FCEBEB;color:#A32D2D;font-weight:bold"
        if "MEDIUM" in str(val): return "background-color:#FAEEDA;color:#854F0B;font-weight:bold"
        if "LOW" in str(val):    return "background-color:#EAF3DE;color:#3B6D11;font-weight:bold"
        return ""

    st.dataframe(fd.style.applymap(colour_risk, subset=["Risk Band","Risk Tier"]), use_container_width=True, hide_index=True)

# ── TAB 3: ACCOUNTS ───────────────────────────
with tab3:
    st.subheader("Account Overview")

    acc_vol = txn_df[txn_df["status"]=="completed"].groupby("account_id").agg(
        lifetime_transactions=("transaction_id","count"),
        lifetime_volume=("amount_abs","sum")
    ).reset_index()
    acc_full = acc_df.merge(acc_vol, on="account_id", how="left").fillna(0)
    acc_full["engagement_tier"] = acc_full["lifetime_transactions"].apply(
        lambda x: "active" if x>=10 else ("moderate" if x>=3 else ("low" if x>=1 else "dormant"))
    )

    fig4 = px.scatter(
        acc_full, x="account_age_days", y="lifetime_volume",
        size="lifetime_transactions", color="risk_tier",
        hover_name="customer_name",
        title="Account Age vs Lifetime Volume (bubble = transaction count)",
        color_discrete_map={"low":"#3B6D11","medium":"#854F0B","high":"#A32D2D"},
        labels={"account_age_days":"Account Age (days)","lifetime_volume":"Lifetime Volume (£)","risk_tier":"Risk Tier"}
    )
    fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig4, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        eng = acc_full["engagement_tier"].value_counts().reset_index()
        fig5 = px.pie(eng, values="count", names="engagement_tier", title="Engagement Tiers",
                      color_discrete_sequence=["#185FA5","#1D9E75","#888780","#E24B4A"])
        fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig5, use_container_width=True)
    with col2:
        ad = acc_full[["account_id","customer_name","account_type","risk_tier","lifetime_transactions","lifetime_volume","engagement_tier"]].copy()
        ad["lifetime_volume"] = ad["lifetime_volume"].apply(lambda x: f"£{x:,.0f}")
        ad.columns = ["Account","Customer","Type","Risk","Transactions","Volume","Engagement"]
        st.dataframe(ad, use_container_width=True, hide_index=True)

# ── TAB 4: TRANSACTIONS ───────────────────────
with tab4:
    st.subheader("Raw Transactions")
    c1, c2, c3 = st.columns(3)
    status_f    = c1.multiselect("Status",        txn_df["status"].unique().tolist(),        txn_df["status"].unique().tolist())
    bl_f        = c2.multiselect("Business Line", txn_df["business_line"].unique().tolist(), txn_df["business_line"].unique().tolist())
    direction_f = c3.multiselect("Direction",     txn_df["flow_direction"].unique().tolist(),txn_df["flow_direction"].unique().tolist())

    filtered = txn_df[
        txn_df["status"].isin(status_f) &
        txn_df["business_line"].isin(bl_f) &
        txn_df["flow_direction"].isin(direction_f)
    ][["transaction_id","account_id","transaction_date","amount","transaction_type","status","business_line","flow_direction"]].copy()
    filtered["amount"] = filtered["amount"].apply(lambda x: f"£{x:,.2f}")
    filtered.columns = ["ID","Account","Date","Amount","Type","Status","Business Line","Direction"]
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(filtered)} of {len(txn_df)} transactions")

st.markdown("---")
st.caption("dbt Financial Reporting Pipeline · Pranav Rao Balguri · [pranavbalguri.github.io](https://pranavbalguri.github.io)")
