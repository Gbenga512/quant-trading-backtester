import argparse
from probot_ai.config import SETTINGS
from probot_ai.mt5_adapter import MT5Adapter
from probot_ai.engine import ProBotEngine

def main():
    parser = argparse.ArgumentParser(description="ProBot AI — MT5 demo trading system")
    parser.add_argument("--demo-orders", action="store_true",
        help="Enable order submission ONLY after MT5 confirms a DEMO account.")
    args = parser.parse_args()
    cfg = SETTINGS
    cfg.demo_only = True
    cfg.allow_order_submission = bool(args.demo_orders)
    adapter = MT5Adapter(cfg)
    try:
        account = adapter.connect()
        mode = "DEMO ORDER EXECUTION ENABLED" if cfg.allow_order_submission else "OBSERVE-ONLY"
        print(f"Connected to MT5 DEMO account. Balance={account.balance:.2f}, Equity={account.equity:.2f}")
        print(f"Mode: {mode}. Live accounts are rejected by the adapter.")
        ProBotEngine(cfg, adapter).run()
    finally:
        adapter.close()

if __name__ == "__main__":
    main()
