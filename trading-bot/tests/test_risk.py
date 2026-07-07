import unittest

from zentrox_bot.config import RiskConfig
from zentrox_bot.models import ExitReason, Side, Signal, Trade
from zentrox_bot.risk import RiskManager


def _signal(entry=100.0, stop=95.0, tp=115.0):
    return Signal(symbol="BTC/USDT", side=Side.LONG, entry=entry, stop=stop,
                  take_profit=tp, ts=0)


def _loss_trade():
    return Trade(symbol="BTC/USDT", side=Side.LONG, qty=1, entry=100, exit=95,
                 opened_ts=0, closed_ts=1, pnl=-50, fees=0, reason="",
                 exit_reason=ExitReason.STOP_LOSS, r_multiple=-1)


class TestRisk(unittest.TestCase):
    def test_position_sizing(self):
        rm = RiskManager(RiskConfig(risk_per_trade=0.01), 10_000)
        d = rm.evaluate(_signal(100, 95, 115), ts=0)   # risk/unit = 5
        self.assertTrue(d.approved)
        # 1% of 10k = 100 risk; 100 / 5 = 20 units.
        self.assertAlmostEqual(d.qty, 20.0)

    def test_rr_gate_rejects_low_rr(self):
        rm = RiskManager(RiskConfig(min_rr=2.0), 10_000)
        # entry 100, stop 95 (risk 5), tp 105 (reward 5) => RR 1.0 < 2.
        d = rm.evaluate(_signal(100, 95, 105), ts=0)
        self.assertFalse(d.approved)
        self.assertIn("RR", d.reason)

    def test_missing_stop_rejected(self):
        rm = RiskManager(RiskConfig(), 10_000)
        d = rm.evaluate(_signal(100, 100, 120), ts=0)
        self.assertFalse(d.approved)

    def test_consecutive_losses_pause(self):
        rm = RiskManager(RiskConfig(max_consecutive_losses=2), 10_000)
        rm.on_trade_closed(_loss_trade())
        rm.on_trade_closed(_loss_trade())
        d = rm.evaluate(_signal(), ts=0)
        self.assertFalse(d.approved)
        self.assertIn("consecutive", d.reason)

    def test_daily_loss_limit(self):
        rm = RiskManager(RiskConfig(daily_loss_limit=0.05), 10_000)
        rm.check_gates(ts=0)                    # establishes the day baseline
        rm.on_equity(9_400)                     # -6% on the day
        d = rm.evaluate(_signal(), ts=0)
        self.assertFalse(d.approved)
        self.assertIn("daily", d.reason)

    def test_drawdown_halt_is_sticky(self):
        rm = RiskManager(RiskConfig(max_drawdown_pause=0.2), 10_000)
        rm.on_equity(7_000)                     # -30% drawdown
        self.assertFalse(rm.evaluate(_signal(), ts=0).approved)
        self.assertTrue(rm.halted)
        # Even after recovery, it stays halted (manual intervention required).
        rm.on_equity(10_000)
        self.assertFalse(rm.evaluate(_signal(), ts=0).approved)

    def test_never_increase_size_after_loss(self):
        rm = RiskManager(RiskConfig(risk_per_trade=0.01, max_consecutive_losses=9), 10_000)
        before = rm.evaluate(_signal(100, 95, 115), ts=0).qty
        rm.balance_pnl(-500)
        rm.on_equity(9_500)
        rm.on_trade_closed(_loss_trade())
        after = rm.evaluate(_signal(100, 95, 115), ts=0).qty
        self.assertLess(after, before)          # size shrinks with equity, never grows


if __name__ == "__main__":
    unittest.main()
