"""Monitor (monitor) — health, status and safety-rule enforcement.

Watches the account/risk state, emits alerts on important transitions, and
enforces the hard safety invariants from the specification:

* every open position must carry a stop-loss (never removed),
* the bot pauses when drawdown / loss limits are exceeded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .alerts import Alerts
from .models import Position, Trade
from .risk import RiskManager


@dataclass
class MonitorState:
    halted: bool = False
    paused_streak: bool = False
    paused_daily: bool = False


class SafetyViolation(RuntimeError):
    """Raised when a hard safety invariant would be broken."""


class Monitor:
    def __init__(self, risk: RiskManager, alerts: Alerts) -> None:
        self.risk = risk
        self.alerts = alerts
        self.state = MonitorState()

    def assert_protected(self, pos: Position) -> None:
        # No eliminar stop-loss: a position without a valid protective stop is
        # never allowed to exist.
        if pos.stop is None or pos.risk_per_unit <= 0:
            raise SafetyViolation(f"position on {pos.symbol} has no valid stop-loss")

    def on_trade(self, trade: Trade) -> None:
        verb = "WIN" if trade.is_win else "LOSS"
        self.alerts.info(
            f"[{verb}] {trade.symbol} {trade.side.value} "
            f"pnl={trade.pnl:.2f} ({trade.r_multiple:+.2f}R) "
            f"exit={trade.exit_reason.value}"
        )

    def check(self, ts: int) -> None:
        """Detect state transitions and alert once on each."""
        if self.risk.halted and not self.state.halted:
            self.state.halted = True
            self.alerts.error(f"BOT HALTED: {self.risk.halt_reason}")

        streak = self.risk.consecutive_losses >= self.risk.config.max_consecutive_losses
        if streak and not self.state.paused_streak:
            self.state.paused_streak = True
            self.alerts.warning(
                f"Paused: {self.risk.consecutive_losses} consecutive losses"
            )
        elif not streak:
            self.state.paused_streak = False

        daily = self.risk.daily_loss >= self.risk.config.daily_loss_limit
        if daily and not self.state.paused_daily:
            self.state.paused_daily = True
            self.alerts.warning(f"Daily loss limit reached: {self.risk.daily_loss:.1%}")
        elif not daily:
            self.state.paused_daily = False

    def status(self) -> dict[str, Any]:
        return {
            "equity": round(self.risk.equity, 2),
            "peak_equity": round(self.risk.peak_equity, 2),
            "drawdown": round(self.risk.drawdown, 4),
            "daily_loss": round(self.risk.daily_loss, 4),
            "consecutive_losses": self.risk.consecutive_losses,
            "halted": self.risk.halted,
        }
