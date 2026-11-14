import argparse
import pandas as pd
from probot_ai.config import SETTINGS
from probot_ai.indicators import add_indicators
from probot_ai.ai_filter import TradeQualityModel

def main():
    p=argparse.ArgumentParser(description="Train ProBot AI market-movement classifier")
    p.add_argument("--csv",required=True,help="OHLC CSV with time,open,high,low,close")
    a=p.parse_args()
    frame=pd.read_csv(a.csv,parse_dates=["time"])
    features=add_indicators(frame,SETTINGS)
    model=TradeQualityModel()
    report=model.fit(features)
    model.save()
    print("Saved models/trade_quality.joblib")
    print(report)
if __name__=="__main__":
    main()
