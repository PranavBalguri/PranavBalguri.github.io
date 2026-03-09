"""
app.py - Streamlit Dashboard for UK National Lottery Predictor
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from data_loader import load_lottery_data, get_ball_frequencies, get_last_seen, get_pair_cooccurrence
from model import frequency_based_picks, monte_carlo_simulate, build_features, train_models, predict_next_draw

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎱 UK Lottery Predictor",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] { font-family: 'Share Tech Mono', monospace; }
h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; }

.main { background: #0d0f1a; }
.block-container { padding-top: 1.5rem; }

.ball {
    display: inline-flex; align-items: center; justify-content: center;
    width: 48px; height: 48px; border-radius: 50%;
    font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 15px;
    margin: 4px; box-shadow: 0 0 14px rgba(247,201,72,0.5);
    background: radial-gradient(circle at 35% 35%, #f7c948, #c49a00);
    color: #1a1200;
}
.ball-blue {
    background: radial-gradient(circle at 35% 35%, #3ae4c1, #1a8a74);
    color: #001a14; box-shadow: 0 0 14px rgba(58,228,193,0.5);
}
.ball-red {
    background: radial-gradient(circle at 35% 35%, #ff6b6b, #cc1a1a);
    color: #fff; box-shadow: 0 0 14px rgba(255,107,107,0.5);
}
.metric-card {
    background: linear-gradient(135deg, #12142a, #1a1c35);
    border: 1px solid #2a2d50; border-radius: 12px;
    padding: 16px 20px; text-align: center;
}
.stTabs [data-baseweb="tab"] { font-family: 'Orbitron', sans-serif; font-size: 12px; }
.disclaimer {
    background: #1a0d0d; border: 1px solid #ff6b6b44;
    border-radius: 8px; padding: 10px 16px; font-size: 12px; color: #ff9999;
}
</style>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    uploaded = None
    return load_lottery_data("lotto_results.csv"), None

@st.cache_data
def get_freq(df_hash):
    df = st.session_state.df
    return get_ball_frequencies(df)

@st.cache_resource
def train(_df_len):
    df = st.session_state.df
    return train_models(df, lookback=10)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎱 UK Lottery Predictor")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📂 Upload your CSV",
        type=["csv"],
        help="Download from national-lottery.co.uk → Results → Lotto → Download history"
    )

    if uploaded_file:
        import io
        raw = pd.read_csv(io.BytesIO(uploaded_file.read()))
        raw.to_csv("/tmp/lotto_results.csv", index=False)
        df = load_lottery_data("/tmp/lotto_results.csv")
        st.success(f"✅ Loaded {len(df)} draws!")
    else:
        df = load_lottery_data()
        st.info("📊 Using demo data. Upload your CSV for real results.")

    st.session_state.df = df

    st.markdown("---")
    st.markdown("**📅 Dataset Info**")
    st.markdown(f"- Draws: **{len(df):,}**")
    st.markdown(f"- From: **{df['date'].min().date()}**")
    st.markdown(f"- To:   **{df['date'].max().date()}**")
    st.markdown("---")

    strategy = st.selectbox("🎯 Pick Strategy", ["hot", "cold", "balanced", "random"])
    n_mc = st.slider("🎲 Monte Carlo Simulations", 10_000, 200_000, 50_000, 10_000)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px; color:#666'>
    ⚠️ Lottery draws are random.<br>
    This tool is for data science education only.
    </div>
    """, unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center; color:#f7c948; letter-spacing:3px; font-size:28px; margin-bottom:4px;'>
🎱 UK NATIONAL LOTTERY PREDICTOR
</h1>
<p style='text-align:center; color:#666; font-size:13px; margin-bottom:24px;'>
Data Science Analysis & Pattern Exploration
</p>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> Lottery draws are statistically independent random events.
No model can predict them. This tool is for <strong>data science education and portfolio purposes only</strong>.
Please gamble responsibly.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview", "📊 Frequency Analysis", "🔥 Hot & Cold",
    "🤖 ML Predictions", "🎲 Monte Carlo"
])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    freq = get_ball_frequencies(df)
    last_seen = get_last_seen(df)

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    kpis = [
        ("Total Draws", f"{len(df):,}"),
        ("Hottest Ball", f"#{freq.idxmax()}"),
        ("Coldest Ball", f"#{freq.idxmin()}"),
        ("Most Overdue", f"#{last_seen.idxmax()}"),
        ("Avg Ball Sum", f"{df['ball_sum'].mean():.0f}"),
    ]
    for col, (label, val) in zip([col1,col2,col3,col4,col5], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div style='font-size:11px; color:#888'>{label}</div>
              <div style='font-size:26px; color:#f7c948; font-family:Orbitron;'>{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent draws
    st.markdown("### 🗓️ Recent Draws")
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    recent = df.tail(10)[["date"] + ball_cols + ["bonus_ball"]].copy()
    recent["date"] = recent["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(recent.rename(columns={
        "ball_1":"B1","ball_2":"B2","ball_3":"B3",
        "ball_4":"B4","ball_5":"B5","ball_6":"B6","bonus_ball":"Bonus"
    }).reset_index(drop=True), use_container_width=True)

    # Quick picks
    st.markdown("### 🎯 Quick Number Picks")
    picks = frequency_based_picks(df, strategy)
    balls_html = "".join([
        f'<span class="ball">{b}</span>' for b in sorted(picks)
    ])
    st.markdown(
        f"<div style='text-align:center; padding:16px;'>{balls_html}</div>",
        unsafe_allow_html=True
    )
    st.caption(f"Strategy: **{strategy.upper()}** — {strategy} frequency numbers")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — FREQUENCY ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    freq = get_ball_frequencies(df)

    # Main frequency bar chart
    mean_f = freq.mean()
    colors = ["#f7c948" if f > mean_f*1.05 else "#ff6b6b" if f < mean_f*0.95 else "#3ae4c1"
              for f in freq.values]

    fig = go.Figure(go.Bar(
        x=freq.index, y=freq.values,
        marker_color=colors, marker_line_width=0,
        hovertemplate="Ball %{x}<br>Drawn: %{y} times<extra></extra>"
    ))
    fig.add_hline(y=mean_f, line_dash="dash", line_color="white",
                  annotation_text=f"Mean: {mean_f:.1f}", annotation_position="top right")
    fig.update_layout(
        title="Ball Frequency — All Time",
        paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
        font_color="#e8e8e8", xaxis_title="Ball Number", yaxis_title="Times Drawn",
        height=400, margin=dict(t=50,b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Yearly trends
    st.markdown("### 📈 Frequency Over Time (Top 6 Balls)")
    top6 = freq.nlargest(6).index.tolist()
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    df_yr = df.copy()
    df_yr["year"] = df_yr["date"].dt.year

    fig2 = go.Figure()
    palette = ["#f7c948","#3ae4c1","#ff6b6b","#a78bfa","#f97316","#60a5fa"]
    for ball, color in zip(top6, palette):
        yearly = df_yr.groupby("year").apply(
            lambda g: (g[ball_cols] == ball).any(axis=1).sum()
        )
        fig2.add_trace(go.Scatter(
            x=yearly.index, y=yearly.values, mode="lines+markers",
            name=f"Ball {ball}", line=dict(color=color, width=2),
            marker=dict(size=5)
        ))
    fig2.update_layout(
        paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
        font_color="#e8e8e8", height=350,
        xaxis_title="Year", yaxis_title="Draws per Year",
        legend=dict(bgcolor="#12142a", bordercolor="#333")
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Ball sum distribution
    col_a, col_b = st.columns(2)
    with col_a:
        fig3 = px.histogram(df, x="ball_sum", nbins=40, title="Ball Sum Distribution",
                            color_discrete_sequence=["#3ae4c1"])
        fig3.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                           font_color="#e8e8e8", height=300)
        st.plotly_chart(fig3, use_container_width=True)
    with col_b:
        odd_counts = df["odd_count"].value_counts().sort_index()
        fig4 = px.bar(x=odd_counts.index, y=odd_counts.values,
                      title="Odd/Even Split", labels={"x":"# Odd Balls","y":"Count"},
                      color_discrete_sequence=["#f7c948"])
        fig4.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                           font_color="#e8e8e8", height=300)
        st.plotly_chart(fig4, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — HOT & COLD
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    freq = get_ball_frequencies(df)
    last_seen = get_last_seen(df)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔥 Top 10 Hot Balls")
        top10 = freq.nlargest(10)
        balls_html = "".join([f'<span class="ball">{b}</span>' for b in top10.index])
        st.markdown(f"<div style='padding:12px'>{balls_html}</div>", unsafe_allow_html=True)
        fig = px.bar(x=top10.index.astype(str), y=top10.values,
                     color_discrete_sequence=["#f7c948"])
        fig.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                          font_color="#e8e8e8", height=280,
                          xaxis_title="Ball", yaxis_title="Times Drawn")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### ❄️ Top 10 Cold Balls")
        bot10 = freq.nsmallest(10)
        balls_html = "".join([f'<span class="ball ball-blue">{b}</span>' for b in bot10.index])
        st.markdown(f"<div style='padding:12px'>{balls_html}</div>", unsafe_allow_html=True)
        fig = px.bar(x=bot10.index.astype(str), y=bot10.values,
                     color_discrete_sequence=["#3ae4c1"])
        fig.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                          font_color="#e8e8e8", height=280,
                          xaxis_title="Ball", yaxis_title="Times Drawn")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### ⏳ Most Overdue Balls")
    overdue = last_seen.sort_values(ascending=False).head(15)
    fig5 = px.bar(
        x=overdue.values, y=overdue.index.astype(str),
        orientation="h", color=overdue.values,
        color_continuous_scale=["#3ae4c1","#f7c948","#ff6b6b"],
        labels={"x":"Draws Since Last Seen","y":"Ball Number"}
    )
    fig5.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                       font_color="#e8e8e8", height=400, showlegend=False,
                       coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

    # Pair co-occurrence heatmap
    st.markdown("### 🔗 Pair Co-occurrence (Top 15 Hot Balls)")
    top15 = freq.nlargest(15).index.tolist()
    matrix = get_pair_cooccurrence(df)
    sub = matrix.loc[top15, top15]
    fig6 = px.imshow(sub, color_continuous_scale="YlOrRd",
                     labels=dict(color="Co-occurrences"),
                     title="How Often Pairs Appear Together")
    fig6.update_layout(paper_bgcolor="#0d0f1a", font_color="#e8e8e8", height=500)
    st.plotly_chart(fig6, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — ML PREDICTIONS
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🤖 Machine Learning Prediction")
    st.markdown("""
    <div class="disclaimer">
    The ML model trains a Random Forest for each ball number using rolling frequency,
    gap analysis, and contextual features. Accuracy will be close to the ~10% random baseline.
    </div><br>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("🚀 Train & Predict", type="primary", use_container_width=True):
            with st.spinner("Training 59 models..."):
                models, scaler, feature_cols, scores = train_models(df, lookback=10)
                result = predict_next_draw(df, models, scaler, feature_cols)
                st.session_state["ml_result"] = result
                st.session_state["ml_scores"] = scores

    if "ml_result" in st.session_state:
        result = st.session_state["ml_result"]
        scores = st.session_state["ml_scores"]

        with col2:
            st.markdown(f"**Avg CV Accuracy:** `{np.mean(list(scores.values())):.3f}` (random baseline ~0.102)")

        st.markdown("#### 🎯 Top 6 Predicted Numbers")
        balls_html = "".join([
            f'<span class="ball">{b}</span>' for b in sorted(result["top_6_predicted"])
        ])
        st.markdown(f"<div style='text-align:center; padding:20px;'>{balls_html}</div>",
                    unsafe_allow_html=True)

        st.markdown("#### 📊 Prediction Probabilities (Top 20)")
        top20 = dict(sorted(result["all_probabilities"].items(),
                            key=lambda x: x[1], reverse=True)[:20])
        fig7 = px.bar(
            x=list(top20.keys()), y=list(top20.values()),
            labels={"x":"Ball","y":"Predicted Probability"},
            color=list(top20.values()), color_continuous_scale="YlOrRd"
        )
        fig7.add_hline(y=6/59, line_dash="dash", line_color="white",
                       annotation_text="Random baseline (6/59)")
        fig7.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                           font_color="#e8e8e8", height=350, showlegend=False,
                           coloraxis_showscale=False)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("👆 Click **Train & Predict** to run the ML model")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 5 — MONTE CARLO
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🎲 Monte Carlo Simulation")
    st.markdown("Simulates thousands of lottery tickets to estimate expected returns.")

    if st.button("▶️ Run Monte Carlo", type="primary"):
        with st.spinner(f"Simulating {n_mc:,} tickets..."):
            mc = monte_carlo_simulate(n_mc)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""<div class="metric-card">
            <div style='font-size:11px;color:#888'>Simulations</div>
            <div style='font-size:24px;color:#f7c948;font-family:Orbitron'>{mc['n_simulations']:,}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            ev = mc["expected_value_per_ticket"]
            st.markdown(f"""<div class="metric-card">
            <div style='font-size:11px;color:#888'>Expected Value / Ticket</div>
            <div style='font-size:24px;color:#ff6b6b;font-family:Orbitron'>£{ev:.4f}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="metric-card">
            <div style='font-size:11px;color:#888'>Ticket Cost</div>
            <div style='font-size:24px;color:#3ae4c1;font-family:Orbitron'>£{mc['ticket_cost']:.2f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        dist = mc["match_distribution"]
        fig8 = px.bar(
            x=[f"{k} matches" for k in dist.keys()],
            y=list(dist.values()),
            title="Match Distribution (% of tickets)",
            color=list(dist.values()),
            color_continuous_scale=["#3ae4c1","#f7c948","#ff6b6b"],
            labels={"x":"Matches","y":"% of Tickets"}
        )
        fig8.update_layout(paper_bgcolor="#0d0f1a", plot_bgcolor="#0d0f1a",
                           font_color="#e8e8e8", height=400, showlegend=False,
                           coloraxis_showscale=False)
        st.plotly_chart(fig8, use_container_width=True)

        st.markdown(f"""
        <div class="disclaimer">
        📉 <strong>Expected Value: £{ev:.4f} per £2 ticket</strong><br>
        {mc['note']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👆 Click **Run Monte Carlo** to simulate lottery tickets")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#333; font-size:11px; font-family: Share Tech Mono, monospace'>
UK LOTTERY PREDICTOR • Built with Python, Streamlit & Plotly • For Educational Use Only
</p>""", unsafe_allow_html=True)
