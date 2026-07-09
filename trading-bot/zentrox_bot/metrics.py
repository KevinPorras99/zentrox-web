"""Performance metrics (métricas).

Computes the KPIs called for in the specification: win rate, profit factor,
expectancy, maximum drawdown, Sharpe/Sortino, net profit and trade count.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from statistics import fmean, pstdev
from typing import Any, Sequence

from .models import Trade


@dataclass
class Metrics:
    trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    profit_factor: float = 0.0
    net_profit: float = 0.0
    total_fees: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0          # average $ per trade
    expectancy_r: float = 0.0        # average R per trade
    max_drawdown: float = 0.0        # fraction of peak equity
    sharpe: float = 0.0
    sortino: float = 0.0
    return_pct: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def max_drawdown(equity_curve: Sequence[float]) -> float:
    peak = -math.inf
    max_dd = 0.0
    for eq in equity_curve:
        peak = max(peak, eq)
        if peak > 0:
            max_dd = max(max_dd, (peak - eq) / peak)
    return max_dd


def _ratio(returns: Sequence[float], downside_only: bool) -> float:
    if len(returns) < 2:
        return 0.0
    mean = fmean(returns)
    if downside_only:
        downside = [min(0.0, r) for r in returns]
        denom = pstdev(downside) if any(downside) else 0.0
    else:
        denom = pstdev(returns)
    if denom == 0:
        return 0.0
    # Annualization is intentionally omitted; these are per-trade ratios and
    # are only meaningful relative to each other across runs.
    return mean / denom


def compute_metrics(
    trades: Sequence[Trade],
    equity_curve: Sequence[float],
    initial_equity: float,
) -> Metrics:
    m = Metrics()
    m.trades = len(trades)
    if not trades:
        m.max_drawdown = max_drawdown(equity_curve) if equity_curve else 0.0
        return m

    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]
    m.wins = len(wins)
    m.losses = len(losses)
    m.win_rate = m.wins / m.trades
    m.gross_profit = sum(t.pnl for t in wins)
    m.gross_loss = -sum(t.pnl for t in losses)   # positive magnitude
    m.net_profit = sum(t.pnl for t in trades)
    m.total_fees = sum(t.fees for t in trades)
    m.profit_factor = (m.gross_profit / m.gross_loss) if m.gross_loss > 0 else math.inf
    m.avg_win = fmean([t.pnl for t in wins]) if wins else 0.0
    m.avg_loss = fmean([t.pnl for t in losses]) if losses else 0.0
    m.expectancy = m.net_profit / m.trades
    m.expectancy_r = fmean([t.r_multiple for t in trades])
    m.max_drawdown = max_drawdown(equity_curve) if equity_curve else 0.0
    per_trade_returns = [t.pnl for t in trades]
    m.sharpe = _ratio(per_trade_returns, downside_only=False)
    m.sortino = _ratio(per_trade_returns, downside_only=True)
    if initial_equity > 0:
        m.return_pct = m.net_profit / initial_equity
    return m


def format_metrics(m: Metrics) -> str:
    pf = "inf" if math.isinf(m.profit_factor) else f"{m.profit_factor:.2f}"
    return (
        f"Trades:        {m.trades}\n"
        f"Win rate:      {m.win_rate:.1%} ({m.wins}W / {m.losses}L)\n"
        f"Profit factor: {pf}\n"
        f"Expectancy:    {m.expectancy:.2f} ({m.expectancy_r:+.3f} R/trade)\n"
        f"Net profit:    {m.net_profit:.2f} ({m.return_pct:+.1%})\n"
        f"Total fees:    {m.total_fees:.2f}\n"
        f"Avg win/loss:  {m.avg_win:.2f} / {m.avg_loss:.2f}\n"
        f"Max drawdown:  {m.max_drawdown:.1%}\n"
        f"Sharpe/Sortino:{m.sharpe:.3f} / {m.sortino:.3f}"
    )
