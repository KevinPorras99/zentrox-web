"""Alert system (sistema de alertas).

A tiny pluggable notifier. The default sink logs to the standard ``logging``
module; a webhook sink is provided for live deployments (opt-in, only used when
a URL is configured, and it fails soft so alerting never crashes the bot).
"""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import Protocol

log = logging.getLogger("zentrox.alerts")


class AlertSink(Protocol):
    def send(self, level: str, message: str) -> None: ...


class LogSink:
    def send(self, level: str, message: str) -> None:
        log.log(getattr(logging, level.upper(), logging.INFO), message)


class WebhookSink:
    """POSTs a JSON payload to a webhook (e.g. Slack/Discord/Telegram relay)."""

    def __init__(self, url: str, timeout: float = 5.0) -> None:
        self.url = url
        self.timeout = timeout

    def send(self, level: str, message: str) -> None:
        payload = json.dumps({"level": level, "text": message}).encode()
        req = urllib.request.Request(
            self.url, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            urllib.request.urlopen(req, timeout=self.timeout)  # noqa: S310
        except Exception as exc:  # pragma: no cover - network best-effort
            log.warning("alert webhook failed: %s", exc)


class Alerts:
    def __init__(self, sinks: list[AlertSink] | None = None) -> None:
        self.sinks = sinks or [LogSink()]

    def _emit(self, level: str, message: str) -> None:
        for sink in self.sinks:
            sink.send(level, message)

    def info(self, message: str) -> None:
        self._emit("info", message)

    def warning(self, message: str) -> None:
        self._emit("warning", message)

    def error(self, message: str) -> None:
        self._emit("error", message)
