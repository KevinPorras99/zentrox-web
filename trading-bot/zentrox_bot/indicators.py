"""Technical indicators and helpers, implemented in pure Python.

These operate on plain lists of floats or :class:`~zentrox_bot.models.Candle`
objects so the bot has zero hard dependency on numpy/pandas. The functions
return series aligned to the input length, using ``None`` for warm-up periods
where a value cannot yet be computed.
"""

from __future__ import annotations

from typing import Optional, Sequence

from .models import Candle


def sma(values: Sequence[float], period: int) -> list[Optional[float]]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[Optional[float]] = []
    total = 0.0
    for i, v in enumerate(values):
        total += v
        if i >= period:
            total -= values[i - period]
        out.append(total / period if i >= period - 1 else None)
    return out


def ema(values: Sequence[float], period: int) -> list[Optional[float]]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[Optional[float]] = []
    k = 2.0 / (period + 1)
    prev: Optional[float] = None
    seed_sum = 0.0
    for i, v in enumerate(values):
        if i < period - 1:
            seed_sum += v
            out.append(None)
        elif i == period - 1:
            seed_sum += v
            prev = seed_sum / period          # seed EMA with an SMA
            out.append(prev)
        else:
            assert prev is not None
            prev = v * k + prev * (1 - k)
            out.append(prev)
    return out


def true_range(candles: Sequence[Candle]) -> list[float]:
    out: list[float] = []
    prev_close: Optional[float] = None
    for c in candles:
        if prev_close is None:
            out.append(c.high - c.low)
        else:
            out.append(max(c.high - c.low,
                           abs(c.high - prev_close),
                           abs(c.low - prev_close)))
        prev_close = c.close
    return out


def atr(candles: Sequence[Candle], period: int = 14) -> list[Optional[float]]:
    """Wilder's Average True Range."""
    tr = true_range(candles)
    out: list[Optional[float]] = [None] * len(candles)
    if len(candles) < period:
        return out
    prev = sum(tr[:period]) / period
    out[period - 1] = prev
    for i in range(period, len(candles)):
        prev = (prev * (period - 1) + tr[i]) / period
        out[i] = prev
    return out


def rsi(values: Sequence[float], period: int = 14) -> list[Optional[float]]:
    out: list[Optional[float]] = [None] * len(values)
    if len(values) <= period:
        return out
    gains = losses = 0.0
    for i in range(1, period + 1):
        ch = values[i] - values[i - 1]
        gains += max(ch, 0.0)
        losses += max(-ch, 0.0)
    avg_gain = gains / period
    avg_loss = losses / period
    out[period] = _rsi_from(avg_gain, avg_loss)
    for i in range(period + 1, len(values)):
        ch = values[i] - values[i - 1]
        avg_gain = (avg_gain * (period - 1) + max(ch, 0.0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-ch, 0.0)) / period
        out[i] = _rsi_from(avg_gain, avg_loss)
    return out


def _rsi_from(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def slope(values: Sequence[Optional[float]], lookback: int = 5) -> Optional[float]:
    """Normalized slope of the last ``lookback`` points of a series.

    Returns (last - first) / first, so the number is comparable across assets
    of different price magnitudes. ``None`` if there is not enough clean data.
    """
    clean = [v for v in values[-lookback:] if v is not None]
    if len(clean) < 2 or clean[0] == 0:
        return None
    return (clean[-1] - clean[0]) / abs(clean[0])


def swing_highs(candles: Sequence[Candle], k: int = 5) -> list[int]:
    """Indices of pivot highs: a bar whose high is the max of +/- k neighbours."""
    idx: list[int] = []
    for i in range(k, len(candles) - k):
        window = candles[i - k:i + k + 1]
        if candles[i].high == max(c.high for c in window):
            idx.append(i)
    return idx


def swing_lows(candles: Sequence[Candle], k: int = 5) -> list[int]:
    idx: list[int] = []
    for i in range(k, len(candles) - k):
        window = candles[i - k:i + k + 1]
        if candles[i].low == min(c.low for c in window):
            idx.append(i)
    return idx


# ---------------------------------------------------------------------------
# Timeframe resampling
# ---------------------------------------------------------------------------

_TF_SECONDS = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "2h": 7200, "4h": 14400, "6h": 21600, "12h": 43200,
    "1d": 86400, "1w": 604800,
}


def timeframe_seconds(tf: str) -> int:
    tf = tf.lower()
    if tf not in _TF_SECONDS:
        raise ValueError(f"unsupported timeframe: {tf}")
    return _TF_SECONDS[tf]


def resample(candles: Sequence[Candle], target_tf: str) -> list[Candle]:
    """Aggregate lower-timeframe candles into a higher timeframe.

    Buckets are aligned to epoch (UTC) boundaries. Partial trailing buckets are
    included so the most recent (still forming) candle is available to a live
    strategy; a backtester that wants only closed candles can drop the last one.
    """
    step = timeframe_seconds(target_tf)
    buckets: dict[int, list[Candle]] = {}
    order: list[int] = []
    for c in candles:
        b = (c.ts // step) * step
        if b not in buckets:
            buckets[b] = []
            order.append(b)
        buckets[b].append(c)
    out: list[Candle] = []
    for b in order:
        group = buckets[b]
        out.append(Candle(
            ts=b,
            open=group[0].open,
            high=max(g.high for g in group),
            low=min(g.low for g in group),
            close=group[-1].close,
            volume=sum(g.volume for g in group),
        ))
    return out
