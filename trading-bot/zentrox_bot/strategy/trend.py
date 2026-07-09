"""Trend / market-regime detection.

Classifies a timeframe as up-trend, down-trend or range using the relationship
and slope of two EMAs. This is what lets the bot *adapt or abstain* depending
on the regime (adaptación al mercado).
"""

from __future__ import annotations

from typing import Sequence

from ..indicators import ema, slope
from ..models import Candle, Trend


def detect_trend(
    candles: Sequence[Candle],
    fast: int,
    slow: int,
    slope_min: float = 0.0,
    slope_lookback: int = 5,
) -> Trend:
    if len(candles) < slow + slope_lookback:
        return Trend.RANGE
    closes = [c.close for c in candles]
    ef = ema(closes, fast)
    es = ema(closes, slow)
    if ef[-1] is None or es[-1] is None:
        return Trend.RANGE
    sl = slope(ef, slope_lookback) or 0.0
    if ef[-1] > es[-1] and sl > slope_min:
        return Trend.UP
    if ef[-1] < es[-1] and sl < -slope_min:
        return Trend.DOWN
    return Trend.RANGE
