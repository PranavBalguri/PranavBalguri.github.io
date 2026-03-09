"""
model.py - ML Prediction Pipeline for UK National Lottery
NOTE: Lottery draws are random; this is for educational/portfolio purposes.
      Models will perform near the random baseline (~10% per ball).
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore")


def build_features(df: pd.DataFrame, lookback: int = 10) -> pd.DataFrame:
    """
    Build features for each draw to predict which balls appear.
    Features are derived from the previous `lookback` draws only.
    """
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    records = []

    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        current = df.iloc[i]
        current_balls = set(current[ball_cols].astype(int).tolist())
        row = {}

        # Rolling frequency of each ball in window
        for ball in range(1, 60):
            appearances = (window[ball_cols] == ball).any(axis=1).sum()
            row[f"freq_{ball}"] = appearances / lookback

        # Gap since each ball last appeared
        for ball in range(1, 60):
            mask = (window[ball_cols] == ball).any(axis=1)
            idxs = mask[mask].index.tolist()
            row[f"gap_{ball}"] = lookback - (window.index.tolist().index(idxs[-1]) if idxs else -1)

        # Context features
        row["ball_sum_prev"] = window["ball_sum"].mean()
        row["odd_count_prev"] = window["odd_count"].mean()
        row["draw_number"] = current["draw_number"]
        row["month"] = current["month"]
        row["day_of_week"] = current["day_of_week"]

        # Targets: one binary label per ball
        for ball in range(1, 60):
            row[f"target_{ball}"] = 1 if ball in current_balls else 0

        records.append(row)

    return pd.DataFrame(records)


def train_models(df: pd.DataFrame, lookback: int = 10) -> dict:
    """Train one model per ball number (1–59)."""
    print("[INFO] Building feature matrix...")
    features_df = build_features(df, lookback)

    feature_cols = [c for c in features_df.columns if not c.startswith("target_")]
    X = features_df[feature_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    models = {}
    scores = {}

    print("[INFO] Training models for each ball (1–59)...")
    for ball in range(1, 60):
        target_col = f"target_{ball}"
        y = features_df[target_col].values

        if y.sum() < 10:
            continue

        clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
        cv_scores = cross_val_score(clf, X_scaled, y, cv=5, scoring="accuracy")
        clf.fit(X_scaled, y)

        models[ball] = {"model": clf, "scaler": scaler, "feature_cols": feature_cols}
        scores[ball] = cv_scores.mean()

        if ball % 10 == 0:
            print(f"  Ball {ball:2d}: CV Accuracy = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    print(f"\n[OK] Trained {len(models)} models. Avg accuracy: {np.mean(list(scores.values())):.3f}")
    return models, scaler, feature_cols, scores


def predict_next_draw(df: pd.DataFrame, models: dict, scaler, feature_cols: list,
                      lookback: int = 10, top_n: int = 6) -> dict:
    """Predict probabilities for the next draw and suggest numbers."""
    window = df.tail(lookback)
    ball_cols = [f"ball_{i}" for i in range(1, 7)]

    row = {}
    for ball in range(1, 60):
        appearances = (window[ball_cols] == ball).any(axis=1).sum()
        row[f"freq_{ball}"] = appearances / lookback

    for ball in range(1, 60):
        mask = (window[ball_cols] == ball).any(axis=1)
        idxs = mask[mask].index.tolist()
        row[f"gap_{ball}"] = lookback - (window.index.tolist().index(idxs[-1]) if idxs else -1)

    row["ball_sum_prev"] = df["ball_sum"].tail(lookback).mean()
    row["odd_count_prev"] = df["odd_count"].tail(lookback).mean()
    row["draw_number"] = df["draw_number"].iloc[-1] + 1
    row["month"] = pd.Timestamp.now().month
    row["day_of_week"] = pd.Timestamp.now().dayofweek

    X_row = pd.DataFrame([row])[feature_cols].values
    X_scaled = scaler.transform(X_row)

    probs = {}
    for ball, m in models.items():
        prob = m["model"].predict_proba(X_scaled)[0]
        probs[ball] = prob[1] if len(prob) > 1 else prob[0]

    prob_series = pd.Series(probs).sort_values(ascending=False)

    return {
        "top_6_predicted": prob_series.head(top_n).index.tolist(),
        "top_10_candidates": prob_series.head(10).index.tolist(),
        "all_probabilities": prob_series.to_dict(),
        "confidence_note": "Random baseline ~10.2%. Higher prob = model's preference only."
    }


def monte_carlo_simulate(n_simulations: int = 100_000) -> dict:
    """
    Monte Carlo simulation: expected value and distribution of outcomes.
    Ticket cost: £2. Jackpot odds: 1 in 45,057,474
    """
    results = defaultdict(int)
    ticket_cost = 2.0
    prizes = {6: 2_000_000, 5: 1750, 4: 140, 3: 30, 2: 0, 1: 0, 0: 0}

    for _ in range(n_simulations):
        winning = set(np.random.choice(range(1, 60), 6, replace=False))
        ticket = set(np.random.choice(range(1, 60), 6, replace=False))
        matches = len(winning & ticket)
        results[matches] += 1

    total = sum(results.values())
    ev = sum((count / total) * prizes[matches] for matches, count in results.items()) - ticket_cost

    return {
        "n_simulations": n_simulations,
        "match_distribution": {k: round(v/total*100, 4) for k, v in sorted(results.items())},
        "expected_value_per_ticket": round(ev, 4),
        "ticket_cost": ticket_cost,
        "note": "Negative EV confirms lottery is not a profitable investment strategy"
    }


def frequency_based_picks(df: pd.DataFrame, strategy: str = "hot") -> list:
    """
    Simple frequency-based number picker.
    strategy: 'hot', 'cold', 'balanced', 'random'
    """
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    all_balls = df[ball_cols].values.flatten()
    freq = pd.Series(all_balls).value_counts().sort_values()

    if strategy == "hot":
        return freq.nlargest(6).index.tolist()
    elif strategy == "cold":
        return freq.nsmallest(6).index.tolist()
    elif strategy == "balanced":
        hot = freq.nlargest(3).index.tolist()
        cold = freq.nsmallest(3).index.tolist()
        return sorted(hot + cold)
    else:
        return sorted(np.random.choice(range(1, 60), 6, replace=False).tolist())


if __name__ == "__main__":
    from data_loader import load_lottery_data

    df = load_lottery_data()
    models, scaler, feature_cols, scores = train_models(df, lookback=10)

    result = predict_next_draw(df, models, scaler, feature_cols)
    print("\n=== Next Draw Prediction ===")
    print(f"Top 6 Predicted: {result['top_6_predicted']}")
    print(f"Top 10 Candidates: {result['top_10_candidates']}")
    print(f"Note: {result['confidence_note']}")

    print("\n=== Monte Carlo Simulation ===")
    mc = monte_carlo_simulate(50_000)
    for k, v in mc.items():
        print(f"  {k}: {v}")

    print("\n=== Frequency-Based Picks ===")
    for strat in ["hot", "cold", "balanced", "random"]:
        picks = frequency_based_picks(df, strat)
        print(f"  {strat.capitalize():10s}: {picks}")
