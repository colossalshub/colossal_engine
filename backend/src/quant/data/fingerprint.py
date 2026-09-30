"""Deterministic fingerprint of the exact ordered bar rows a run consumed."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import cast

__all__ = ["fingerprint_bars"]


def fingerprint_bars(rows: Sequence[Mapping[str, object]]) -> str:
    """Return a lowercase hex SHA-256 of the canonical serialization.

    The input must be the exact list of bar dicts passed into the engine,
    in the order the engine consumed them. Rows are formatted as:
        venue|symbol|timeframe|ts|open|high|low|close|volume
    with floats printed via ':.10g'. Lines are LF-separated with no
    trailing newline.
    """
    lines: list[str] = []
    for r in rows:
        lines.append(
            "{v}|{s}|{t}|{ts}|{o:.10g}|{h:.10g}|{low:.10g}|{c:.10g}|{vol:.10g}".format(
                v=r["venue"],
                s=r["symbol"],
                t=r["timeframe"],
                ts=int(cast(int, r["ts"])),
                o=float(cast(float, r["open"])),
                h=float(cast(float, r["high"])),
                low=float(cast(float, r["low"])),
                c=float(cast(float, r["close"])),
                vol=float(cast(float, r["volume"])),
            )
        )
    payload = "\n".join(lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
