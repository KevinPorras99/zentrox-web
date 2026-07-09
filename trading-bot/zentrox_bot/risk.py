"""Risk manager (gestor de riesgo).

Owns capital-preservation rules that are independent of any single strategy:

* fixed-fractional position sizing from the stop distance,
* mandatory stop-loss and minimum reward/risk gate,
* pause after N consecutive losses,
* daily loss limit,
* global drawdown circuit-breaker,
* never increase risk after losses (sizing is always off current equity, and
  the account halts instead of "revenge trading").
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .config import RiskConfig
from .models import Signal, Trade


@dataclass
class RiskDecision:
    approved: bool
    qty: float = 0.0
    reason: str = ""


class RiskManager:
    def __init__(self, config: RiskConfig, initial_equity: float) -> None:
        self.config = config
        # ``balance`` is realized (closed) equity; ``equity`` is marked-to-market
        # including open positions. Sizing and limits use ``equity``.
        self.balance = initial_equity
        self.equity = initial_equity
        self.peak_equity = initial_equity
        self.consecutive_losses = 0
        self._day_key: str | None = None
        self._day_start_equity = initial_equity
        self.halted = False
        self.halt_reason = ""

    # -- account updates ---------------------------------------------------
    def _roll_day(self, ts: int) -> None:
        key = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        if key != self._day_key:
            self._day_key = key
            self._day_start_equity = self.equity

    def on_equity(self, equity: float) -> None:
        self.equity = equity
        self.peak_equity = max(self.peak_equity, equity)

    def balance_pnl(self, pnl: float) -> None:
        """Apply a realized PnL from a closed trade to the account balance."""
        self.balance += pnl

    def on_trade_closed(self, trade: Trade) -> None:
        """Update streak counters when a trade fully closes."""
        if trade.pnl < 0:
            self.consecutive_losses += 1
        elif trade.pnl > 0:
            self.consecutive_losses = 0

    @property
    def drawdown(self) -> float:
        if self.peak_equity <= 0:
            return 0.0
        return (self.peak_equity - self.equity) / self.peak_equity

    @property
    def daily_loss(self) -> float:
        if self._day_start_equity <= 0:
            return 0.0
        return (self._day_start_equity - self.equity) / self._day_start_equity

    # -- gating ------------------------------------------------------------
    def check_gates(self, ts: int) -> RiskDecision:
        self._roll_day(ts)
        if self.halted:
            return RiskDecision(False, reason=f"halted: {self.halt_reason}")
        if self.drawdown >= self.config.max_drawdown_pause:
            self.halted = True
            self.halt_reason = f"max drawdown {self.drawdown:.1%}"
            return RiskDecision(False, reason=self.halt_reason)
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            return RiskDecision(
                False, reason=f"{self.consecutive_losses} consecutive losses (paused)"
            )
        if self.daily_loss >= self.config.daily_loss_limit:
            return RiskDecision(
                False, reason=f"daily loss limit hit ({self.daily_loss:.1%})"
            )
        return RiskDecision(True)

    # -- sizing ------------------------------------------------------------
    def evaluate(self, signal: Signal, ts: int) -> RiskDecision:
        gate = self.check_gates(ts)
        if not gate.approved:
            return gate
        if signal.risk_per_unit <= 0:
            return RiskDecision(False, reason="missing/invalid stop-loss")
        if signal.rr < self.config.min_rr:
            return RiskDecision(
                False, reason=f"RR {signal.rr:.2f} below minimum {self.config.min_rr}"
            )
        risk_amount = self.equity * self.config.risk_per_trade
        qty = risk_amount / signal.risk_per_unit
        if qty <= 0:
            return RiskDecision(False, reason="computed size is zero")
        return RiskDecision(True, qty=qty, reason="approved")
