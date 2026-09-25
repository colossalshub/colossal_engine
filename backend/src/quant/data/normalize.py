"""Canonical timeframe tokens and epoch-ms conversion."""

from __future__ import annotations

import datetime

_CCXT_TOKEN_MAP: dict[str, str] = {
    "1M": "1mo",
    "1m": "1m",
    "1w": "1w",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}

_YFINANCE_TOKEN_MAP: dict[str, str] = {
    "1wk": "1w",
    "1mo": "1mo",
    "1d": "1d",
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
}

_SOURCE_MAPS: dict[str, dict[str, str]] = {
    "ccxt": _CCXT_TOKEN_MAP,
    "yfinance": _YFINANCE_TOKEN_MAP,
}


def normalize_timeframe(token: str, source: str) -> str:
    """Map a source-specific timeframe token to a canonical token."""
    mapping = _SOURCE_MAPS.get(source)
    if mapping is None:
        msg = (
            f"Unknown timeframe source {source!r} for token {token!r}"
        )
        raise ValueError(msg)
    try:
        return mapping[token]
    except KeyError as exc:
        msg = f"Unknown timeframe token {token!r} for source {source!r}"
        raise ValueError(msg) from exc


def to_epoch_ms(value: object) -> int:
    """Convert a value to UTC epoch milliseconds (int64)."""
    if isinstance(value, int):
        return value
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            msg = "Naive datetimes are not allowed; use timezone-aware UTC datetimes"
            raise ValueError(msg)
        utc_dt = value.astimezone(datetime.timezone.utc)
        return int(utc_dt.timestamp() * 1000)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            msg = "Naive datetimes are not allowed; use timezone-aware UTC datetimes"
            raise ValueError(msg)
        utc_dt = parsed.astimezone(datetime.timezone.utc)
        return int(utc_dt.timestamp() * 1000)
    type_name = type(value).__name__
    msg = f"Unsupported type for epoch-ms conversion: {type_name}"
    raise TypeError(msg)
