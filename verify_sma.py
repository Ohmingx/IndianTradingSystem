import pandas as pd

df = pd.read_csv("data/normalized/RELIANCE.NS.csv", parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)
df["sma20"] = df["close"].rolling(20).mean()
df["sma50"] = df["close"].rolling(50).mean()

window = df[(df["timestamp"] >= "2015-04-20") & (df["timestamp"] <= "2015-04-29")]
print(window[["timestamp", "close", "sma20", "sma50"]].to_string(index=False))
