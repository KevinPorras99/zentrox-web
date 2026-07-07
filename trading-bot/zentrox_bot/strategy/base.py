"""Strategy interface and the context passed to it on every evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from ..config import StrategyConfig
from ..models import Candle, Signal


@dataclass
class StrategyContext:
    """Everything a strategy needs to make a decision at one point in time.

    All candle lists are *closed* candles up to and including the current
    moment, sorted ascending. The operational timeframe drives the loop; the
    higher timeframes are provided already aligned to the same instant.
    """

    symbol: str
    config: StrategyConfig
    op: Sequence[Candle]     # operational timeframe (e.g. 15m)
    mtf: Sequence[Candle]    # intermediate timeframe (e.g. 4h)
    htf: Sequence[Candle]    # higher timeframe (e.g. 1d)

    @property
    def price(self) -> float:
        return self.op[-1].close


class Strategy(ABC):
    """Base class for trading strategies.

    A strategy only *proposes* trades via :class:`Signal`. Position sizing and
    the final go/no-go decision belong to the risk manager, keeping the two
    concerns cleanly separated (as in the reference architecture).
    """

    name: str = "strategy"

    @abstractmethod
    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        """Return a :class:`Signal` to enter, or ``None`` to stand aside."""
