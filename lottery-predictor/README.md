# 🎱 UK National Lottery Predictor

A free, open-source data science project for exploring UK National Lottery patterns.

> ⚠️ **Disclaimer**: Lottery draws are statistically independent random events. This tool is for **data science education** only.

---

## 📁 Project Structure

```
lottery_predictor/
├── data_loader.py      # Data loading, cleaning & feature engineering
├── eda.py              # Exploratory Data Analysis (charts saved to outputs/)
├── model.py            # ML prediction pipeline + Monte Carlo simulation
├── app.py              # 🚀 Streamlit dashboard (main app)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 🚀 Quick Start (100% Free)

### 1. Install Python 3.8+
Download from https://python.org (free)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get historical data (free)
- Go to: https://www.national-lottery.co.uk/results/lotto/draw-history
- Scroll down → Click **"Download results"**
- Save as `lotto_results.csv` in this folder

### 4. Run the dashboard
```bash
streamlit run app.py
```
Opens at http://localhost:8501 🎉

---

## 📊 Features

| Feature | Description |
|---|---|
| **Frequency Analysis** | Hot/cold balls, yearly trends, heatmaps |
| **Overdue Analysis** | Balls not drawn for longest time |
| **Pair Co-occurrence** | Which balls appear together most |
| **ML Predictions** | Random Forest model per ball |
| **Monte Carlo** | Expected value simulation |
| **Quick Picks** | Hot/cold/balanced/random strategies |
| **CSV Upload** | Upload your own data file |

---

## 🌐 Deploy for Free (Streamlit Cloud)

1. Push this folder to a free GitHub repo
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Set main file: `app.py`
5. Click **Deploy** → your app is live at a free URL!

---

## 🧠 How the ML Works

For each ball number (1–59), a Random Forest classifier is trained to predict
"will this ball appear in the next draw?" using features:

- Rolling frequency (last 10 draws)
- Gap since last appearance  
- Ball sum trends
- Odd/even ratios
- Day/month context

**Expected accuracy**: ~10–11% (barely above random baseline of 6/59 ≈ 10.2%)

---

## 🎲 Monte Carlo

Simulates N random lottery tickets to estimate:
- Match distribution (0–6 balls)
- Expected value per £2 ticket
- Confirms negative EV (the house always wins)

---

## 📦 All Tools Used (100% Free)

| Tool | Purpose | Cost |
|---|---|---|
| Python 3 | Language | Free |
| pandas | Data manipulation | Free |
| numpy | Numerical computing | Free |
| scikit-learn | Machine learning | Free |
| matplotlib/seaborn | Static charts | Free |
| plotly | Interactive charts | Free |
| streamlit | Dashboard | Free |
| Streamlit Cloud | Hosting | Free |
| GitHub | Version control | Free |

---

Made with ❤️ for data science learning.
