"""
data_loader.py - Load and clean UK National Lottery historical data
Download CSV from: https://www.national-lottery.co.uk/results/lotto/draw-history
"""

import pandas as pd
import numpy as np
import os

def load_lottery_data(filepath: str = "lotto_results.csv") -> pd.DataFrame:
    """
    Load and clean the National Lottery CSV data.
    Supports the official format from national-lottery.co.uk
    """
    # Try to load from file, else generate sample data for demo
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        df = _clean_official_format(df)
    else:
        print(f"[INFO] '{filepath}' not found. Generating sample data for demo.")
        df = _generate_sample_data()

    df = _engineer_features(df)
    print(f"[OK] Loaded {len(df)} draws ({df['date'].min().date()} to {df['date'].max().date()})")
    return df


def _clean_official_format(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the official National Lottery CSV format."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Detect ball columns
    ball_cols = [c for c in df.columns if "ball" in c and "bonus" not in c and "lucky" not in c]
    bonus_cols = [c for c in df.columns if "bonus" in c]
    date_cols = [c for c in df.columns if "draw" in c or "date" in c]

    rename = {}
    for i, c in enumerate(sorted(ball_cols)[:6], 1):
        rename[c] = f"ball_{i}"
    if bonus_cols:
        rename[bonus_cols[0]] = "bonus_ball"
    if date_cols:
        rename[date_cols[0]] = "date"

    df = df.rename(columns=rename)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"])

    ball_columns = [f"ball_{i}" for i in range(1, 7)]
    for col in ball_columns + ["bonus_ball"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=ball_columns)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def _generate_sample_data(n=2000) -> pd.DataFrame:
    """Generate realistic sample data mimicking actual lottery draws."""
    np.random.seed(42)
    dates = pd.date_range(start="1994-11-19", periods=n, freq="3D")
    records = []
    for d in dates:
        balls = sorted(np.random.choice(range(1, 60), 6, replace=False).tolist())
        remaining = [x for x in range(1, 60) if x not in balls]
        bonus = np.random.choice(remaining)
        records.append({
            "date": d,
            "ball_1": balls[0], "ball_2": balls[1], "ball_3": balls[2],
            "ball_4": balls[3], "ball_5": balls[4], "ball_6": balls[5],
            "bonus_ball": bonus
        })
    return pd.DataFrame(records)


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to the dataframe."""
    ball_cols = [f"ball_{i}" for i in range(1, 7)]

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek
    df["draw_number"] = range(1, len(df) + 1)

    # Sum, mean, range of balls
    df["ball_sum"] = df[ball_cols].sum(axis=1)
    df["ball_mean"] = df[ball_cols].mean(axis=1)
    df["ball_range"] = df[ball_cols].max(axis=1) - df[ball_cols].min(axis=1)

    # Odd/even counts
    df["odd_count"] = df[ball_cols].apply(lambda r: sum(x % 2 != 0 for x in r), axis=1)
    df["even_count"] = 6 - df["odd_count"]

    # High/low split (1-29 low, 30-59 high)
    df["low_count"] = df[ball_cols].apply(lambda r: sum(x <= 29 for x in r), axis=1)
    df["high_count"] = 6 - df["low_count"]

    # Consecutive numbers count
    def count_consecutives(row):
        balls = sorted(row[ball_cols].values)
        return sum(1 for i in range(len(balls)-1) if balls[i+1] - balls[i] == 1)
    df["consecutive_count"] = df.apply(count_consecutives, axis=1)

    return df


def get_ball_frequencies(df: pd.DataFrame) -> pd.Series:
    """Return frequency count for each ball number."""
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    all_balls = df[ball_cols].values.flatten()
    return pd.Series(all_balls).value_counts().sort_index()


def get_last_seen(df: pd.DataFrame) -> pd.Series:
    """For each ball, return how many draws ago it last appeared."""
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    last_seen = {}
    total_draws = len(df)
    for ball in range(1, 60):
        mask = (df[ball_cols] == ball).any(axis=1)
        draws_with_ball = df[mask].index.tolist()
        if draws_with_ball:
            last_seen[ball] = total_draws - 1 - draws_with_ball[-1]
        else:
            last_seen[ball] = total_draws
    return pd.Series(last_seen)


def get_pair_cooccurrence(df: pd.DataFrame) -> pd.DataFrame:
    """Build a 59x59 co-occurrence matrix for ball pairs."""
    ball_cols = [f"ball_{i}" for i in range(1, 7)]
    matrix = np.zeros((59, 59), dtype=int)
    for _, row in df.iterrows():
        balls = sorted(row[ball_cols].dropna().astype(int).tolist())
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                a, b = balls[i]-1, balls[j]-1
                matrix[a][b] += 1
                matrix[b][a] += 1
    return pd.DataFrame(matrix, index=range(1, 60), columns=range(1, 60))


if __name__ == "__main__":
    df = load_lottery_data()
    print(df.head())
    print(df.describe())
