import unittest

from zentrox_bot.backtest import Backtester, walk_forward
from zentrox_bot.config import BotConfig
from zentrox_bot.data import SyntheticFeed
from zentrox_bot.strategy import TrendFollowingStrategy


def _feed(bars=3000, seed=7, symbols=("BTC/USDT",)):
    return SyntheticFeed(symbols=symbols, base_timeframe="15m", bars=bars, seed=seed)


def _config(symbols=("BTC/USDT",)):
    cfg = BotConfig(symbols=list(symbols), initial_equity=10_000)
    cfg.strategy.operational = "15m"
    return cfg


class TestBacktest(unittest.TestCase):
    def test_runs_and_reports(self):
        bt = Backtester(_feed(), _config(), TrendFollowingStrategy())
        res = bt.run()
        self.assertTrue(res.equity_curve)
        self.assertGreaterEqual(res.metrics.trades, 0)
        # Equity curve values are finite and positive.
        self.assertTrue(all(e > 0 for _, e in res.equity_curve))

    def test_deterministic(self):
        r1 = Backtester(_feed(), _config(), TrendFollowingStrategy()).run()
        r2 = Backtester(_feed(), _config(), TrendFollowingStrategy()).run()
        self.assertEqual(r1.metrics.trades, r2.metrics.trades)
        self.assertAlmostEqual(r1.final_equity, r2.final_equity)

    def test_no_stopless_positions_and_capital_preserved(self):
        # With mandatory stops and 1% risk, a single trade can never lose more
        # than ~1% of equity, so the account can't be wiped out in one shot.
        cfg = _config()
        cfg.risk.risk_per_trade = 0.01
        res = Backtester(_feed(seed=3), cfg, TrendFollowingStrategy()).run()
        worst = min((t.pnl for t in res.trades), default=0.0)
        # Allow slack for slippage/fees beyond the nominal 1%.
        self.assertGreater(worst, -0.05 * cfg.initial_equity)

    def test_multi_symbol(self):
        symbols = ("BTC/USDT", "ETH/USDT")
        res = Backtester(_feed(symbols=symbols), _config(symbols),
                         TrendFollowingStrategy()).run()
        self.assertTrue(res.equity_curve)

    def test_walk_forward_folds(self):
        folds = walk_forward(_feed(), _config(), TrendFollowingStrategy, folds=3)
        self.assertEqual(len(folds), 3)


if __name__ == "__main__":
    unittest.main()
