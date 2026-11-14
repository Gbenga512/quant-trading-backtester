class MT5Adapter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.mt5 = None

    def connect(self):
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise RuntimeError("Install MetaTrader5 on a Windows machine with MT5 terminal.") from exc
        self.mt5 = mt5
        if not mt5.initialize():
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
        account = mt5.account_info()
        if account is None:
            raise RuntimeError(f"MT5 account unavailable: {mt5.last_error()}")
        if getattr(account, "trade_mode", None) != mt5.ACCOUNT_TRADE_MODE_DEMO:
            mt5.shutdown()
            raise RuntimeError("Safety lock: ProBot AI only connects to MT5 DEMO accounts.")
        return account

    def account(self):
        return self.mt5.account_info()

    def positions(self, symbol=None):
        result = self.mt5.positions_get(symbol=symbol) if symbol else self.mt5.positions_get()
        return list(result or [])

    def candles(self, symbol, count, timeframe):
        tf = getattr(self.mt5, f"TIMEFRAME_{timeframe}")
        rates = self.mt5.copy_rates_from_pos(symbol, tf, 0, count)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"No rates for {symbol}: {self.mt5.last_error()}")
        import pandas as pd
        frame = pd.DataFrame(rates)
        frame["time"] = pd.to_datetime(frame["time"], unit="s", utc=True)
        return frame.rename(columns={"tick_volume": "volume"})

    def tick(self, symbol):
        tick = self.mt5.symbol_info_tick(symbol)
        info = self.mt5.symbol_info(symbol)
        if tick is None or info is None:
            raise RuntimeError(f"Symbol unavailable: {symbol}")
        return tick, info

    def _filling_mode(self, info):
        mt5 = self.mt5
        modes = info.filling_mode
        if modes & mt5.SYMBOL_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        if modes & mt5.SYMBOL_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        return mt5.ORDER_FILLING_RETURN

    def send_market_order(self, signal, volume):
        if not self.cfg.demo_only or not self.cfg.allow_order_submission:
            raise RuntimeError("Order submission is disabled. Explicit demo test configuration required.")
        mt5 = self.mt5
        tick, info = self.tick(signal.symbol)
        price = tick.ask if signal.side == "BUY" else tick.bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL, "symbol": signal.symbol, "volume": volume,
            "type": mt5.ORDER_TYPE_BUY if signal.side == "BUY" else mt5.ORDER_TYPE_SELL,
            "price": price, "sl": signal.stop_loss, "tp": signal.take_profit,
            "deviation": 20, "magic": self.cfg.magic_number,
            "comment": "ProBotAI-demo", "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self._filling_mode(info),
        }
        check = mt5.order_check(request)
        if check is None or check.retcode != 0:
            raise RuntimeError(f"MT5 order_check failed: {check}")
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"MT5 order failed: {result}")
        return result

    def close(self):
        if self.mt5:
            self.mt5.shutdown()
