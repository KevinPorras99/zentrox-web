"""Trade journal / registry (registro) backed by SQLite.

Persists every executed trade and every notable decision (including *why* a
signal was rejected) so the bot's behaviour is fully auditable, as required by
the specification ("Registrar todas las decisiones").
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import ExitReason, Side, Trade


def _iso(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


class Journal:
    def __init__(self, path: str = "zentrox_journal.sqlite") -> None:
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                qty REAL NOT NULL,
                entry REAL NOT NULL,
                exit REAL NOT NULL,
                opened_at TEXT NOT NULL,
                closed_at TEXT NOT NULL,
                pnl REAL NOT NULL,
                fees REAL NOT NULL,
                r_multiple REAL NOT NULL,
                reason TEXT,
                exit_reason TEXT
            );
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                at TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                detail TEXT
            );
            """
        )
        self.conn.commit()

    def record_trade(self, trade: Trade) -> None:
        self.conn.execute(
            """INSERT INTO trades
               (symbol, side, qty, entry, exit, opened_at, closed_at,
                pnl, fees, r_multiple, reason, exit_reason)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                trade.symbol, trade.side.value, trade.qty, trade.entry, trade.exit,
                _iso(trade.opened_ts), _iso(trade.closed_ts), trade.pnl, trade.fees,
                trade.r_multiple, trade.reason, trade.exit_reason.value,
            ),
        )
        self.conn.commit()

    def record_decision(self, ts: int, symbol: str, action: str,
                        detail: str = "") -> None:
        self.conn.execute(
            "INSERT INTO decisions (at, symbol, action, detail) VALUES (?,?,?,?)",
            (_iso(ts), symbol, action, detail),
        )
        self.conn.commit()

    def trade_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Journal":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
