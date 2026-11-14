import argparse, json
import pandas as pd
from probot_ai.config import SETTINGS
from probot_ai.backtest import run_backtest

def main():
    p=argparse.ArgumentParser(description="Run preliminary ProBot AI CSV backtest")
    p.add_argument("--csv", required=True, help="OHLC CSV with time,open,high,low,close")
    p.add_argument("--symbol", required=True, choices=SETTINGS.symbols)
    p.add_argument("--pip-size", type=float, required=True)
    p.add_argument("--pip-value-per-lot", type=float, required=True,
                   help="Broker/account-currency pip value for one standard lot; verify first")
    p.add_argument("--balance", type=float, default=10000)
    a=p.parse_args()
    frame=pd.read_csv(a.csv, parse_dates=["time"])
    result=run_backtest(frame,a.symbol,SETTINGS,a.balance,a.pip_size,a.pip_value_per_lot)
    trades=result.pop("trades")
    print(json.dumps(result,indent=2,default=str))
    trades.to_csv("probot_backtest_trades.csv",index=False)
    print("Saved trade ledger to probot_backtest_trades.csv")
if __name__=="__main__":
    main()
