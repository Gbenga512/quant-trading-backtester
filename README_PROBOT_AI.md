# ProBot AI — Integrated Demo-First FX System

This branch adds a modular Python/MT5 quantitative FX research and execution foundation.

## Safety defaults
- Demo account only: the adapter rejects non-demo MT5 accounts.
- Observe-only: order submission is disabled by default.
- No live trading mode is implemented.
- Risk engine blocks new entries after daily loss or equity drawdown thresholds.
- MT5 order sizing uses broker-side `order_calc_profit`, not hard-coded pip-value assumptions.

## Instruments and timeframe
Initial watchlist: EURUSD, GBPUSD, USDJPY. Initial signal timeframe: M5.
Verify exact broker symbol names (suffixes may apply), contract specifications, spreads, commission and swap before running.

## Install
Use Windows with MetaTrader 5 desktop installed and logged into a DEMO account.

```powershell
py -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m pytest
python run.py --observe
```

## Current research strategy
Closed-candle trend/momentum rule using EMA 20/50/200, RSI 14, ADX 14 and ATR 14. Stops and targets are ATR-based. The strategy is a testable baseline, not a claim of profitability.

## Backtesting
Use broker-quality historical OHLC data and correct symbol pip size/value. The included bar-based harness is a preliminary research tool only: it does not model bid/ask spread, commission, swaps, latency, variable slippage or intrabar tick paths. Do not treat its output as a production-grade performance claim.

## ML filter
The optional Random Forest filter requires at least 500 labelled observations and uses chronological train/test ordering. Its labels and evaluation must be reviewed for class imbalance and leakage before using it to filter live signals. It is not enabled in the execution loop yet.

## Before demo order execution
1. Confirm account is demo and symbol names resolve.
2. Validate broker volume, tick size, filling modes and stops level.
3. Add a persistent daily risk baseline and restart-safe kill switch.
4. Add spread/commission-aware tick backtesting and walk-forward evaluation.
5. Review logs and order reconciliation.
6. Only enable demo order submission after those checks. Live trading remains out of scope.

## Architecture
`config` settings; `indicators` feature calculations; `strategy` signals; `risk` controls; `mt5_adapter` broker boundary; `engine` orchestration; `storage` audit log; `backtest` research harness; `ai_filter` optional model.
