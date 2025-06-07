# 🤖 AI Trading Bot – Intraday BTC Strategy

This project is an automated trading bot focused on **Intraday BTC/USDT** trading, powered by **Machine Learning**. It is designed to collect real data from Binance, train models, and execute backtested strategies. AWS deployment is planned for production.

---

## 🚀 Features

- Download historical candle data from **Binance**
- Store data in CSV format for offline use and training
- Build and train machine learning models
- Integrate AI signals into backtesting
- Prepare for real-time deployment with AWS

---

## 🛠️ Tech Stack

- Python 3.10
- [python-binance](https://github.com/sammchardy/python-binance)
- pandas, numpy, matplotlib
- scikit-learn, tensorflow or pytorch
- VS Code + JupyterLab

---

## 📁 Project Structure

```
AI-Trading-Bot/
├── src/                  # Core logic
│   ├── data_collector.py
│   ├── model.py
│   ├── backtesting.py
│   ├── execution.py
│   └── utils.py
├── notebooks/            # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   └── 02_feature_engineering.ipynb
│   └── 03_model_training.ipynb
├── data/                 # Historical CSV data
├── venv/                 # Virtual environment (ignored)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

```bash
# Clone the repository
git clone https://github.com/your-username/AI-Trading-Bot.git
cd AI-Trading-Bot

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📉 Fetch Binance Data

```python
from src.data_collector import get_binance_klines

# Download BTC/USDT 1m candles
get_binance_klines("BTCUSDT", "1m", "2023-01-01", "2023-12-31")
```

---

## 🧠 Train AI Model

> See `/notebooks/` to train and evaluate your model.

---

## ☁️ Future AWS Integration

- Store datasets and models in **S3**
- Deploy inference model via **Lambda + API Gateway**
- Automate retraining with **CloudWatch**

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License

MIT License
