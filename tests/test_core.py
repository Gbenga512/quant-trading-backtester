from datetime import date
import pandas as pd
import pytest
from probot_ai.config import Settings
from probot_ai.risk import RiskManager
from probot_ai.indicators import add_indicators

def test_config_rejects_live_mode():
    cfg = Settings()
    cfg.demo_only = False
    with pytest.raises(ValueError):
        cfg.validate()

def test_risk_halts_after_daily_loss():
    cfg = Settings(max_daily_loss=0.02)
    risk = RiskManager(cfg)
    risk.update(10000, date(2026, 1, 1))
    status = risk.update(9700, date(2026, 1, 1))
    assert status["halted"]

def test_indicators_add_columns():
    cfg = Settings()
    n = 300
    close = pd.Series([1.1 + i*0.00001 for i in range(n)])
    frame = pd.DataFrame({"time":pd.date_range("2026-01-01", periods=n, freq="5min"),
        "open":close,"high":close+0.0002,"low":close-0.0002,"close":close})
    out = add_indicators(frame, cfg)
    assert {"ema_fast","ema_slow","ema_trend","rsi","adx","atr"}.issubset(out.columns)
