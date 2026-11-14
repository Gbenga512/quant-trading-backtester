import numpy as np
import pandas as pd

REQUIRED = {"time", "open", "high", "low", "close"}

def add_indicators(frame: pd.DataFrame, cfg) -> pd.DataFrame:
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing OHLC columns: {sorted(missing)}")
    df = frame.copy().sort_values("time").drop_duplicates("time")
    for col in ("open", "high", "low", "close"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    close, high, low = df.close, df.high, df.low
    df["ema_fast"] = close.ewm(span=cfg.fast_ema, adjust=False).mean()
    df["ema_slow"] = close.ewm(span=cfg.slow_ema, adjust=False).mean()
    df["ema_trend"] = close.ewm(span=cfg.trend_ema, adjust=False).mean()
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/cfg.rsi_period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/cfg.rsi_period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi"] = (100 - (100 / (1 + rs))).fillna(50)
    prev = close.shift(1)
    tr = pd.concat([(high-low), (high-prev).abs(), (low-prev).abs()], axis=1).max(axis=1)
    df["atr"] = tr.ewm(alpha=1/cfg.atr_period, adjust=False).mean()
    up, down = high.diff(), -low.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0)
    atr = df["atr"].replace(0, np.nan)
    plus_di = 100 * plus_dm.ewm(alpha=1/cfg.adx_period, adjust=False).mean() / atr
    minus_di = 100 * minus_dm.ewm(alpha=1/cfg.adx_period, adjust=False).mean() / atr
    dx = 100 * (plus_di-minus_di).abs() / (plus_di+minus_di).replace(0, np.nan)
    df["adx"] = dx.ewm(alpha=1/cfg.adx_period, adjust=False).mean().fillna(0)
    return df.replace([np.inf, -np.inf], np.nan)
