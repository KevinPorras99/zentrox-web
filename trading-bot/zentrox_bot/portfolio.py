"""Portfolio manager (gestor del portafolio).

Enforces book-level constraints that a single-trade risk check cannot see:

* maximum number of concurrent positions,
* maximum positions per symbol,
* maximum aggregate risk exposure vs equity,
* blocking new entries that are highly correlated with open ones.
"""

from __future__ import annotations

from statistics import fmean
from typing import Optional, Sequence

from .config import RiskConfig
from .models import Position


def correlation(a: Sequence[float], b: Sequence[float]) -> Optional[float]:
    """Pearson correlation of two equal-length return series."""
    n = min(len(a), len(b))
    if n < 3:
        return None
    a, b = a[-n:], b[-n:]
    ma, mb = fmean(a), fmean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return cov / (va ** 0.5 * vb ** 0.5)


class PortfolioManager:
    def __init__(self, config: RiskConfig) -> None:
        self.config = config
        self.positions: list[Position] = []

    def open_symbols(self) -> list[str]:
        return [p.symbol for p in self.positions]

    def total_risk(self) -> float:
        return sum(p.qty * p.risk_per_unit for p in self.positions)

    def can_open(
        self,
        symbol: str,
        new_risk: float,
        equity: float,
        returns: Optional[dict[str, Sequence[float]]] = None,
    ) -> tuple[bool, str]:
        if len(self.positions) >= self.config.max_open_positions:
            return False, "max open positions reached"
        held = sum(1 for p in self.positions if p.symbol == symbol)
        if held >= self.config.max_positions_per_symbol:
            return False, f"max positions per {symbol} reached"
        exposure = (self.total_risk() + new_risk) / equity if equity > 0 else 1.0
        if exposure > self.config.max_total_exposure:
            return False, f"exposure {exposure:.1%} exceeds cap"
        if returns and symbol in returns:
            for other in self.open_symbols():
                if other == symbol or other not in returns:
                    continue
                corr = correlation(returns[symbol], returns[other])
                if corr is not None and abs(corr) > self.config.max_correlation:
                    return False, f"correlation {corr:.2f} with {other} too high"
        return True, "ok"

    def add(self, position: Position) -> None:
        self.positions.append(position)

    def remove(self, position: Position) -> None:
        if position in self.positions:
            self.positions.remove(position)
