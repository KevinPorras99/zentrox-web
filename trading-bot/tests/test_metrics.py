import math
import unittest

from zentrox_bot.metrics import compute_metrics, max_drawdown
from zentrox_bot.models import ExitReason, Side, Trade


def _t(pnl, r=0.0, fees=0.0):
    return Trade(symbol="X", side=Side.LONG, qty=1, entry=100, exit=100 + pnl,
                 opened_ts=0, closed_ts=1, pnl=pnl, fees=fees, reason="",
                 exit_reason=ExitReason.TAKE_PROFIT, r_multiple=r)


class TestMetrics(unittest.TestCase):
    def test_max_drawdown(self):
        curve = [100, 120, 90, 110, 80]
        # Peak 120 -> trough 80 => 33.3%.
        self.assertAlmostEqual(max_drawdown(curve), (120 - 80) / 120)

    def test_profit_factor_and_winrate(self):
        trades = [_t(30, 3), _t(-10, -1), _t(20, 2), _t(-10, -1)]
        m = compute_metrics(trades, [10_000, 10_030, 10_020, 10_040, 10_030], 10_000)
        self.assertEqual(m.trades, 4)
        self.assertEqual(m.wins, 2)
        self.assertAlmostEqual(m.win_rate, 0.5)
        self.assertAlmostEqual(m.gross_profit, 50)
        self.assertAlmostEqual(m.gross_loss, 20)
        self.assertAlmostEqual(m.profit_factor, 2.5)
        self.assertAlmostEqual(m.net_profit, 30)
        self.assertAlmostEqual(m.expectancy, 7.5)

    def test_profit_factor_infinite_without_losses(self):
        m = compute_metrics([_t(10, 1), _t(5, 1)], [10_000, 10_010, 10_015], 10_000)
        self.assertTrue(math.isinf(m.profit_factor))

    def test_empty(self):
        m = compute_metrics([], [10_000], 10_000)
        self.assertEqual(m.trades, 0)
        self.assertEqual(m.net_profit, 0)


if __name__ == "__main__":
    unittest.main()
