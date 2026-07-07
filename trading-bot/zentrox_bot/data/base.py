"""Abstract data feed interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from ..models import Candle


class DataFeed(ABC):
    """A source of OHLCV candles for one or more symbols.

    Implementations must return candles sorted ascending by timestamp for the
    requested symbol and timeframe.
    """

    @abstractmethod
    def symbols(self) -> Sequence[str]:
        ...

    @abstractmethod
    def get_candles(self, symbol: str, timeframe: str) -> list[Candle]:
        ...
