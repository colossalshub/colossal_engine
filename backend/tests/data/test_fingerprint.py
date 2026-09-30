from __future__ import annotations

import re

from quant.data.fingerprint import fingerprint_bars

_EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _bar(ts: int, close: float = 100.0) -> dict[str, object]:
    return {
        "venue": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "ts": ts,
        "open": 100.0,
        "high": 110.0,
        "low": 90.0,
        "close": close,
        "volume": 1.0,
    }


def test_deterministic() -> None:
    rows = [_bar(1), _bar(2)]
    assert fingerprint_bars(rows) == fingerprint_bars(rows)


def test_order_matters() -> None:
    a, b = _bar(1), _bar(2)
    assert fingerprint_bars([a, b]) != fingerprint_bars([b, a])


def test_bar_value_change_matters() -> None:
    base = [_bar(1), _bar(2, close=100.0)]
    changed = [_bar(1), _bar(2, close=100.0 + 1e-6)]
    assert fingerprint_bars(base) != fingerprint_bars(changed)


def test_precision_boundary_distinguishes_tenth_significant_digit() -> None:
    # 1.234567890 / 1.234567891 differ in the 10th significant digit.
    a = fingerprint_bars([_bar(1, close=1.234567890)])
    b = fingerprint_bars([_bar(1, close=1.234567891)])
    assert a != b


def test_precision_floor_ignores_digits_below_threshold() -> None:
    a = fingerprint_bars([_bar(1, close=1.2345678901)])
    b = fingerprint_bars([_bar(1, close=1.23456789012)])
    assert a == b


def test_empty_input_is_sha256_of_empty_bytes() -> None:
    assert fingerprint_bars([]) == _EMPTY_SHA256


def test_digest_is_64_lowercase_hex() -> None:
    digest = fingerprint_bars([_bar(1)])
    assert len(digest) == 64
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
