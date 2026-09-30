"""Fail-closed ingestion when the internal page cap truncates the requested range."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import duckdb
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_INGEST_SCRIPT = _REPO_ROOT / "scripts" / "ingest_bars.py"

_DAY_MS = 86_400_000
_START_MS = _DAY_MS


def _load_ingest_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "ingest_bars_under_test",
        _INGEST_SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _candle(ts: int) -> list[float | int]:
    return [ts, 100.0, 101.0, 99.0, 100.0, 1.0]


def _fetch_kwargs(
    *,
    venue: str = "binance",
    symbol: str = "BTC/USDT",
    db_path: Path,
    start_ms: int,
    end_ms: int,
    fetch_ohlcv: Any,
) -> dict[str, Any]:
    return {
        "fetch_ohlcv": fetch_ohlcv,
        "venue": venue,
        "symbol": symbol,
        "ccxt_timeframe": "1d",
        "canonical_timeframe": "1d",
        "asset_class": "crypto",
        "start_ms": start_ms,
        "end_ms": end_ms,
        "db_path": db_path,
    }


def test_complete_fetch_two_pages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = _load_ingest_module()
    monkeypatch.setattr(mod, "_PAGE_LIMIT", 10)
    start_ms = _START_MS
    end_ms = start_ms + 19 * _DAY_MS
    page_calls = 0

    def fetch_ohlcv(
        symbol: str,
        timeframe: str,
        since: int,
        limit: int,
    ) -> list[list[float | int]]:
        nonlocal page_calls
        page_calls += 1
        if page_calls == 1:
            return [_candle(start_ms + i * _DAY_MS) for i in range(10)]
        return [_candle(start_ms + i * _DAY_MS) for i in range(10, 20)]

    db_path = tmp_path / "bars.duckdb"
    total = mod.fetch_and_ingest(
        **_fetch_kwargs(
            db_path=db_path,
            start_ms=start_ms,
            end_ms=end_ms,
            fetch_ohlcv=fetch_ohlcv,
        ),
    )
    assert total == 20


def test_empty_first_page_returns_zero(tmp_path: Path) -> None:
    mod = _load_ingest_module()

    def fetch_ohlcv(
        symbol: str,
        timeframe: str,
        since: int,
        limit: int,
    ) -> list[list[float | int]]:
        return []

    db_path = tmp_path / "bars.duckdb"
    total = mod.fetch_and_ingest(
        **_fetch_kwargs(
            db_path=db_path,
            start_ms=_START_MS,
            end_ms=_START_MS + 10 * _DAY_MS,
            fetch_ohlcv=fetch_ohlcv,
        ),
    )
    assert total == 0


def test_page_cap_incomplete_raises_runtime_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = _load_ingest_module()
    monkeypatch.setattr(mod, "_MAX_PAGES", 3)
    start_ms = _START_MS
    end_ms = 10**13

    def fetch_ohlcv(
        symbol: str,
        timeframe: str,
        since: int,
        limit: int,
    ) -> list[list[float | int]]:
        return [_candle(since + i * _DAY_MS) for i in range(limit)]

    db_path = tmp_path / "bars.duckdb"
    with pytest.raises(RuntimeError) as exc_info:
        mod.fetch_and_ingest(
            **_fetch_kwargs(
                db_path=db_path,
                start_ms=start_ms,
                end_ms=end_ms,
                fetch_ohlcv=fetch_ohlcv,
            ),
        )
    page_limit = mod._PAGE_LIMIT
    since = start_ms
    last_ts_ms = start_ms
    for _ in range(3):
        last_ts_ms = since + (page_limit - 1) * _DAY_MS
        since = last_ts_ms + 1
    msg = str(exc_info.value)
    assert "ingestion incomplete" in msg
    assert "page cap" in msg
    assert mod._iso(last_ts_ms) in msg
    assert mod._iso(end_ms) in msg
    assert "Retry with a narrower range" in msg


def test_page_cap_hit_but_range_covered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = _load_ingest_module()
    monkeypatch.setattr(mod, "_MAX_PAGES", 3)
    start_ms = _START_MS
    end_ms = start_ms + 500 * _DAY_MS

    def fetch_ohlcv(
        symbol: str,
        timeframe: str,
        since: int,
        limit: int,
    ) -> list[list[float | int]]:
        bars: list[list[float | int]] = []
        ts = since
        while len(bars) < limit and ts <= end_ms:
            bars.append(_candle(ts))
            ts += _DAY_MS
        return bars

    db_path = tmp_path / "bars.duckdb"
    total = mod.fetch_and_ingest(
        **_fetch_kwargs(
            db_path=db_path,
            start_ms=start_ms,
            end_ms=end_ms,
            fetch_ohlcv=fetch_ohlcv,
        ),
    )
    assert total == 501


def test_bars_written_before_page_cap_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = _load_ingest_module()
    monkeypatch.setattr(mod, "_MAX_PAGES", 3)
    start_ms = _START_MS
    end_ms = 10**13

    def fetch_ohlcv(
        symbol: str,
        timeframe: str,
        since: int,
        limit: int,
    ) -> list[list[float | int]]:
        return [_candle(since + i * _DAY_MS) for i in range(limit)]

    db_path = tmp_path / "bars.duckdb"
    with pytest.raises(RuntimeError):
        mod.fetch_and_ingest(
            **_fetch_kwargs(
                db_path=db_path,
                start_ms=start_ms,
                end_ms=end_ms,
                fetch_ohlcv=fetch_ohlcv,
            ),
        )

    conn = duckdb.connect(str(db_path))
    try:
        count = conn.execute("SELECT COUNT(*) FROM curated_bars").fetchone()[0]
    finally:
        conn.close()
    assert count > 0
