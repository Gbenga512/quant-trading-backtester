from dataclasses import dataclass
from datetime import date

@dataclass
class RiskState:
    day: date
    day_start_equity: float
    high_watermark: float
    halted: bool = False
    halt_reason: str = ""

class RiskManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.state = None

    def update(self, equity, today=None):
        today = today or date.today()
        if self.state is None or self.state.day != today:
            self.state = RiskState(today, equity, equity)
        self.state.high_watermark = max(self.state.high_watermark, equity)
        daily_loss = max(0.0, (self.state.day_start_equity-equity)/max(self.state.day_start_equity, 1e-9))
        drawdown = max(0.0, (self.state.high_watermark-equity)/max(self.state.high_watermark, 1e-9))
        if daily_loss >= self.cfg.max_daily_loss:
            self.state.halted, self.state.halt_reason = True, "DAILY_LOSS_LIMIT"
        if drawdown >= self.cfg.max_equity_drawdown:
            self.state.halted, self.state.halt_reason = True, "EQUITY_DRAWDOWN_LIMIT"
        return {"daily_loss": daily_loss, "drawdown": drawdown, "halted": self.state.halted,
                "halt_reason": self.state.halt_reason}

    def approve(self, equity, open_positions, symbol_positions, spread_points):
        if self.state is None or self.state.halted:
            return False, "RISK_STATE_HALTED_OR_UNINITIALISED"
        if len(open_positions) >= self.cfg.max_positions:
            return False, "MAX_OPEN_POSITIONS"
        if symbol_positions >= self.cfg.max_positions_per_symbol:
            return False, "MAX_POSITIONS_FOR_SYMBOL"
        if spread_points is None or spread_points > self.cfg.max_spread_points:
            return False, "SPREAD_LIMIT"
        if equity <= 0:
            return False, "INVALID_EQUITY"
        return True, "APPROVED"

    @staticmethod
    def volume_from_mt5(mt5, symbol, side, entry, stop, equity, risk_fraction, info):
        """Use broker-calculated loss for 1 lot; never guess pip value."""
        order_type = mt5.ORDER_TYPE_BUY if side == "BUY" else mt5.ORDER_TYPE_SELL
        one_lot_loss = abs(mt5.order_calc_profit(order_type, symbol, 1.0, entry, stop) or 0.0)
        if one_lot_loss <= 0:
            raise ValueError("MT5 could not calculate stop-loss value")
        raw = equity * risk_fraction / one_lot_loss
        step = info.volume_step
        volume = (raw // step) * step
        volume = min(info.volume_max, max(0.0, volume))
        if volume < info.volume_min:
            raise ValueError("Calculated volume is below broker minimum")
        return round(volume, 8)
