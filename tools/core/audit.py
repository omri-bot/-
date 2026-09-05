"""Append-only log of every platform call, written to data/runs/."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from . import paths

RUNS = paths.DATA / "runs"


def record(
    platform: str,
    action: str,
    client: str,
    *,
    request: dict[str, Any] | None = None,
    response: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    RUNS.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    entry = {
        "ts": now.isoformat(),
        "platform": platform,
        "action": action,
        "client": client,
        "request": _redact(request or {}),
        "response": response,
        "error": error,
    }
    logfile = RUNS / f"{now:%Y-%m-%d}.jsonl"
    with logfile.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


_SECRET_HINTS = ("token", "secret", "password", "key")


def _redact(data: dict[str, Any]) -> dict[str, Any]:
    return {
        k: ("***" if any(h in k.lower() for h in _SECRET_HINTS) else v)
        for k, v in data.items()
    }
