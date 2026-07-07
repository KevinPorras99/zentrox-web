"""Core domain models for the Zentrox trading bot.

All models are plain dataclasses using only the standard library so the bot
can run and be tested without any third-party dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Side(str, Enum):
    """Direction of a position / order."""

    LONG = "long"
    SHORT = "short"

    @property
    def sign(self) -> int:
        """+1 for long, -1 for short. Handy for PnL math."""
        return 1 if self is Side.LONG else -1


class Trend(str, Enum):
    """Market regime detected by the strategy."""

    UP = "up"          # tendencia alcista
    DOWN = "down"      # tendencia bajista
    RANGE = "range"    # mercado lateral


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class ExitReason(str, Enum):
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    PARTIAL = "partial"
    TIME_STOP = "time_stop"
    MANUAL = "manual"
    END_OF_DATA = "end_of_data"


@dataclass(frozen=True)
class Candle:
    """A single OHLCV bar. ``ts`` is the open time in epoch seconds (UTC)."""

    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def range(self) -> float:
        return self.high - self.low


@dataclass
class Signal:
    """A trade intention produced by the strategy.

    The strategy only proposes; the risk manager decides the final size and
    whether the trade is allowed at all.
    """

    symbol: str
    side: Side
    entry: float
    stop: float
    take_profit: float
    reason: str = ""
    ts: int = 0
    # Optional scale-out targets as (price, fraction_of_position) pairs.
    partials: list[tuple[float, float]] = field(default_factory=list)

    @property
    def risk_per_unit(self) -> float:
        """Absolute price distance between entry and stop."""
        return abs(self.entry - self.stop)

    @property
    def reward_per_unit(self) -> float:
        return abs(self.take_profit - self.entry)

    @property
    def rr(self) -> float:
        """Reward-to-risk ratio. 0 if the stop is invalid (zero distance)."""
        risk = self.risk_per_unit
        if risk <= 0:
            return 0.0
        return self.reward_per_unit / risk


@dataclass
class Order:
    symbol: str
    side: Side
    qty: float
    type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    fill_price: Optional[float] = None
    ts: int = 0


@dataclass
class Position:
    """An open position with its protective and target levels."""

    symbol: str
    side: Side
    qty: float
    entry: float
    stop: float
    take_profit: float
    opened_ts: int
    reason: str = ""
    # Remaining scale-out targets not yet hit.
    partials: list[tuple[float, float]] = field(default_factory=list)
    # Highest (long) / lowest (short) price seen, used by the trailing stop.
    extreme: float = 0.0
    risk_per_unit: float = 0.0
    # Execution accounting.
    initial_qty: float = 0.0
    entry_fee: float = 0.0
    bars_held: int = 0

    def unrealized(self, price: float) -> float:
        return (price - self.entry) * self.side.sign * self.qty


@dataclass
class Trade:
    """A closed (fully or partially) trade, i.e. a journal entry / result."""

    symbol: str
    side: Side
    qty: float
    entry: float
    exit: float
    opened_ts: int
    closed_ts: int
    pnl: float
    fees: float
    reason: str
    exit_reason: ExitReason
    r_multiple: float = 0.0

    @property
    def is_win(self) -> bool:
        return self.pnl > 0
