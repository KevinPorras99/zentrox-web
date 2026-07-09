"""Dashboard (dashboard).

Renders a self-contained HTML report of a backtest: the KPI table plus an
inline-SVG equity curve. No external assets or JS libraries, so it opens
anywhere and needs no network.
"""

from __future__ import annotations

import html
import math
from typing import Sequence

from .backtest import BacktestResult

_GOLD = "#ffd805"
_ORANGE = "#f49f20"
_BG = "#000000"
_GRAY = "#afafaf"


def _equity_svg(curve: Sequence[tuple[int, float]], w: int = 900, h: int = 320) -> str:
    if len(curve) < 2:
        return "<p>Not enough data for a chart.</p>"
    values = [e for _, e in curve]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    pad = 40
    n = len(values)

    def x(i: int) -> float:
        return pad + (w - 2 * pad) * i / (n - 1)

    def y(v: float) -> float:
        return h - pad - (h - 2 * pad) * (v - lo) / span

    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values))
    baseline = y(values[0])
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Equity curve">
  <rect x="0" y="0" width="{w}" height="{h}" fill="{_BG}"/>
  <line x1="{pad}" y1="{baseline:.1f}" x2="{w-pad}" y2="{baseline:.1f}"
        stroke="{_GRAY}" stroke-dasharray="4 4" stroke-width="1"/>
  <polyline points="{pts}" fill="none" stroke="{_GOLD}" stroke-width="2"/>
  <text x="{pad}" y="24" fill="{_GRAY}" font-family="monospace" font-size="13">
    equity {values[0]:.0f} → {values[-1]:.0f}</text>
</svg>"""


def render_html(result: BacktestResult, title: str = "Zentrox Bot — Backtest") -> str:
    m = result.metrics
    pf = "∞" if math.isinf(m.profit_factor) else f"{m.profit_factor:.2f}"
    rows = [
        ("Trades", f"{m.trades}"),
        ("Win rate", f"{m.win_rate:.1%} ({m.wins}W / {m.losses}L)"),
        ("Profit factor", pf),
        ("Expectancy", f"{m.expectancy:.2f} ({m.expectancy_r:+.3f} R)"),
        ("Net profit", f"{m.net_profit:.2f} ({m.return_pct:+.1%})"),
        ("Total fees", f"{m.total_fees:.2f}"),
        ("Max drawdown", f"{m.max_drawdown:.1%}"),
        ("Sharpe / Sortino", f"{m.sharpe:.3f} / {m.sortino:.3f}"),
        ("Final equity", f"{result.final_equity:.2f}"),
    ]
    trs = "\n".join(
        f'<tr><td>{html.escape(k)}</td><td class="v">{html.escape(v)}</td></tr>'
        for k, v in rows
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
  :root {{ --gold:{_GOLD}; --orange:{_ORANGE}; --gray:{_GRAY}; }}
  body {{ background:{_BG}; color:#fff; font-family:'Space Grotesk',system-ui,sans-serif;
         margin:0; padding:2rem; }}
  h1 {{ color:var(--gold); font-family:'Press Start 2P',monospace; font-size:1rem;
        letter-spacing:1px; }}
  table {{ border-collapse:collapse; width:100%; max-width:560px; margin-top:1rem; }}
  td {{ padding:.55rem .8rem; border-bottom:1px solid #222; }}
  td.v {{ text-align:right; color:var(--gold); font-family:monospace; }}
  .card {{ background:#0a0a0a; border:1px solid #1c1c1c; border-radius:10px;
           padding:1.2rem; margin-top:1.5rem; }}
</style></head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="card">{_equity_svg(result.equity_curve)}</div>
  <div class="card"><table>{trs}</table></div>
</body></html>"""


def write_html(result: BacktestResult, path: str,
               title: str = "Zentrox Bot — Backtest") -> None:
    from pathlib import Path
    Path(path).write_text(render_html(result, title))
