"""Deterministic synthetic price feed.

Generates reproducible OHLCV data with configurable trend and volatility so the
strategy, backtester and tests can run fully offline. It uses a seeded
``random.Random`` (no numpy) so results are stable across machines.
"""

from __future__ import annotations

import math
import random
from typing import Sequence

from ..indicators import resample, timeframe_seconds
from ..models import Candle
from .base import DataFeed


class SyntheticFeed(DataFeed):
    def __init__(
        self,
        symbols: Sequence[str] = ("BTC/USDT",),
        base_timeframe: str = "15m",
        bars: int = 4000,
        start_price: float = 30_000.0,
        drift: float = 0.00003,      # per-bar log drift (trend)
        volatility: float = 0.004,   # per-bar volatility
        seed: int = 42,
        start_ts: int = 1_700_000_000,
    ) -> None:
        self._symbols = list(symbols)
        self.base_timeframe = base_timeframe
        self.bars = bars
        self.start_price = start_price
        self.drift = drift
        self.volatility = volatility
        self.seed = seed
        self.start_ts = start_ts
        self._cache: dict[str, list[Candle]] = {}

    def symbols(self) -> Sequence[str]:
        return list(self._symbols)

    def _generate(self, symbol: str) -> list[Candle]:
        # Per-symbol deterministic seed so different symbols diverge but each is
        # reproducible run to run.
        rng = random.Random(f"{self.seed}:{symbol}")
        step = timeframe_seconds(self.base_timeframe)
        price = self.start_price
        candles: list[Candle] = []
        # Slowly varying regime cycle so the series contains up-trends,
        # down-trends and ranges (exercises the regime-adaptation logic).
        for i in range(self.bars):
            regime = math.sin(i / 400.0)      # -1..1 over ~400 bars
            drift = self.drift * regime
            shock = rng.gauss(0.0, self.volatility)
            ret = drift + shock
            new_price = max(0.01, price * math.exp(ret))
            high = max(price, new_price) * (1 + abs(rng.gauss(0, self.volatility / 2)))
            low = min(price, new_price) * (1 - abs(rng.gauss(0, self.volatility / 2)))
            volume = max(1.0, rng.gauss(1000, 250) * (1 + abs(shock) * 10))
            candles.append(Candle(
                ts=self.start_ts + i * step,
                open=round(price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(new_price, 2),
                volume=round(volume, 2),
            ))
            price = new_price
        return candles

    def get_candles(self, symbol: str, timeframe: str) -> list[Candle]:
        if symbol not in self._symbols:
            raise KeyError(f"unknown symbol {symbol}")
        base = self._cache.get(symbol)
        if base is None:
            base = self._generate(symbol)
            self._cache[symbol] = base
        if timeframe == self.base_timeframe:
            return list(base)
        return resample(base, timeframe)
