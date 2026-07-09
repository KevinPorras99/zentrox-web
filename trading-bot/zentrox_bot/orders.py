"""Order manager (gestor de órdenes) with a paper-trading broker.

Handles the full lifecycle of a position: entry fills (with commission and
adverse slippage), and per-bar management of stop-loss, take-profit, optional
trailing stop, configurable partial exits and an optional time stop.

Intrabar resolution is deliberately *pessimistic*: if a single bar's range
touches both the stop and the target, the stop is assumed to fill first. This
keeps backtests honest rather than optimistic.
"""

from __future__ import annotations

from typing import Optional

from .config import ExecutionConfig, StrategyConfig
from .models import (
    Candle,
    ExitReason,
    Position,
    Side,
    Signal,
    Trade,
)


class OrderManager:
    def __init__(self, execution: ExecutionConfig, strategy: StrategyConfig) -> None:
        self.execution = execution
        self.strategy = strategy

    # -- entry -------------------------------------------------------------
    def open(self, signal: Signal, qty: float, ref_price: float, ts: int) -> Position:
        fill = self._apply_slippage(ref_price, signal.side, entering=True)
        entry_fee = fill * qty * self.execution.commission
        return Position(
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            entry=fill,
            stop=signal.stop,
            take_profit=signal.take_profit,
            opened_ts=ts,
            reason=signal.reason,
            partials=list(signal.partials),
            extreme=fill,
            risk_per_unit=abs(fill - signal.stop),
            initial_qty=qty,
            entry_fee=entry_fee,
        )

    # -- per-bar management ------------------------------------------------
    def update(
        self, pos: Position, candle: Candle, atr: Optional[float] = None
    ) -> list[Trade]:
        pos.bars_held += 1
        trades: list[Trade] = []

        # Track the running extreme for trailing logic.
        if pos.side is Side.LONG:
            pos.extreme = max(pos.extreme, candle.high)
        else:
            pos.extreme = min(pos.extreme, candle.low)

        if self.strategy.use_trailing_stop and atr:
            self._apply_trailing(pos, atr)

        # 1) Stop-loss first (pessimistic).
        if self._stop_hit(pos, candle):
            trades.append(self._close(pos, pos.stop, candle.ts, ExitReason.STOP_LOSS,
                                      pos.qty))
            return trades

        # 2) Partial targets.
        for price, frac in list(pos.partials):
            if self._level_reached(pos, candle, price):
                chunk = min(frac * pos.initial_qty, pos.qty)
                if chunk > 0:
                    trades.append(self._close(pos, price, candle.ts,
                                              ExitReason.PARTIAL, chunk))
                pos.partials.remove((price, frac))
                if pos.qty <= 0:
                    return trades

        # 3) Take-profit.
        if self._level_reached(pos, candle, pos.take_profit):
            trades.append(self._close(pos, pos.take_profit, candle.ts,
                                      ExitReason.TAKE_PROFIT, pos.qty))
            return trades

        # 4) Time stop.
        max_bars = self.strategy.max_holding_bars
        if max_bars and pos.bars_held >= max_bars:
            trades.append(self._close(pos, candle.close, candle.ts,
                                      ExitReason.TIME_STOP, pos.qty))
        return trades

    def force_close(self, pos: Position, price: float, ts: int) -> Trade:
        return self._close(pos, price, ts, ExitReason.END_OF_DATA, pos.qty)

    # -- helpers -----------------------------------------------------------
    def _apply_trailing(self, pos: Position, atr: float) -> None:
        dist = self.strategy.trailing_atr_mult * atr
        if pos.side is Side.LONG:
            pos.stop = max(pos.stop, pos.extreme - dist)
        else:
            pos.stop = min(pos.stop, pos.extreme + dist)

    def _stop_hit(self, pos: Position, candle: Candle) -> bool:
        if pos.side is Side.LONG:
            return candle.low <= pos.stop
        return candle.high >= pos.stop

    def _level_reached(self, pos: Position, candle: Candle, price: float) -> bool:
        if pos.side is Side.LONG:
            return candle.high >= price
        return candle.low <= price

    def _apply_slippage(self, price: float, side: Side, entering: bool) -> float:
        slip = self.execution.slippage
        # Entering long or exiting short => you pay up. And vice-versa.
        worse_up = (side is Side.LONG) == entering
        return price * (1 + slip) if worse_up else price * (1 - slip)

    def _close(
        self,
        pos: Position,
        price: float,
        ts: int,
        reason: ExitReason,
        qty: float,
    ) -> Trade:
        qty = min(qty, pos.qty)
        exit_fill = self._apply_slippage(price, pos.side, entering=False)
        exit_fee = exit_fill * qty * self.execution.commission
        # Allocate the entry fee proportionally to the chunk being closed.
        entry_fee_share = pos.entry_fee * (qty / pos.initial_qty) if pos.initial_qty else 0.0
        gross = (exit_fill - pos.entry) * pos.side.sign * qty
        fees = entry_fee_share + exit_fee
        pnl = gross - fees
        r_multiple = 0.0
        if pos.risk_per_unit > 0:
            r_multiple = (exit_fill - pos.entry) * pos.side.sign / pos.risk_per_unit
        pos.qty -= qty
        return Trade(
            symbol=pos.symbol,
            side=pos.side,
            qty=qty,
            entry=pos.entry,
            exit=exit_fill,
            opened_ts=pos.opened_ts,
            closed_ts=ts,
            pnl=pnl,
            fees=fees,
            reason=pos.reason,
            exit_reason=reason,
            r_multiple=r_multiple,
        )
