import streamlit as st
import pandas as pd
from datetime import datetime, date
import anthropic
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Security Master DQ Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0d1117; }
    .stApp { background: #0d1117; color: #e6edf3; }

    section[data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
    }

    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
    }
    [data-testid="metric-container"] label { color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e6edf3; font-size: 28px; font-weight: 700; }

    .section-header {
        font-size: 13px;
        font-weight: 600;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #21262d;
    }

    .stButton > button {
        background: #238636;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #30363d; }
    .stTabs [data-baseweb="tab"] { color: #8b949e; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #e6edf3 !important; border-bottom: 2px solid #388bfd !important; }

    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        border-radius: 6px !important;
    }
    .stTextArea textarea {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }

    .chat-sql {
        background: #0d1117;
        border: 1px solid #388bfd33;
        border-left: 3px solid #388bfd;
        border-radius: 4px;
        padding: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #79c0ff;
        margin: 8px 0;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    securities = pd.read_csv("security-master-dq/data/security_master.csv")
    corporate_actions = pd.read_csv("security-master-dq/data/corporate_actions.csv")
    exceptions = pd.read_csv("security-master-dq/data/exceptions.csv")
    return securities, corporate_actions, exceptions

securities, corporate_actions, exceptions_df = load_data()

if "exceptions" not in st.session_state:
    st.session_state.exceptions = exceptions_df.copy()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── DQ logic ──────────────────────────────────────────────────────────────────
def detect_exceptions(sec_df):
    issues = []
    valid_currencies = ["USD","GBP","EUR","JPY","CHF","AUD","CAD","SGD","HKD","SEK","NOK","DKK"]

    for _, row in sec_df.iterrows():
        sid = row["security_id"]
        if row["asset_class"] == "Equity" and (pd.isna(row["isin"]) or str(row["isin"]).strip() == ""):
            issues.append({"security_id": sid, "type": "Missing ISIN", "severity": "High"})
        if pd.isna(row["currency"]) or str(row["currency"]).strip() == "":
            issues.append({"security_id": sid, "type": "Missing Currency", "severity": "High"})
        if not pd.isna(row["currency"]) and str(row["currency"]).strip() not in valid_currencies:
            issues.append({"security_id": sid, "type": "Invalid Currency", "severity": "High"})
        if pd.isna(row["ticker"]) or str(row["ticker"]).strip() == "":
            issues.append({"security_id": sid, "type": "Missing Ticker", "severity": "Medium"})
        try:
            last_upd = datetime.strptime(str(row["last_updated"]), "%Y-%m-%d")
            if (datetime(2024, 1, 15) - last_upd).days > 30:
                issues.append({"security_id": sid, "type": "Stale Price", "severity": "Medium"})
        except:
            pass
        if str(row.get("data_source","")).strip() == "Manual":
            issues.append({"security_id": sid, "type": "Manual Data Source", "severity": "Medium"})

    return pd.DataFrame(issues) if issues else pd.DataFrame(columns=["security_id","type","severity"])


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏦 Security Master DQ")
    st.markdown("<div style='color:#8b949e;font-size:12px;margin-bottom:16px'>Reference Data Operations Dashboard</div>", unsafe_allow_html=True)
    st.markdown("---")

    asset_filter = st.multiselect("Asset Class", options=["Equity","Bond"], default=["Equity","Bond"])
    status_filter = st.multiselect("Status", options=["Active","Inactive"], default=["Active","Inactive"])
    sev_filter = st.multiselect("Severity", options=["Critical","High","Medium","Low"], default=["Critical","High","Medium","Low"])

    st.markdown("---")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.caption("Required for AI Query Assistant tab")

    st.markdown("---")
    st.markdown("<div style='color:#8b949e;font-size:11px'>Built by Pranav Balguri<br>RaKiTics · 2024<br>Stack: Python · Streamlit · Claude API</div>", unsafe_allow_html=True)


# ── Filters ────────────────────────────────────────────────────────────────────
filtered_sec = securities[
    (securities["asset_class"].isin(asset_filter)) &
    (securities["status"].isin(status_filter))
]

live_exceptions = detect_exceptions(filtered_sec)
open_exceptions = st.session_state.exceptions[
    (st.session_state.exceptions["status"] == "Open") &
    (st.session_state.exceptions["severity"].isin(sev_filter))
]


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# Security Master Data Quality")
st.markdown("<div style='color:#8b949e;font-size:14px;margin-bottom:24px'>Reference data governance · Hedge fund demo · Pranav Balguri</div>", unsafe_allow_html=True)


# ── KPIs ───────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total = len(filtered_sec)
exc_open = len(open_exceptions)
critical = len(open_exceptions[open_exceptions["severity"] == "Critical"]) if exc_open else 0
high_sev = len(open_exceptions[open_exceptions["severity"] == "High"]) if exc_open else 0
live_issues = len(live_exceptions)
clean_pct = round((1 - live_issues / max(total, 1)) * 100, 1)

k1.metric("Total Securities", total)
k2.metric("Open Exceptions", exc_open)
k3.metric("High / Critical", f"{critical + high_sev}")
k4.metric("Live DQ Issues", live_issues)
k5.metric("Data Quality Score", f"{clean_pct}%")


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📋 Security Master", "⚠️ Exception Manager", "📅 Corporate Actions", "🤖 AI Query Assistant"])


# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Security Master — All Instruments</div>', unsafe_allow_html=True)

    search = st.text_input("🔍 Search by name, ticker, ISIN or security ID", placeholder="e.g. Apple, AAPL, US0378331005")
    if search:
        mask = filtered_sec.apply(lambda r: search.lower() in str(r).lower(), axis=1)
        display_sec = filtered_sec[mask]
    else:
        display_sec = filtered_sec

    issue_ids = live_exceptions["security_id"].unique() if not live_exceptions.empty else []

    def highlight_issues(row):
        if row["security_id"] in issue_ids:
            return ["background-color: #2d1f0d; color: #e3a139"] * len(row)
        return [""] * len(row)

    cols_show = ["security_id","name","asset_class","isin","ticker","currency","exchange","country","status","last_updated","price","data_source"]
    st.dataframe(
        display_sec[cols_show].style.apply(highlight_issues, axis=1),
        use_container_width=True,
        height=420,
    )
    st.caption(f"🟡 Highlighted rows have active data quality issues · {len(issue_ids)} securities flagged")

    if not live_exceptions.empty:
        st.markdown('<div class="section-header">Live Data Quality Breakdown</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Issues by Type**")
            st.dataframe(live_exceptions.groupby("type").size().reset_index(name="count").sort_values("count", ascending=False), use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**Issues by Severity**")
            st.dataframe(live_exceptions.groupby("severity").size().reset_index(name="count"), use_container_width=True, hide_index=True)


# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Open Exceptions — Investigation & Resolution</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2,1])
    with c1:
        exc_type_filter = st.multiselect("Filter by Exception Type", options=st.session_state.exceptions["exception_type"].unique().tolist(), default=[])
    with c2:
        show_resolved = st.checkbox("Show Resolved", value=False)

    exc_display = st.session_state.exceptions.copy()
    if not show_resolved:
        exc_display = exc_display[exc_display["status"] == "Open"]
    if sev_filter:
        exc_display = exc_display[exc_display["severity"].isin(sev_filter)]
    if exc_type_filter:
        exc_display = exc_display[exc_display["exception_type"].isin(exc_type_filter)]

    for _, row in exc_display.iterrows():
        icon = "🔴" if row["severity"]=="Critical" else "🟠" if row["severity"]=="High" else "🟡" if row["severity"]=="Medium" else "🔵"
        with st.expander(f"{icon} {row['exception_id']} · {row['exception_type']} · {row['security_id']}"):
            dc1, dc2, dc3 = st.columns(3)
            dc1.markdown(f"**Security ID:** `{row['security_id']}`")
            dc2.markdown(f"**Severity:** {row['severity']}")
            dc3.markdown(f"**Status:** `{row['status']}`")
            st.markdown(f"**Description:** {row['description']}")
            if not pd.isna(row.get("notes","")):
                st.markdown(f"**Notes:** {row['notes']}")

            if row["status"] == "Open":
                with st.form(f"resolve_{row['exception_id']}"):
                    resolution_note = st.text_area("Resolution notes")
                    resolved_by = st.text_input("Resolved by", value="Pranav B")
                    if st.form_submit_button("✅ Mark as Resolved"):
                        idx = st.session_state.exceptions[st.session_state.exceptions["exception_id"] == row["exception_id"]].index[0]
                        st.session_state.exceptions.at[idx, "status"] = "Resolved"
                        st.session_state.exceptions.at[idx, "resolved_date"] = date.today().strftime("%Y-%m-%d")
                        st.session_state.exceptions.at[idx, "resolved_by"] = resolved_by
                        st.session_state.exceptions.at[idx, "notes"] = resolution_note
                        st.success(f"Exception {row['exception_id']} resolved!")
                        st.rerun()


# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Corporate Actions — Pending & Processed</div>', unsafe_allow_html=True)

    ca_status = st.radio("Filter by status", ["All","Pending","Processed"], horizontal=True)
    ca_display = corporate_actions if ca_status == "All" else corporate_actions[corporate_actions["status"] == ca_status]
    ca_merged = ca_display.merge(securities[["security_id","name","asset_class"]], on="security_id", how="left")

    m1, m2, m3 = st.columns(3)
    m1.metric("Pending Actions", len(corporate_actions[corporate_actions["status"]=="Pending"]))
    m2.metric("Processed", len(corporate_actions[corporate_actions["status"]=="Processed"]))
    m3.metric("Unprocessed Splits ⚠️", len(corporate_actions[(corporate_actions["action_type"]=="Stock Split") & (corporate_actions["status"]=="Pending")]))

    st.dataframe(
        ca_merged[["action_id","security_id","name","action_type","announcement_date","effective_date","status","cash_amount","ratio","currency","processed"]],
        use_container_width=True,
        height=380,
    )

    st.markdown('<div class="section-header">⚠️ Upcoming Actions Requiring Attention</div>', unsafe_allow_html=True)
    for _, row in ca_merged[ca_merged["status"]=="Pending"].iterrows():
        if not pd.isna(row["effective_date"]):
            st.markdown(f"- **{row['name']}** · `{row['action_type']}` · Effective: `{row['effective_date']}` · Processed: `{row['processed']}`")


# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">AI-Powered Natural Language Query</div>', unsafe_allow_html=True)
    st.markdown("<div style='color:#8b949e;font-size:13px;margin-bottom:16px'>Ask questions about the security master in plain English. Claude converts them to pandas code and runs against the dataset.</div>", unsafe_allow_html=True)

    schema_context = """
You are a data analyst assistant for a hedge fund reference data team.
You have access to three pandas DataFrames:

1. `securities` - Security Master
   Columns: security_id, name, asset_class, isin, cusip, ticker, currency, exchange, country, sector, maturity_date, coupon_rate, par_value, status, last_updated, price, data_source

2. `corporate_actions` - Corporate Actions
   Columns: action_id, security_id, ticker, action_type, announcement_date, effective_date, status, details, cash_amount, ratio, currency, processed

3. `exceptions_df` - Data Quality Exceptions
   Columns: exception_id, security_id, exception_type, severity, description, detected_date, status, resolved_date, resolved_by, notes

Respond ONLY with JSON in this exact format, no markdown, no preamble:
{
  "explanation": "Plain English explanation of what the query does",
  "pandas_code": "A single pandas expression that returns a DataFrame or Series. Use variable names: securities, corporate_actions, exceptions_df",
  "insight": "Key finding or data quality observation"
}
"""

    example_queries = [
        "Show all equities missing an ISIN",
        "Which securities have stale prices?",
        "List all pending unprocessed corporate actions",
        "Show bonds by currency with average price",
        "Which securities use Manual as their data source?",
        "Show open exceptions by severity",
    ]

    st.markdown("**Example queries:**")
    eq_cols = st.columns(3)
    for i, q in enumerate(example_queries):
        if eq_cols[i % 3].button(q, key=f"eq_{i}"):
            st.session_state["prefill_query"] = q

    prefill = st.session_state.pop("prefill_query", "")
    user_query = st.text_input("Ask a question about the data", value=prefill, placeholder="e.g. Show me all high severity open exceptions")

    if st.button("🔍 Run Query") and user_query:
        if not api_key:
            st.warning("Please enter your Anthropic API key in the sidebar to use AI queries.")
        else:
            with st.spinner("Claude is analysing the data..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1000,
                        system=schema_context,
                        messages=[{"role": "user", "content": user_query}]
                    )
                    raw = message.content[0].text.strip()
                    result = json.loads(raw)

                    st.session_state.chat_history.append({
                        "query": user_query,
                        "code": result.get("pandas_code",""),
                        "insight": result.get("insight",""),
                    })

                    local_vars = {"securities": securities, "corporate_actions": corporate_actions, "exceptions_df": st.session_state.exceptions}
                    exec_result = eval(result["pandas_code"], {}, local_vars)

                    st.markdown(f"**Explanation:** {result['explanation']}")
                    st.markdown('<div class="chat-sql">' + result["pandas_code"] + '</div>', unsafe_allow_html=True)
                    st.markdown(f"💡 **Insight:** {result['insight']}")
                    st.dataframe(exec_result if isinstance(exec_result, pd.DataFrame) else exec_result.to_frame(), use_container_width=True)

                except json.JSONDecodeError:
                    st.error("Could not parse Claude's response. Try rephrasing your question.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.chat_history:
        st.markdown('<div class="section-header">Query History</div>', unsafe_allow_html=True)
        for h in reversed(st.session_state.chat_history[-5:]):
            with st.expander(f"Q: {h['query']}"):
                st.markdown(f"**Code:** `{h['code']}`")
                st.markdown(f"**Insight:** {h['insight']}")
