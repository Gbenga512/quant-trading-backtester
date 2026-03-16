import pandas as pd
import numpy as np
import yfinance as yf

# Download stock data
data = yf.download("AAPL", start="2020-01-01", end="2024-01-01")

# Calculate moving averages
data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

# Generate signals
data["Signal"] = np.where(data["MA50"] > data["MA200"], 1, 0)

# Strategy returns
data["Returns"] = data["Close"].pct_change()
data["Strategy"] = data["Returns"] * data["Signal"].shift(1)

# Performance
cumulative = (1 + data["Strategy"]).cumprod()

print("Final Return:", cumulative.iloc[-1])
