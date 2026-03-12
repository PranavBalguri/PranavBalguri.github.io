import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Financial Reporting Pipeline",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e0e0e0;
    }
    .risk-high { color: #A32D2D; font-weight: bold; }
    .risk-medium { color: #854F0B; font-weight: bold; }
    .risk-low { color: #3B6D11; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

DB_PATH = "./finance.duckdb"

@st.cache_data
def load_data():
    con = duckdb.connect(DB_PATH, read_only=True)

    pnl = con.execute("""
        SELECT * FROM main_marts.fct_daily_pnl
        ORDER BY transaction_date
    """).df()

    fraud = con.execute("""
        SELECT * FROM main_marts.fct_fraud_indicators
        ORDER BY fraud_risk_score DESC
    """).df()

    accounts = con.execute("""
        SELECT * FROM main_marts.dim_accounts
        ORDER BY lifetime_volume DESC
    """).df()

    transactions = con.execute("""
        SELECT * FROM main_staging.stg_transactions
        ORDER BY transaction_date
    """).df()

    con.close()
    return pnl, fraud, accounts, transactions

try:
    pnl_df, fraud_df, accounts_df, txn_df = load_data()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"Could not connect to DuckDB. Have you run `dbt seed` and `dbt run` first? Error: {e}")
    st.stop()

st.title("💰 Financial Reporting Pipeline")
st.caption("Built with dbt Core + DuckDB | by Pranav Rao Balguri")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

total_volume = txn_df['amount_abs'].sum()
total_revenue = pnl_df['estimated_revenue'].sum()
high_risk = len(fraud_df[fraud_df['fraud_risk_score'] >= 60])
total_txns = len(txn_df)

with col1:
    st.metric("Total Volume", f"£{total_volume:,.0f}", f"{total_txns} transactions")
with col2:
    st.metric("Estimated Revenue", f"£{total_revenue:,.0f}", "Fees + interest")
with col3:
    st.metric("High Risk Accounts", f"{high_risk}", "Referred to fraud team")
with col4:
    completed = len(txn_df[txn_df['status'] == 'completed'])
    st.metric("Completed Transactions", f"{completed}", f"of {total_txns} total")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 P&L Analysis",
    "🚨 Fraud Risk",
    "👤 Accounts",
    "📋 Raw Transactions"
])

with tab1:
    st.subheader("Daily P&L by Business Line")

    col1, col2 = st.columns([2, 1])

    with col1:
        pnl_chart = pnl_df.groupby(
            ['transaction_date', 'business_line']
        )['estimated_revenue'].sum().reset_index()

        fig = px.bar(
            pnl_chart,
            x='transaction_date',
            y='estimated_revenue',
            color='business_line',
            title='Daily Estimated Revenue by Business Line',
            labels={
                'estimated_revenue': 'Revenue (£)',
                'transaction_date': 'Date',
                'business_line': 'Business Line'
            },
            color_discrete_map={
                'wealth_management': '#185FA5',
                'lending': '#1D9E75',
                'retail_banking': '#888780'
            }
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend_title='Business Line'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        flow_data = txn_df.groupby('flow_direction')['amount_abs'].sum().reset_index()
        fig2 = px.pie(
            flow_data,
            values='amount_abs',
            names='flow_direction',
            title='Inflows vs Outflows',
            color_discrete_map={
                'inflow': '#185FA5',
                'outflow': '#E24B4A'
            },
            hole=0.6
        )
        fig2.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("P&L Summary Table")
    pnl_display = pnl_df[[
        'transaction_date', 'business_line', 'total_transactions',
        'gross_inflows', 'gross_outflows', 'net_position',
        'estimated_revenue', 'mtd_revenue'
    ]].copy()
    pnl_display.columns = [
        'Date', 'Business Line', 'Transactions',
        'Gross Inflows', 'Gross Outflows', 'Net Position',
        'Est. Revenue', 'MTD Revenue'
    ]
    for col in ['Gross Inflows', 'Gross Outflows', 'Net Position', 'Est. Revenue', 'MTD Revenue']:
        pnl_display[col] = pnl_display[col].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(pnl_display, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Fraud Risk Scoring — All Accounts")

    col1, col2, col3 = st.columns(3)
    with col1:
        high = len(fraud_df[fraud_df['fraud_risk_score'] >= 60])
        st.metric("HIGH Risk", high, "Refer to Fraud Team", delta_color="inverse")
    with col2:
        medium = len(fraud_df[(fraud_df['fraud_risk_score'] >= 30) & (fraud_df['fraud_risk_score'] < 60)])
        st.metric("MEDIUM Risk", medium, "Enhanced Monitoring", delta_color="off")
    with col3:
        low = len(fraud_df[fraud_df['fraud_risk_score'] < 30])
        st.metric("LOW Risk", low, "Standard Processing")

    fig3 = px.bar(
        fraud_df.sort_values('fraud_risk_score', ascending=True),
        x='fraud_risk_score',
        y='customer_name',
        orientation='h',
        title='Fraud Risk Score by Account',
        color='fraud_risk_score',
        color_continuous_scale=['#3B6D11', '#854F0B', '#A32D2D'],
        range_color=[0, 100],
        labels={
            'fraud_risk_score': 'Risk Score (0-100)',
            'customer_name': 'Customer'
        }
    )
    fig3.add_vline(x=60, line_dash="dash", line_color="#A32D2D",
                   annotation_text="High risk threshold (60)")
    fig3.add_vline(x=30, line_dash="dash", line_color="#854F0B",
                   annotation_text="Medium risk threshold (30)")
    fig3.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        coloraxis_showscale=False
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Detailed Fraud Indicators")
    fraud_display = fraud_df[[
        'account_id', 'customer_name', 'risk_tier',
        'flagged_transaction_count', 'near_threshold_count',
        'total_volume', 'fraud_risk_score', 'risk_band'
    ]].copy()
    fraud_display.columns = [
        'Account', 'Customer', 'Risk Tier',
        'Flagged Txns', 'Near Threshold',
        'Total Volume', 'Fraud Score', 'Risk Band'
    ]
    fraud_display['Total Volume'] = fraud_display['Total Volume'].apply(
        lambda x: f"£{x:,.0f}"
    )

    def colour_risk(val):
        if 'HIGH' in str(val):
            return 'background-color: #FCEBEB; color: #A32D2D; font-weight: bold'
        elif 'MEDIUM' in str(val):
            return 'background-color: #FAEEDA; color: #854F0B; font-weight: bold'
        elif 'LOW' in str(val):
            return 'background-color: #EAF3DE; color: #3B6D11; font-weight: bold'
        return ''

    styled = fraud_display.style.applymap(
        colour_risk, subset=['Risk Band']
    ).applymap(
        colour_risk, subset=['Risk Tier']
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Account Overview")

    fig4 = px.scatter(
        accounts_df,
        x='account_age_days',
        y='lifetime_volume',
        size='lifetime_transactions',
        color='risk_tier',
        hover_name='customer_name',
        title='Account Age vs Lifetime Volume (bubble size = transaction count)',
        color_discrete_map={
            'low': '#3B6D11',
            'medium': '#854F0B',
            'high': '#A32D2D'
        },
        labels={
            'account_age_days': 'Account Age (days)',
            'lifetime_volume': 'Lifetime Volume (£)',
            'risk_tier': 'Risk Tier'
        }
    )
    fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig4, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        eng_data = accounts_df['engagement_tier'].value_counts().reset_index()
        fig5 = px.pie(
            eng_data,
            values='count',
            names='engagement_tier',
            title='Account Engagement Tiers',
            color_discrete_sequence=['#185FA5', '#1D9E75', '#888780', '#E24B4A']
        )
        fig5.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        acc_display = accounts_df[[
            'account_id', 'customer_name', 'account_type',
            'risk_tier', 'lifetime_transactions',
            'lifetime_volume', 'engagement_tier'
        ]].copy()
        acc_display.columns = [
            'Account', 'Customer', 'Type',
            'Risk', 'Transactions', 'Volume', 'Engagement'
        ]
        acc_display['Volume'] = acc_display['Volume'].apply(lambda x: f"£{x:,.0f}")
        st.dataframe(acc_display, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Raw Transactions")

    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.multiselect(
            "Filter by status",
            options=txn_df['status'].unique().tolist(),
            default=txn_df['status'].unique().tolist()
        )
    with col2:
        bl_filter = st.multiselect(
            "Filter by business line",
            options=txn_df['business_line'].unique().tolist(),
            default=txn_df['business_line'].unique().tolist()
        )
    with col3:
        direction_filter = st.multiselect(
            "Filter by direction",
            options=txn_df['flow_direction'].unique().tolist(),
            default=txn_df['flow_direction'].unique().tolist()
        )

    filtered = txn_df[
        txn_df['status'].isin(status_filter) &
        txn_df['business_line'].isin(bl_filter) &
        txn_df['flow_direction'].isin(direction_filter)
    ]

    txn_display = filtered[[
        'transaction_id', 'account_id', 'transaction_date',
        'amount', 'transaction_type', 'status',
        'business_line', 'flow_direction', 'description'
    ]].copy()
    txn_display.columns = [
        'ID', 'Account', 'Date', 'Amount',
        'Type', 'Status', 'Business Line', 'Direction', 'Description'
    ]
    txn_display['Amount'] = txn_display['Amount'].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(txn_display, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(filtered)} of {len(txn_df)} transactions")

st.markdown("---")
st.caption("dbt Financial Reporting Pipeline | Pranav Rao Balguri | github.com/PranavBalguri")
