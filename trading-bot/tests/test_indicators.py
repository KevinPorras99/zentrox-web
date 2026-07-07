import unittest

from zentrox_bot.indicators import (
    atr,
    ema,
    resample,
    sma,
    slope,
    swing_highs,
    swing_lows,
)
from zentrox_bot.models import Candle


def _c(ts, o, h, l, c, v=1.0):
    return Candle(ts=ts, open=o, high=h, low=l, close=c, volume=v)


class TestIndicators(unittest.TestCase):
    def test_sma(self):
        out = sma([1, 2, 3, 4, 5], 3)
        self.assertEqual(out[:2], [None, None])
        self.assertAlmostEqual(out[2], 2.0)
        self.assertAlmostEqual(out[4], 4.0)

    def test_ema_seeds_with_sma(self):
        out = ema([1, 2, 3, 4, 5], 3)
        self.assertIsNone(out[1])
        self.assertAlmostEqual(out[2], 2.0)          # seed = SMA of first 3
        self.assertGreater(out[4], out[2])           # rising series

    def test_atr_positive(self):
        candles = [_c(i, 10, 12, 8, 11) for i in range(20)]
        a = atr(candles, 14)
        self.assertIsNone(a[12])
        self.assertIsNotNone(a[13])
        self.assertGreater(a[-1], 0)

    def test_slope_normalized(self):
        self.assertAlmostEqual(slope([10, 11, 12], 3), 0.2)
        self.assertIsNone(slope([None, None], 3))

    def test_swings(self):
        # A clear peak at index 3 and trough at index 7.
        highs = [1, 2, 3, 9, 3, 2, 1, 0, 1, 2, 3]
        candles = [_c(i, h, h, h, h) for i, h in enumerate(highs)]
        self.assertIn(3, swing_highs(candles, 2))
        self.assertIn(7, swing_lows(candles, 2))

    def test_resample_aggregates_bucket(self):
        # Four 15m candles inside one 1h bucket [0, 3600).
        candles = [
            _c(0, 100, 105, 99, 101, 10),
            _c(900, 101, 110, 100, 108, 12),
            _c(1800, 108, 109, 95, 97, 8),
            _c(2700, 97, 103, 96, 102, 5),
        ]
        out = resample(candles, "1h")
        self.assertEqual(len(out), 1)
        bar = out[0]
        self.assertEqual(bar.ts, 0)
        self.assertEqual(bar.open, 100)
        self.assertEqual(bar.high, 110)
        self.assertEqual(bar.low, 95)
        self.assertEqual(bar.close, 102)
        self.assertEqual(bar.volume, 35)


if __name__ == "__main__":
    unittest.main()
