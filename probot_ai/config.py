from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Settings:
    # Safe defaults: the engine refuses live accounts and live order submission.
    demo_only: bool = True
    allow_order_submission: bool = False
    timeframe: str = "M5"
    symbols: tuple[str, ...] = ("EURUSD", "GBPUSD", "USDJPY")
    risk_per_trade: float = 0.0025
    max_daily_loss: float = 0.02
    max_equity_drawdown: float = 0.05
    max_positions: int = 2
    max_positions_per_symbol: int = 1
    max_spread_points: int = 25
    min_adx: float = 18.0
    min_reward_risk: float = 1.5
    ai_min_probability: float = 0.55
    atr_stop_multiple: float = 1.8
    atr_target_multiple: float = 2.7
    fast_ema: int = 20
    slow_ema: int = 50
    trend_ema: int = 200
    rsi_period: int = 14
    adx_period: int = 14
    atr_period: int = 14
    magic_number: int = 6142026
    poll_seconds: int = 5
    data_bars: int = 1500
    database_path: str = "data/probot_ai.sqlite3"
    log_path: str = "logs/probot_ai.log"
    news_blackout_minutes: int = 30
    # Broker-specific pip values must be verified before backtesting.
    pip_size: dict[str, float] = field(default_factory=lambda: {
        "EURUSD": 0.0001, "GBPUSD": 0.0001, "USDJPY": 0.01
    })

    def validate(self):
        if not 0 < self.risk_per_trade <= 0.01:
            raise ValueError("risk_per_trade must be > 0 and <= 1%")
        if not 0 < self.max_daily_loss <= 0.05:
            raise ValueError("max_daily_loss must be > 0 and <= 5%")
        if not 0 < self.max_equity_drawdown <= 0.10:
            raise ValueError("max_equity_drawdown must be > 0 and <= 10%")
        if self.max_positions < 1:
            raise ValueError("max_positions must be at least 1")
        if not self.demo_only:
            raise ValueError("This build is demo-only; live mode is disabled.")

SETTINGS = Settings()
