from dataclasses import dataclass

@dataclass
class Signal:
    symbol: str
    side: str
    entry: float
    stop_loss: float
    take_profit: float
    reason: str
    timestamp: object

class TrendMomentumStrategy:
    """Closed-candle trend/momentum strategy; deliberately conservative."""
    def __init__(self, cfg):
        self.cfg = cfg

    def generate(self, symbol, frame):
        if frame is None or len(frame) < self.cfg.trend_ema + 5:
            return None
        row = frame.iloc[-2]  # last fully closed candle; ignore forming candle
        required = ["ema_fast", "ema_slow", "ema_trend", "rsi", "adx", "atr", "close"]
        if any(row.get(k) is None for k in required) or row[required].isna().any():
            return None
        if row.atr <= 0 or row.adx < self.cfg.min_adx:
            return None
        side = None
        if row.ema_fast > row.ema_slow and row.close > row.ema_trend and 52 <= row.rsi <= 68:
            side = "BUY"
        elif row.ema_fast < row.ema_slow and row.close < row.ema_trend and 32 <= row.rsi <= 48:
            side = "SELL"
        if side is None:
            return None
        entry = float(row.close)
        distance = float(row.atr * self.cfg.atr_stop_multiple)
        target = float(row.atr * self.cfg.atr_target_multiple)
        if side == "BUY":
            sl, tp = entry-distance, entry+target
        else:
            sl, tp = entry+distance, entry-target
        rr = target / distance
        if rr < self.cfg.min_reward_risk:
            return None
        return Signal(symbol, side, entry, sl, tp,
                      f"EMA trend + RSI confirmation + ADX {row.adx:.1f}", row.time)
