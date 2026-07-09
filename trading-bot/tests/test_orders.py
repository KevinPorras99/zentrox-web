import unittest

from zentrox_bot.config import ExecutionConfig, StrategyConfig
from zentrox_bot.models import Candle, ExitReason, Side, Signal
from zentrox_bot.orders import OrderManager


def _c(ts, o, h, l, c):
    return Candle(ts=ts, open=o, high=h, low=l, close=c, volume=1.0)


def _mgr(commission=0.0, slippage=0.0, **strat):
    return OrderManager(ExecutionConfig(commission=commission, slippage=slippage),
                        StrategyConfig(**strat))


def _long(entry=100.0, stop=90.0, tp=130.0, partials=None):
    return Signal(symbol="X", side=Side.LONG, entry=entry, stop=stop,
                  take_profit=tp, partials=partials or [], ts=0)


class TestOrders(unittest.TestCase):
    def test_stop_loss_fills_and_pnls(self):
        m = _mgr()
        pos = m.open(_long(), qty=1, ref_price=100, ts=0)
        self.assertAlmostEqual(pos.risk_per_unit, 10)
        trades = m.update(pos, _c(1, 100, 101, 89, 95))
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].exit_reason, ExitReason.STOP_LOSS)
        self.assertAlmostEqual(trades[0].pnl, -10)
        self.assertAlmostEqual(trades[0].r_multiple, -1.0)

    def test_take_profit(self):
        m = _mgr()
        pos = m.open(_long(), qty=1, ref_price=100, ts=0)
        trades = m.update(pos, _c(1, 100, 131, 100, 120))
        self.assertEqual(trades[0].exit_reason, ExitReason.TAKE_PROFIT)
        self.assertAlmostEqual(trades[0].pnl, 30)

    def test_stop_before_target_when_both_touched(self):
        m = _mgr()
        pos = m.open(_long(), qty=1, ref_price=100, ts=0)
        # Bar spans both 89 (stop) and 131 (tp): stop must win (pessimistic).
        trades = m.update(pos, _c(1, 100, 131, 89, 120))
        self.assertEqual(trades[0].exit_reason, ExitReason.STOP_LOSS)

    def test_partial_then_runner(self):
        m = _mgr()
        pos = m.open(_long(partials=[(120, 0.5)]), qty=1, ref_price=100, ts=0)
        t1 = m.update(pos, _c(1, 100, 125, 115, 118))     # hits partial, not tp
        self.assertEqual(len(t1), 1)
        self.assertEqual(t1[0].exit_reason, ExitReason.PARTIAL)
        self.assertAlmostEqual(t1[0].qty, 0.5)
        self.assertAlmostEqual(pos.qty, 0.5)
        t2 = m.update(pos, _c(2, 118, 131, 118, 130))     # runner hits tp
        self.assertEqual(t2[0].exit_reason, ExitReason.TAKE_PROFIT)
        self.assertAlmostEqual(t2[0].qty, 0.5)

    def test_commission_and_slippage_hurt_pnl(self):
        clean = _mgr()
        costed = _mgr(commission=0.001, slippage=0.001)
        p1 = clean.open(_long(), 1, 100, 0)
        p2 = costed.open(_long(), 1, 100, 0)
        self.assertGreater(p2.entry, p1.entry)            # buy fills higher
        t1 = clean.update(p1, _c(1, 100, 131, 100, 120))[0]
        t2 = costed.update(p2, _c(1, 100, 131, 100, 120))[0]
        self.assertLess(t2.pnl, t1.pnl)                   # costs reduce profit
        self.assertGreater(t2.fees, 0)

    def test_time_stop(self):
        m = _mgr(max_holding_bars=2)
        pos = m.open(_long(), qty=1, ref_price=100, ts=0)
        self.assertEqual(m.update(pos, _c(1, 100, 105, 99, 101)), [])
        trades = m.update(pos, _c(2, 101, 106, 100, 103))
        self.assertEqual(trades[0].exit_reason, ExitReason.TIME_STOP)

    def test_trailing_stop_ratchets_up(self):
        m = _mgr(use_trailing_stop=True, trailing_atr_mult=1.0)
        pos = m.open(_long(stop=90), qty=1, ref_price=100, ts=0)
        m.update(pos, _c(1, 100, 120, 100, 118), atr=5.0)  # extreme 120 -> stop 115
        self.assertAlmostEqual(pos.stop, 115)
        trades = m.update(pos, _c(2, 118, 119, 114, 116), atr=5.0)  # low 114 < 115
        self.assertEqual(trades[0].exit_reason, ExitReason.STOP_LOSS)


if __name__ == "__main__":
    unittest.main()
