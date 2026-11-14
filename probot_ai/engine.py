import logging, time
from pathlib import Path
from .indicators import add_indicators
from .strategy import TrendMomentumStrategy
from .risk import RiskManager
from .storage import Store
from .ai_filter import TradeQualityModel

class ProBotEngine:
    def __init__(self, cfg, adapter):
        cfg.validate()
        self.cfg, self.adapter = cfg, adapter
        self.strategy = TrendMomentumStrategy(cfg)
        self.risk = RiskManager(cfg)
        self.store = Store(cfg.database_path)
        self.logger = logging.getLogger("probot_ai")
        self.ai_model = None
        model_path = Path("models/trade_quality.joblib")
        if model_path.exists():
            try:
                self.ai_model = TradeQualityModel(str(model_path)).load()
                self.store.log("ai_model_loaded", {"path": str(model_path)})
            except Exception as exc:
                self.store.log("ai_model_load_error", {"error": str(exc)})

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
        active_count = len(all_positions)
        for symbol in self.cfg.symbols:
            if active_count >= self.cfg.max_positions:
                break
            frame = add_indicators(self.adapter.candles(symbol, self.cfg.data_bars, self.cfg.timeframe), self.cfg)
            signal = self.strategy.generate(symbol, frame)
            if signal is None:
                continue
            ai_probability = None
            if self.ai_model is not None:
                try:
                    ai_probability = self.ai_model.probability(frame.iloc[-2])
                except Exception as exc:
                    self.store.log("ai_filter_error", {"error": str(exc)}, symbol)
                    continue
                if ai_probability < self.cfg.ai_min_probability:
                    self.store.log("ai_filter_rejected", {"probability": ai_probability}, symbol)
                    continue
            tick, info = self.adapter.tick(symbol)
            spread = (tick.ask-tick.bid)/info.point
            symbol_positions = len(self.adapter.positions(symbol))
            approved, reason = self.risk.approve(float(account.equity), all_positions,
                                                  symbol_positions, spread)
            self.store.log("signal_review", {"signal": signal.__dict__, "approved": approved,
                             "reason": reason, "spread_points": spread,
                             "ai_probability": ai_probability}, symbol)
            if not approved:
                continue
            # Observe-only by default. No order is sent unless deliberately enabled for demo.
            if not self.cfg.allow_order_submission:
                continue
            volume = self.risk.volume_from_mt5(self.adapter.mt5, symbol, signal.side,
                       tick.ask if signal.side == "BUY" else tick.bid, signal.stop_loss,
                       float(account.equity), self.cfg.risk_per_trade, info)
            result = self.adapter.send_market_order(signal, volume)
            self.store.log("order_result", {"retcode": result.retcode,
                             "order": result.order, "deal": result.deal, "volume": volume}, symbol)
            active_count += 1

    def run(self):
        logging.basicConfig(level=logging.INFO)
        while True:
            self.scan_once()
            time.sleep(self.cfg.poll_seconds)
