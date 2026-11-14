import argparse
from probot_ai.config import SETTINGS
from probot_ai.mt5_adapter import MT5Adapter
from probot_ai.engine import ProBotEngine

def main():
    parser = argparse.ArgumentParser(description="ProBot AI — MT5 demo trading system")
    parser.add_argument("--observe", action="store_true", help="Analyse and log signals without placing orders")
    args = parser.parse_args()
    cfg = SETTINGS
    cfg.allow_order_submission = False  # hard default; demo order mode requires a deliberate code/config change
    adapter = MT5Adapter(cfg)
    try:
        account = adapter.connect()
        print(f"Connected to MT5 demo account. Balance={account.balance:.2f}, Equity={account.equity:.2f}")
        print("Observe-only mode: no orders will be sent.")
        ProBotEngine(cfg, adapter).run()
    finally:
        adapter.close()

if __name__ == "__main__":
    main()
