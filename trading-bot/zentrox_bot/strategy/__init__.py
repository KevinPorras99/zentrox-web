"""Strategy engine (motor de estrategia)."""

from .base import Strategy, StrategyContext
from .trend import detect_trend
from .levels import Levels, find_levels
from .trend_following import TrendFollowingStrategy

__all__ = [
    "Strategy",
    "StrategyContext",
    "detect_trend",
    "Levels",
    "find_levels",
    "TrendFollowingStrategy",
]
