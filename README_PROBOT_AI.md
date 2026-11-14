# ProBot AI — Integrated Demo-First FX System

ProBot AI is a modular Python/MT5 quantitative FX research and execution system. This branch adds the first integrated implementation to the existing quantitative backtesting repository.

## Safety defaults
- Demo account only: the MT5 adapter rejects non-demo accounts.
- Observe-only: order submission is disabled by default.
- No live trading mode is implemented.
- Risk engine blocks new entries after daily loss or equity drawdown thresholds.
- MT5 order sizing uses broker-side `order_calc_profit`, not hard-coded pip-value assumptions.
- Never put MT5 passwords, Telegram tokens or API keys in source control.

## Instruments and timeframe
Initial watchlist: EURUSD, GBPUSD, USDJPY. Signal timeframe: M5. Verify exact broker symbol names (suffixes may apply), contract specifications, spreads, commissions, swaps and execution rules before running.

## Install
Use Windows with MetaTrader 5 desktop installed and logged into a DEMO account.

```powershell
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m pytest
python run.py --observe
```

## Dashboard
After the observer has created the event database, run:
```powershell
streamlit run probot_ai/dashboard.py
```

## Research strategy
Closed-candle trend/momentum baseline using EMA 20/50/200, RSI 14, ADX 14 and ATR 14. Stops and targets are ATR-based. This is a testable hypothesis, not a claim of profitability.

## Backtesting
Prepare broker-quality OHLC CSV data with columns `time,open,high,low,close`. Run:
```powershell
python backtest_cli.py --csv data/EURUSD_M5.csv --symbol EURUSD --pip-size 0.0001 --pip-value-per-lot 10
``
The pip value example is not universal; verify it for the broker, instrument and account currency. The included bar-based harness is preliminary: it does not model bid/ask spread, commission, swaps, latency, variable slippage or tick-level intrabar paths. It is not a production-grade performance claim.

## ML filter
An optional Random Forest movement classifier can be trained from indicator-enriched historical data. It requires at least 500 labelled observations and chronological train/test ordering. If a saved model exists at `models/trade_quality.joblib`, the engine applies its probability threshold to candidate trades. Model validation, class balance, drift and leakage checks are required before relying on it.

## Before demo order execution
1. Confirm the connected account is demo and broker symbols resolve.
2. Validate volume limits, tick size, filling mode, stops level and order permissions.
3. Persist daily risk baselines and kill-switch state across restarts.
4. Add spread/commission-aware tick backtesting and walk-forward evaluation.
5. Verify position reconciliation and duplicate-order prevention.
6. Enable order submission only after reviewing the complete test report. Live trading remains out of scope.

## Components
`config`, `indicators`, `strategy`, `risk`, `mt5_adapter`, `engine`, `storage`, `backtest`, `ai_filter`, and `dashboard`.
