"""Command-line interface for the Zentrox bot.

Examples
--------
    python -m zentrox_bot demo
    python -m zentrox_bot backtest --synthetic --bars 6000 --html report.html
    python -m zentrox_bot backtest --csv BTC/USDT=data/btc_15m.csv
    python -m zentrox_bot walkforward --folds 4
"""

from __future__ import annotations

import argparse
import logging
import sys

from .backtest import Backtester, walk_forward
from .config import BotConfig
from .dashboard import write_html
from .data import CSVFeed, SyntheticFeed
from .journal import Journal
from .metrics import format_metrics
from .strategy import TrendFollowingStrategy


def _build_config(args: argparse.Namespace, symbols: list[str]) -> BotConfig:
    if getattr(args, "config", None):
        cfg = BotConfig.load(args.config)
        cfg.symbols = symbols or cfg.symbols
        return cfg
    cfg = BotConfig(symbols=symbols)
    if getattr(args, "risk", None) is not None:
        cfg.risk.risk_per_trade = args.risk
    return cfg


def _make_feed(args: argparse.Namespace) -> tuple[object, list[str]]:
    if getattr(args, "csv", None):
        files = {}
        for pair in args.csv:
            sym, _, path = pair.partition("=")
            if not path:
                raise SystemExit(f"invalid --csv entry '{pair}', expected SYMBOL=path")
            files[sym] = path
        feed = CSVFeed(files, base_timeframe=args.operational)
        return feed, list(files)
    symbols = args.symbols or ["BTC/USDT"]
    feed = SyntheticFeed(
        symbols=symbols,
        base_timeframe=args.operational,
        bars=args.bars,
        seed=args.seed,
    )
    return feed, symbols


def _cmd_backtest(args: argparse.Namespace) -> int:
    feed, symbols = _make_feed(args)
    cfg = _build_config(args, symbols)
    cfg.strategy.operational = args.operational
    journal = Journal(args.journal) if args.journal else None
    bt = Backtester(feed, cfg, TrendFollowingStrategy(), journal=journal)
    result = bt.run()
    print(f"Symbols: {', '.join(symbols)}")
    print(format_metrics(result.metrics))
    print(f"Final equity: {result.final_equity:.2f}")
    if args.html:
        write_html(result, args.html)
        print(f"Dashboard written to {args.html}")
    if journal:
        print(f"Journal: {args.journal} ({journal.trade_count()} trades)")
        journal.close()
    return 0


def _cmd_walkforward(args: argparse.Namespace) -> int:
    feed, symbols = _make_feed(args)
    cfg = _build_config(args, symbols)
    cfg.strategy.operational = args.operational
    folds = walk_forward(feed, cfg, TrendFollowingStrategy, folds=args.folds)
    for f in folds:
        print(f"\n--- Fold {f.index + 1} [{f.start_ts} → {f.end_ts}] ---")
        print(format_metrics(f.metrics))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zentrox_bot",
                                description="Zentrox crypto trading bot")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--symbols", nargs="*", help="symbols, e.g. BTC/USDT ETH/USDT")
        sp.add_argument("--synthetic", action="store_true",
                        help="use the built-in synthetic feed (default when no --csv)")
        sp.add_argument("--csv", nargs="*", help="SYMBOL=path.csv entries")
        sp.add_argument("--operational", default="15m", help="operational timeframe")
        sp.add_argument("--bars", type=int, default=20000,
                        help="synthetic bar count (needs enough for the 1D filter)")
        sp.add_argument("--seed", type=int, default=42, help="synthetic RNG seed")
        sp.add_argument("--risk", type=float, help="risk fraction per trade (e.g. 0.01)")
        sp.add_argument("--config", help="path to a JSON config file")

    bt = sub.add_parser("backtest", help="run a backtest")
    add_common(bt)
    bt.add_argument("--journal", help="SQLite journal path")
    bt.add_argument("--html", help="write an HTML dashboard to this path")
    bt.set_defaults(func=_cmd_backtest)

    demo = sub.add_parser("demo", help="quick synthetic demo")
    add_common(demo)
    demo.add_argument("--journal", help="SQLite journal path")
    demo.add_argument("--html", help="write an HTML dashboard to this path")
    demo.set_defaults(func=_cmd_backtest)

    wf = sub.add_parser("walkforward", help="out-of-sample walk-forward")
    add_common(wf)
    wf.add_argument("--folds", type=int, default=4)
    wf.set_defaults(func=_cmd_walkforward)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
