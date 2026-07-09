"""Zentrox crypto trading bot.

A modular, capital-preservation-first trading bot built to the project
specification. Core packages:

    config      configuration objects and (de)serialization
    models      domain models (Candle, Signal, Position, Trade, ...)
    indicators  pure-Python technical indicators + timeframe resampling
    data        data ingestion feeds (synthetic, CSV, optional live)
    strategy    multi-timeframe trend/regime detection and the strategy engine
    risk        position sizing and capital-preservation limits
    portfolio   book-level exposure / correlation constraints
    orders      order manager / paper broker (SL, TP, trailing, partials)
    metrics     performance KPIs
    journal     SQLite trade & decision registry
    monitor     health, status and safety-rule enforcement
    alerts      pluggable alert sinks
    backtest    the event-driven engine (+ walk-forward helpers)
"""

from .config import BotConfig, RiskConfig, StrategyConfig, ExecutionConfig
from .backtest import Backtester, BacktestResult, walk_forward
from .strategy import TrendFollowingStrategy

__version__ = "0.1.0"

__all__ = [
    "BotConfig",
    "RiskConfig",
    "StrategyConfig",
    "ExecutionConfig",
    "Backtester",
    "BacktestResult",
    "walk_forward",
    "TrendFollowingStrategy",
    "__version__",
]
