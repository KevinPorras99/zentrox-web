"""Backtesting engine — the orchestrator that wires every component together.

It runs a single, event-driven loop over a unified multi-symbol clock and, at
each step, applies the exact same sequence a live bot would:

    manage open positions  ->  mark equity  ->  run safety/monitor checks
    ->  ask the strategy  ->  risk-size  ->  portfolio-check  ->  place order

Because the *same* Strategy / RiskManager / PortfolioManager / OrderManager are
used here and (would be) in live trading, a passing backtest exercises the real
decision path — only the data source and broker differ.

Realism baked in: commissions, adverse slippage, pessimistic intrabar fills
(stop before target), and strict no-lookahead alignment of the higher
timeframes (only *closed* HTF/MTF candles are visible at each step).
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from typing import Optional, Sequence

from .alerts import Alerts
from .config import BotConfig
from .data.base import DataFeed
from .indicators import atr as atr_series_fn, timeframe_seconds
from .journal import Journal
from .metrics import Metrics, compute_metrics
from .models import Candle, Position, Trade
from .monitor import Monitor
from .orders import OrderManager
from .portfolio import PortfolioManager
from .risk import RiskManager
from .strategy.base import Strategy, StrategyContext


@dataclass
class BacktestResult:
    metrics: Metrics
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[tuple[int, float]] = field(default_factory=list)
    initial_equity: float = 0.0
    final_equity: float = 0.0


@dataclass
class _SymbolData:
    op: list[Candle]
    mtf: list[Candle]
    htf: list[Candle]
    atr: list[Optional[float]]
    mtf_close: list[int]
    htf_close: list[int]
    index: int = 0
    last_price: float = 0.0
    returns: list[float] = field(default_factory=list)


class Backtester:
    def __init__(
        self,
        feed: DataFeed,
        config: BotConfig,
        strategy: Strategy,
        journal: Optional[Journal] = None,
        alerts: Optional[Alerts] = None,
    ) -> None:
        self.feed = feed
        self.config = config
        self.strategy = strategy
        self.journal = journal
        self.alerts = alerts or Alerts()
        self.risk = RiskManager(config.risk, config.initial_equity)
        self.portfolio = PortfolioManager(config.risk)
        self.orders = OrderManager(config.execution, config.strategy)
        self.monitor = Monitor(self.risk, self.alerts)

    # ------------------------------------------------------------------
    def _load(self) -> dict[str, _SymbolData]:
        s = self.config.strategy
        data: dict[str, _SymbolData] = {}
        for sym in self.config.symbols:
            op = self.feed.get_candles(sym, s.operational)
            mtf = self.feed.get_candles(sym, s.mtf_trend)
            htf = self.feed.get_candles(sym, s.htf_trend)
            mtf_step = timeframe_seconds(s.mtf_trend)
            htf_step = timeframe_seconds(s.htf_trend)
            data[sym] = _SymbolData(
                op=op,
                mtf=mtf,
                htf=htf,
                atr=atr_series_fn(op, s.atr_period),
                mtf_close=[c.ts + mtf_step for c in mtf],
                htf_close=[c.ts + htf_step for c in htf],
            )
        return data

    @staticmethod
    def _closed_slice(candles: list[Candle], close_times: list[int],
                     now_close: int) -> list[Candle]:
        # Number of higher-timeframe candles whose close time <= now.
        n = bisect.bisect_right(close_times, now_close)
        return candles[:n]

    # ------------------------------------------------------------------
    def run(self, start_ts: Optional[int] = None,
            end_ts: Optional[int] = None) -> BacktestResult:
        data = self._load()
        op_step = timeframe_seconds(self.config.strategy.operational)

        # Unified, ordered clock across all symbols.
        clock = sorted({c.ts for sd in data.values() for c in sd.op
                        if (start_ts is None or c.ts >= start_ts)
                        and (end_ts is None or c.ts <= end_ts)})

        trades: list[Trade] = []
        equity_curve: list[tuple[int, float]] = []
        # Fast lookup: symbol -> {ts -> index}
        ts_index = {sym: {c.ts: i for i, c in enumerate(sd.op)}
                    for sym, sd in data.items()}
        open_by_symbol: dict[str, Position] = {}

        for t in clock:
            for sym, sd in data.items():
                i = ts_index[sym].get(t)
                if i is None:
                    continue
                sd.index = i
                candle = sd.op[i]
                sd.last_price = candle.close
                if i > 0:
                    prev = sd.op[i - 1].close
                    if prev > 0:
                        sd.returns.append((candle.close - prev) / prev)
                        if len(sd.returns) > 200:
                            sd.returns.pop(0)

                # 1) Manage an existing position on this symbol.
                pos = open_by_symbol.get(sym)
                if pos is not None:
                    closed = self.orders.update(pos, candle, sd.atr[i])
                    for tr in closed:
                        trades.append(tr)
                        self.risk.balance_pnl(tr.pnl)
                        self.risk.on_trade_closed(tr)
                        self.monitor.on_trade(tr)
                        if self.journal:
                            self.journal.record_trade(tr)
                    if pos.qty <= 1e-12:
                        self.portfolio.remove(pos)
                        open_by_symbol.pop(sym, None)

            # 2) Mark-to-market equity across the book at this instant.
            equity = self.risk.balance + sum(
                p.unrealized(data[p.symbol].last_price)
                for p in self.portfolio.positions
            )
            self.risk.on_equity(equity)
            equity_curve.append((t, equity))
            self.monitor.check(t)

            # 3) Look for new entries.
            for sym, sd in data.items():
                if sym in open_by_symbol:
                    continue
                i = ts_index[sym].get(t)
                if i is None:
                    continue
                candle = sd.op[i]
                now_close = candle.ts + op_step
                ctx = StrategyContext(
                    symbol=sym,
                    config=self.config.strategy,
                    op=sd.op[:i + 1],
                    mtf=self._closed_slice(sd.mtf, sd.mtf_close, now_close),
                    htf=self._closed_slice(sd.htf, sd.htf_close, now_close),
                )
                signal = self.strategy.evaluate(ctx)
                if signal is None:
                    continue
                decision = self.risk.evaluate(signal, candle.ts)
                if not decision.approved:
                    if self.journal:
                        self.journal.record_decision(
                            candle.ts, sym, "reject", decision.reason)
                    continue
                new_risk = decision.qty * signal.risk_per_unit
                returns = {s: d.returns for s, d in data.items()}
                ok, why = self.portfolio.can_open(sym, new_risk, equity, returns)
                if not ok:
                    if self.journal:
                        self.journal.record_decision(candle.ts, sym, "reject", why)
                    continue
                pos = self.orders.open(signal, decision.qty, candle.close, candle.ts)
                self.monitor.assert_protected(pos)
                self.portfolio.add(pos)
                open_by_symbol[sym] = pos
                if self.journal:
                    self.journal.record_decision(
                        candle.ts, sym, "open",
                        f"{signal.side.value} qty={decision.qty:.6f} "
                        f"RR={signal.rr:.2f} {signal.reason}")

        # Close anything still open at the end of the data.
        last_ts = clock[-1] if clock else 0
        for sym, pos in list(open_by_symbol.items()):
            tr = self.orders.force_close(pos, data[sym].last_price, last_ts)
            trades.append(tr)
            self.risk.balance_pnl(tr.pnl)
            self.risk.on_trade_closed(tr)
            if self.journal:
                self.journal.record_trade(tr)
            self.portfolio.remove(pos)
        if open_by_symbol:
            equity_curve.append((last_ts, self.risk.balance))

        metrics = compute_metrics(trades, [e for _, e in equity_curve],
                                  self.config.initial_equity)
        return BacktestResult(
            metrics=metrics,
            trades=trades,
            equity_curve=equity_curve,
            initial_equity=self.config.initial_equity,
            final_equity=self.risk.balance,
        )


# ----------------------------------------------------------------------
# Out-of-sample / walk-forward helpers
# ----------------------------------------------------------------------

@dataclass
class WalkForwardFold:
    index: int
    start_ts: int
    end_ts: int
    metrics: Metrics


def walk_forward(
    feed: DataFeed,
    config: BotConfig,
    strategy_factory,
    folds: int = 4,
) -> list[WalkForwardFold]:
    """Split the timeline into ``folds`` sequential out-of-sample segments and
    backtest each independently.

    ``strategy_factory`` is a zero-arg callable returning a fresh strategy for
    each fold (so no state leaks between folds). This provides the scaffolding
    for validating parameter stability across time (validación fuera de muestra
    / walk-forward).
    """
    # Determine the overall operational time span.
    all_ts = sorted({c.ts for sym in config.symbols
                     for c in feed.get_candles(sym, config.strategy.operational)})
    if not all_ts or folds < 1:
        return []
    span = all_ts[-1] - all_ts[0]
    seg = span // folds
    results: list[WalkForwardFold] = []
    for f in range(folds):
        start = all_ts[0] + f * seg
        end = all_ts[0] + (f + 1) * seg if f < folds - 1 else all_ts[-1]
        bt = Backtester(feed, config, strategy_factory())
        res = bt.run(start_ts=start, end_ts=end)
        results.append(WalkForwardFold(f, start, end, res.metrics))
    return results
