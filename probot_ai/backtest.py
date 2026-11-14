"""Simple bar-based research harness. Not an execution simulator.
For reliable research, include spread, commission, swaps and slippage in the input data/model.
"""
import pandas as pd
from .indicators import add_indicators
from .strategy import TrendMomentumStrategy

def run_backtest(frame, symbol, cfg, initial_balance=10000.0, pip_size=0.0001,
                 pip_value_per_lot=10.0, risk_fraction=None):
    df = add_indicators(frame, cfg).reset_index(drop=True)
    strategy = TrendMomentumStrategy(cfg)
    balance, peak, max_dd = float(initial_balance), float(initial_balance), 0.0
    trades = []
    risk_fraction = risk_fraction or cfg.risk_per_trade
    i = cfg.trend_ema + 5
    while i < len(df)-1:
        signal = strategy.generate(symbol, df.iloc[:i+2])
        if signal is None:
            i += 1
            continue
        entry_i = i+1
        entry = float(df.iloc[entry_i].open)
        stop = signal.stop_loss
        target = signal.take_profit
        risk_pips = abs(entry-stop)/pip_size
        if risk_pips <= 0:
            i += 1
            continue
        lots = balance*risk_fraction/(risk_pips*pip_value_per_lot)
        outcome, exit_price, exit_i = "OPEN", None, entry_i
        for j in range(entry_i, len(df)):
            bar = df.iloc[j]
            if signal.side == "BUY":
                hit_sl, hit_tp = bar.low <= stop, bar.high >= target
            else:
                hit_sl, hit_tp = bar.high >= stop, bar.low <= target
            if hit_sl:  # conservative: stop wins if both touched in same candle
                outcome, exit_price, exit_i = "LOSS", stop, j
                break
            if hit_tp:
                outcome, exit_price, exit_i = "WIN", target, j
                break
        if exit_price is None:
            i += 1
            continue
        pnl_pips = (exit_price-entry)/pip_size * (1 if signal.side=="BUY" else -1)
        pnl = pnl_pips*pip_value_per_lot*lots
        balance += pnl
        peak = max(peak, balance)
        max_dd = max(max_dd, (peak-balance)/peak)
        trades.append({"symbol":symbol,"side":signal.side,"entry_time":df.iloc[entry_i].time,
                       "exit_time":df.iloc[exit_i].time,"entry":entry,"exit":exit_price,
                       "lots":lots,"pnl":pnl,"outcome":outcome,"balance":balance})
        i = exit_i+1
    t = pd.DataFrame(trades)
    gross_profit = t.loc[t.pnl>0,"pnl"].sum() if len(t) else 0
    gross_loss = abs(t.loc[t.pnl<0,"pnl"].sum()) if len(t) else 0
    return {"trades":t,"ending_balance":balance,"net_profit":balance-initial_balance,
            "profit_factor":gross_profit/gross_loss if gross_loss else None,
            "win_rate":float((t.pnl>0).mean()) if len(t) else 0.0,
            "max_drawdown":max_dd,"trade_count":len(t)}
