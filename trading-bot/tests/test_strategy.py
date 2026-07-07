import unittest

from zentrox_bot.models import Candle, Trend
from zentrox_bot.strategy.levels import find_levels
from zentrox_bot.strategy.trend import detect_trend


def _series(closes):
    return [Candle(ts=i * 900, open=c, high=c * 1.001, low=c * 0.999, close=c,
                   volume=1.0) for i, c in enumerate(closes)]


class TestTrend(unittest.TestCase):
    def test_uptrend(self):
        candles = _series([100 + i for i in range(120)])
        self.assertEqual(detect_trend(candles, 21, 55), Trend.UP)

    def test_downtrend(self):
        candles = _series([300 - i for i in range(120)])
        self.assertEqual(detect_trend(candles, 21, 55), Trend.DOWN)

    def test_range_when_flat(self):
        candles = _series([100 for _ in range(120)])
        self.assertEqual(detect_trend(candles, 21, 55), Trend.RANGE)

    def test_insufficient_data_is_range(self):
        candles = _series([100, 101, 102])
        self.assertEqual(detect_trend(candles, 21, 55), Trend.RANGE)


class TestLevels(unittest.TestCase):
    def test_nearest_levels(self):
        closes = [10, 12, 15, 11, 8, 9, 13, 16, 12, 10, 14, 18, 13, 9, 7, 11, 15]
        candles = [Candle(ts=i, open=c, high=c + 1, low=c - 1, close=c)
                   for i, c in enumerate(closes)]
        levels = find_levels(candles, k=2, lookback=50)
        price = 12
        sup = levels.nearest_support(price)
        res = levels.nearest_resistance(price)
        if sup is not None:
            self.assertLess(sup, price)
        if res is not None:
            self.assertGreater(res, price)


if __name__ == "__main__":
    unittest.main()
