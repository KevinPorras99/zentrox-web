"""Multi-timeframe trend-following breakout strategy.

Implements the specification's decision flow:

1. Analyse trend on the higher (1D) and intermediate (4H) timeframes.
2. Identify supports / resistances on the operational timeframe.
3. Wait for confirmation on the operational timeframe (breakout of a level in
   the direction of the aligned trend).
4. Apply entry filters (trend alignment, volume, spread handled at execution).
5. Compute a structural + ATR based stop and an RR-based take-profit.

The strategy never predicts; it only reacts to these rules, and abstains when
the regime is a range or the higher timeframes disagree.
"""

from __future__ import annotations

from typing import Optional

from ..indicators import atr, sma
from ..models import Side, Signal, Trend
from .base import Strategy, StrategyContext
from .levels import find_levels
from .trend import detect_trend


class TrendFollowingStrategy(Strategy):
    name = "trend_following"

    def evaluate(self, ctx: StrategyContext) -> Optional[Signal]:
        cfg = ctx.config
        if len(ctx.op) < max(cfg.ema_slow, cfg.level_lookback, cfg.atr_period) + 5:
            return None

        htf = detect_trend(ctx.htf, cfg.ema_fast, cfg.ema_slow, cfg.trend_slope_min)
        mtf = detect_trend(ctx.mtf, cfg.ema_fast, cfg.ema_slow, cfg.trend_slope_min)

        # Filtro: tendencia alineada. Range or disagreement => abstain.
        if htf != mtf or htf == Trend.RANGE:
            return None
        bias = Side.LONG if htf == Trend.UP else Side.SHORT

        # Volume filter.
        vols = [c.volume for c in ctx.op]
        vol_ma = sma(vols, 20)[-1]
        if vol_ma and vols[-1] < cfg.min_volume_ratio * vol_ma:
            return None

        atr_series = atr(list(ctx.op), cfg.atr_period)
        a = atr_series[-1]
        if not a or a <= 0:
            return None

        levels = find_levels(ctx.op, cfg.swing_lookback, cfg.level_lookback)
        last = ctx.op[-1]
        prev = ctx.op[-2]
        entry = last.close

        if bias is Side.LONG:
            res = levels.nearest_resistance(prev.close)
            if res is None:
                return None
            # Confirmation: breakout of resistance by the configured buffer.
            if last.close <= res * (1 + cfg.breakout_buffer):
                return None
            support = levels.nearest_support(entry)
            atr_stop = entry - cfg.atr_stop_mult * a
            stop = min(support, atr_stop) if support is not None else atr_stop
            if stop >= entry:
                return None
        else:
            sup = levels.nearest_support(prev.close)
            if sup is None:
                return None
            if last.close >= sup * (1 - cfg.breakout_buffer):
                return None
            resistance = levels.nearest_resistance(entry)
            atr_stop = entry + cfg.atr_stop_mult * a
            stop = max(resistance, atr_stop) if resistance is not None else atr_stop
            if stop <= entry:
                return None

        risk = abs(entry - stop)
        if risk <= 0:
            return None
        # Take-profit at the ideal RR; the risk manager still enforces min RR.
        tp = entry + bias.sign * risk * cfg.target_rr

        partials: list[tuple[float, float]] = []
        if cfg.partial_fraction > 0:
            partial_price = entry + bias.sign * risk * cfg.partial_rr
            partials.append((partial_price, cfg.partial_fraction))

        return Signal(
            symbol=ctx.symbol,
            side=bias,
            entry=entry,
            stop=stop,
            take_profit=tp,
            reason=f"{bias.value} breakout | HTF={htf.value} MTF={mtf.value}",
            ts=last.ts,
            partials=partials,
        )
