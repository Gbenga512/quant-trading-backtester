import logging, time
from .indicators import add_indicators
from .strategy import TrendMomentumStrategy
from .risk import RiskManager
from .storage import Store

class ProBotEngine:
    def __init__(self, cfg, adapter):
        cfg.validate()
        self.cfg, self.adapter = cfg, adapter
        self.strategy = TrendMomentumStrategy(cfg)
        self.risk = RiskManager(cfg)
        self.store = Store(cfg.database_path)
        self.logger = logging.getLogger("probot_ai")

    def scan_once(self):
        account = self.adapter.account()
        if account is None:
            raise RuntimeError("Account information unavailable")
        risk_status = self.risk.update(float(account.equity))
        self.store.log("risk_status", risk_status)
        if risk_status["halted"]:
            self.store.log("trading_halted", risk_status)
            return
        all_positions = self.adapter.positions()
        for symbol in self.cfg.symbols:
            frame = add_indicators(self.adapter.candles(symbol, self.cfg.data_bars, self.cfg.timeframe), self.cfg)
            signal = self.strategy.generate(symbol, frame)
            if signal is None:
                continue
            tick, info = self.adapter.tick(symbol)
            spread = (tick.ask-tick.bid)/info.point
            symbol_positions = len(self.adapter.positions(symbol))
            approved, reason = self.risk.approve(float(account.equity), all_positions,
                                                  symbol_positions, spread)
            self.store.log("signal_review", {"signal": signal.__dict__, "approved": approved,
                             "reason": reason, "spread_points": spread}, symbol)
            if not approved:
                continue
            # Build remains observe-only until the user explicitly enables demo execution.
            if not self.cfg.allow_order_submission:
                continue
            volume = self.risk.volume_from_mt5(self.adapter.mt5, symbol, signal.side,
                       tick.ask if signal.side == "BUY" else tick.bid, signal.stop_loss,
                       float(account.equity), self.cfg.risk_per_trade, info)
            result = self.adapter.send_market_order(signal, volume)
            self.store.log("order_result", {"retcode": result.retcode,
                             "order": result.order, "deal": result.deal, "volume": volume}, symbol)

    def run(self):
        logging.basicConfig(level=logging.INFO)
        while True:
            self.scan_once()
            time.sleep(self.cfg.poll_seconds)
