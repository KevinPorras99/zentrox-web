"""Configuration objects for the bot.

Config can be built in code, loaded from a JSON file, or from a plain ``dict``.
Everything has sensible, conservative defaults that follow the specification
(capital preservation first).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class RiskConfig:
    # Riesgo por operación: 0.5%--1% del capital.
    risk_per_trade: float = 0.01          # 1% of equity per trade
    min_rr: float = 2.0                    # minimum reward/risk (1:2)
    ideal_rr: float = 3.0                  # informational target (1:3)
    max_consecutive_losses: int = 3       # pause after N losses in a row
    daily_loss_limit: float = 0.03        # stop the day after -3% equity
    max_drawdown_pause: float = 0.20      # pause the bot beyond -20% drawdown
    # Portfolio level constraints.
    max_total_exposure: float = 0.30      # sum of position risk vs equity
    max_open_positions: int = 5
    max_positions_per_symbol: int = 1
    max_correlation: float = 0.8          # block highly correlated new entries

    def __post_init__(self) -> None:
        if not (0 < self.risk_per_trade <= 0.05):
            raise ValueError("risk_per_trade must be within (0, 0.05]")
        if self.min_rr <= 0:
            raise ValueError("min_rr must be positive")


@dataclass
class StrategyConfig:
    # Multi-timeframe analysis.
    htf_trend: str = "1d"                 # tendencia principal
    mtf_trend: str = "4h"                 # tendencia intermedia
    operational: str = "15m"              # temporalidad operativa (15m--1H)
    ema_fast: int = 21
    ema_slow: int = 55
    swing_lookback: int = 5               # bars each side for swing points
    level_lookback: int = 120             # bars scanned for S/R levels
    breakout_buffer: float = 0.0005       # 0.05% beyond level to confirm
    atr_period: int = 14
    atr_stop_mult: float = 1.5            # stop distance = mult * ATR
    target_rr: float = 3.0               # take-profit reward/risk (ideal 1:3)
    min_volume_ratio: float = 1.0         # volume vs its moving average
    trend_slope_min: float = 0.0          # min normalized EMA slope for trend
    use_trailing_stop: bool = False
    trailing_atr_mult: float = 2.0
    max_holding_bars: int = 0             # 0 = disabled (tiempo máximo)
    # Salidas parciales: fraction to scale out at ``partial_rr``.
    # 0 disables partials; e.g. 0.5 takes half off at 1:2.
    partial_fraction: float = 0.0
    partial_rr: float = 2.0


@dataclass
class ExecutionConfig:
    commission: float = 0.0004            # 0.04% taker fee per side
    slippage: float = 0.0005              # 0.05% adverse slippage on fills
    max_spread: float = 0.001             # skip if spread wider than 0.1%


@dataclass
class BotConfig:
    symbols: list[str] = field(default_factory=lambda: ["BTC/USDT"])
    initial_equity: float = 10_000.0
    risk: RiskConfig = field(default_factory=RiskConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    journal_path: str = "zentrox_journal.sqlite"
    live: bool = False                    # False => paper/backtest only

    # ---- (de)serialization helpers -------------------------------------
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotConfig":
        data = dict(data)
        risk = RiskConfig(**data.pop("risk", {}))
        strategy = StrategyConfig(**data.pop("strategy", {}))
        execution = ExecutionConfig(**data.pop("execution", {}))
        return cls(risk=risk, strategy=strategy, execution=execution, **data)

    @classmethod
    def load(cls, path: str | Path) -> "BotConfig":
        return cls.from_dict(json.loads(Path(path).read_text()))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))
