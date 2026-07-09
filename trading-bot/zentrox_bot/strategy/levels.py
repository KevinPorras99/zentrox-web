"""Support / resistance / liquidity detection.

Levels are built from recent swing pivots. The nearest resistance above price
and nearest support below price are what the strategy uses for breakout
confirmation and structural stops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from ..indicators import swing_highs, swing_lows
from ..models import Candle


@dataclass
class Levels:
    supports: list[float] = field(default_factory=list)   # sorted ascending
    resistances: list[float] = field(default_factory=list)

    def nearest_support(self, price: float) -> Optional[float]:
        below = [s for s in self.supports if s < price]
        return max(below) if below else None

    def nearest_resistance(self, price: float) -> Optional[float]:
        above = [r for r in self.resistances if r > price]
        return min(above) if above else None


def find_levels(candles: Sequence[Candle], k: int = 5, lookback: int = 120) -> Levels:
    window = list(candles[-lookback:]) if lookback else list(candles)
    highs = [window[i].high for i in swing_highs(window, k)]
    lows = [window[i].low for i in swing_lows(window, k)]
    return Levels(supports=sorted(lows), resistances=sorted(highs))
