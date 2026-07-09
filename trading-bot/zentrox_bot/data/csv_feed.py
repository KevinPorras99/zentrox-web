"""CSV-backed data feed for backtesting with your own historical data.

Expected columns (header required, order flexible):
    timestamp, open, high, low, close, volume

``timestamp`` may be epoch seconds, epoch milliseconds, or an ISO-8601 string.
One file per symbol; map symbols to file paths when constructing the feed.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from ..indicators import resample
from ..models import Candle
from .base import DataFeed


def _parse_ts(raw: str) -> int:
    raw = raw.strip()
    try:
        val = float(raw)
        # Heuristic: treat large numbers as milliseconds.
        return int(val / 1000) if val > 1e11 else int(val)
    except ValueError:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())


class CSVFeed(DataFeed):
    def __init__(self, files: dict[str, str], base_timeframe: str) -> None:
        self.files = {s: Path(p) for s, p in files.items()}
        self.base_timeframe = base_timeframe
        self._cache: dict[str, list[Candle]] = {}

    def symbols(self) -> Sequence[str]:
        return list(self.files)

    def _load(self, symbol: str) -> list[Candle]:
        path = self.files[symbol]
        candles: list[Candle] = []
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            fields = {name.lower(): name for name in (reader.fieldnames or [])}
            ts_key = fields.get("timestamp") or fields.get("time") or fields.get("date")
            if ts_key is None:
                raise ValueError(f"{path}: missing timestamp column")
            for row in reader:
                candles.append(Candle(
                    ts=_parse_ts(row[ts_key]),
                    open=float(row[fields["open"]]),
                    high=float(row[fields["high"]]),
                    low=float(row[fields["low"]]),
                    close=float(row[fields["close"]]),
                    volume=float(row.get(fields.get("volume", ""), 0) or 0),
                ))
        candles.sort(key=lambda c: c.ts)
        return candles

    def get_candles(self, symbol: str, timeframe: str) -> list[Candle]:
        if symbol not in self.files:
            raise KeyError(f"unknown symbol {symbol}")
        base = self._cache.get(symbol)
        if base is None:
            base = self._load(symbol)
            self._cache[symbol] = base
        if timeframe == self.base_timeframe:
            return list(base)
        return resample(base, timeframe)
