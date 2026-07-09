"""Optional live/historical exchange feed via ccxt.

This module is imported lazily and is the *only* place that needs the optional
``ccxt`` dependency. Everything else in the bot runs without it. Install with:

    pip install ccxt

Note: this feed pulls OHLCV over the network; it is intended for fetching real
historical data for backtests and for a future live loop. Order execution
against a real exchange is intentionally NOT implemented here — going live
requires explicit, audited work and API keys with the right permissions.
"""

from __future__ import annotations

from typing import Sequence

from ..indicators import resample
from ..models import Candle
from .base import DataFeed


class CCXTFeed(DataFeed):
    def __init__(
        self,
        exchange_id: str,
        symbols: Sequence[str],
        base_timeframe: str = "15m",
        limit: int = 1000,
        params: dict | None = None,
    ) -> None:
        try:
            import ccxt  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "ccxt is required for CCXTFeed. Install with `pip install ccxt`."
            ) from exc
        self.exchange = getattr(ccxt, exchange_id)(params or {})
        self._symbols = list(symbols)
        self.base_timeframe = base_timeframe
        self.limit = limit
        self._cache: dict[str, list[Candle]] = {}

    def symbols(self) -> Sequence[str]:
        return list(self._symbols)

    def _fetch(self, symbol: str) -> list[Candle]:
        raw = self.exchange.fetch_ohlcv(
            symbol, timeframe=self.base_timeframe, limit=self.limit
        )
        return [
            Candle(ts=int(ts // 1000), open=o, high=h, low=lo, close=c, volume=v)
            for ts, o, h, lo, c, v in raw
        ]

    def get_candles(self, symbol: str, timeframe: str) -> list[Candle]:
        if symbol not in self._symbols:
            raise KeyError(f"unknown symbol {symbol}")
        base = self._cache.get(symbol)
        if base is None:
            base = self._fetch(symbol)
            self._cache[symbol] = base
        if timeframe == self.base_timeframe:
            return list(base)
        return resample(base, timeframe)
