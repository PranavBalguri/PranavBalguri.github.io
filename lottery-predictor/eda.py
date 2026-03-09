"""
eda.py - Exploratory Data Analysis for UK National Lottery
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from data_loader import load_lottery_data, get_ball_frequencies, get_last_seen, get_pair_cooccurrence
import warnings
warnings.filterwarnings("ignore")

# ── Style ──────────────────────────────────────────────────────────────────────
DARK_BG   = "#0d0f1a"
ACCENT1   = "#f7c948"   # gold
ACCENT2   = "#3ae4c1"   # teal
ACCENT3   = "#ff6b6b"   # red
TEXT_COL  = "#e8e8e8"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": DARK_BG,
    "axes.edgecolor": "#333355", "axes.labelcolor": TEXT_COL,
    "xtick.color": TEXT_COL, "ytick.color": TEXT_COL,
    "text.color": TEXT_COL, "grid.color": "#1e2040",
    "grid.linestyle": "--", "grid.alpha": 0.5,
    "font.family": "monospace",
})


def plot_ball_frequency(df: pd.DataFrame, save: bool = True):
    freq = get_ball_frequencies(df)
    mean_freq = freq.mean()

    fig, ax = plt.subplots(figsize=(16, 5))
    colors = [ACCENT1 if f > mean_freq * 1.05 else ACCENT3 if f < mean_freq * 0.95 else ACCENT2
              for f in freq.values]
    bars = ax.bar(freq.index, freq.values, color=colors, width=0.8, zorder=3)
    ax.axhline(mean_freq, color="white", linestyle="--", linewidth=1.2, alpha=0.7, label=f"Mean: {mean_freq:.1f}")
    ax.set_title("Ball Frequency Distribution — All Draws", fontsize=16, color=ACCENT1, pad=16)
    ax.set_xlabel("Ball Number", fontsize=11)
    ax.set_ylabel("Times Drawn", fontsize=11)
    ax.grid(axis="y", zorder=0)
    ax.set_xlim(0.5, 59.5)

    # Annotate top 5 hot / cold
    top5 = freq.nlargest(5).index.tolist()
    bot5 = freq.nsmallest(5).index.tolist()
    for ball in top5:
        ax.annotate("🔥", xy=(ball, freq[ball]+1), ha="center", fontsize=9)
    for ball in bot5:
        ax.annotate("❄️", xy=(ball, freq[ball]+1), ha="center", fontsize=9)

    patches = [
        mpatches.Patch(color=ACCENT1, label="Hot (above avg)"),
        mpatches.Patch(color=ACCENT2, label="Normal"),
        mpatches.Patch(color=ACCENT3, label="Cold (below avg)"),
    ]
    ax.legend(handles=patches, loc="upper right", framealpha=0.2)
    plt.tight_layout()
    if save:
        plt.savefig("outputs/01_ball_frequency.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print("[OK] Saved 01_ball_frequency.png")
    plt.show()


def plot_overdue_balls(df: pd.DataFrame, save: bool = True):
    last_seen = get_last_seen(df)
    last_seen_sorted = last_seen.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(16, 5))
    colors = [ACCENT3 if v > 20 else ACCENT1 if v > 10 else ACCENT2 for v in last_seen_sorted.values]
    ax.barh(last_seen_sorted.index.astype(str), last_seen_sorted.values, color=colors, height=0.7)
    ax.set_title("Overdue Balls — Draws Since Last Appearance", fontsize=15, color=ACCENT1, pad=14)
    ax.set_xlabel("Draws Since Last Seen", fontsize=11)
    ax.set_ylabel("Ball Number", fontsize=11)
    ax.grid(axis="x")
    plt.tight_layout()
    if save:
        plt.savefig("outputs/02_overdue_balls.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print("[OK] Saved 02_overdue_balls.png")
    plt.show()


def plot_pair_heatmap(df: pd.DataFrame, top_n: int = 20, save: bool = True):
    matrix = get_pair_cooccurrence(df)
    freq = get_ball_frequencies(df)
    top_balls = freq.nlargest(top_n).index.tolist()
    sub = matrix.loc[top_balls, top_balls]

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(sub, cmap="YlOrRd", linewidths=0.3, linecolor="#222244",
                annot=True, fmt="d", annot_kws={"size": 7}, ax=ax,
                cbar_kws={"shrink": 0.7})
    ax.set_title(f"Ball Pair Co-occurrence (Top {top_n} Hot Balls)", fontsize=14, color=ACCENT1, pad=14)
    plt.tight_layout()
    if save:
        plt.savefig("outputs/03_pair_heatmap.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print("[OK] Saved 03_pair_heatmap.png")
    plt.show()


def plot_sum_distribution(df: pd.DataFrame, save: bool = True):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Ball sum histogram
    ax = axes[0]
    ax.hist(df["ball_sum"], bins=40, color=ACCENT2, edgecolor=DARK_BG, alpha=0.9, zorder=3)
    ax.axvline(df["ball_sum"].mean(), color=ACCENT1, linestyle="--", linewidth=2, label=f"Mean: {df['ball_sum'].mean():.1f}")
    ax.set_title("Distribution of Ball Sum per Draw", fontsize=13, color=ACCENT1)
    ax.set_xlabel("Sum of 6 Balls")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(axis="y", zorder=0)

    # Odd/even distribution
    ax2 = axes[1]
    odd_counts = df["odd_count"].value_counts().sort_index()
    ax2.bar(odd_counts.index, odd_counts.values, color=ACCENT1, edgecolor=DARK_BG, width=0.6)
    ax2.set_title("Odd vs Even Split per Draw", fontsize=13, color=ACCENT1)
    ax2.set_xlabel("Number of Odd Balls")
    ax2.set_ylabel("Frequency")
    ax2.set_xticks(range(7))
    ax2.set_xticklabels([f"{i} odd\n{6-i} even" for i in range(7)], fontsize=8)
    ax2.grid(axis="y", zorder=0)

    plt.tight_layout()
    if save:
        plt.savefig("outputs/04_sum_odd_even.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print("[OK] Saved 04_sum_odd_even.png")
    plt.show()


def plot_frequency_over_time(df: pd.DataFrame, balls: list = None, save: bool = True):
    if balls is None:
        freq = get_ball_frequencies(df)
        balls = freq.nlargest(5).index.tolist()

    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    df = df.copy()
    df["year"] = df["date"].dt.year

    fig, ax = plt.subplots(figsize=(14, 5))
    colors = [ACCENT1, ACCENT2, ACCENT3, "#a78bfa", "#f97316"]

    for ball, color in zip(balls, colors):
        yearly = df.groupby("year").apply(
            lambda g: (g[ball_cols] == ball).any(axis=1).sum()
        )
        ax.plot(yearly.index, yearly.values, marker="o", markersize=4,
                linewidth=2, color=color, label=f"Ball {ball}")

    ax.set_title("Top 5 Hot Balls — Frequency Over Time", fontsize=14, color=ACCENT1)
    ax.set_xlabel("Year")
    ax.set_ylabel("Times Drawn per Year")
    ax.legend(loc="upper right", framealpha=0.2)
    ax.grid(zorder=0)
    plt.tight_layout()
    if save:
        plt.savefig("outputs/05_frequency_over_time.png", dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print("[OK] Saved 05_frequency_over_time.png")
    plt.show()


def run_full_eda(df: pd.DataFrame):
    import os
    os.makedirs("outputs", exist_ok=True)
    print("\n=== Running Full EDA ===\n")
    plot_ball_frequency(df)
    plot_overdue_balls(df)
    plot_pair_heatmap(df)
    plot_sum_distribution(df)
    plot_frequency_over_time(df)
    print("\n[DONE] All charts saved to outputs/")


if __name__ == "__main__":
    df = load_lottery_data()
    run_full_eda(df)
