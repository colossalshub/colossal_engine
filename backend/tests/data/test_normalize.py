from __future__ import annotations

import datetime

import pytest

from quant.data.normalize import normalize_timeframe, to_epoch_ms

EPOCH_MS_2025_01_01_UTC = 1735689600000


@pytest.mark.parametrize(
    "token",
    ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"],
)
def test_normalize_timeframe_ccxt_canonical_pass_through(token: str) -> None:
    assert normalize_timeframe(token, "ccxt") == token


@pytest.mark.parametrize(
    "token",
    ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1mo"],
)
def test_normalize_timeframe_yfinance_canonical_pass_through(token: str) -> None:
    assert normalize_timeframe(token, "yfinance") == token


def test_normalize_timeframe_ccxt_month_case_trap() -> None:
    assert normalize_timeframe("1M", "ccxt") == "1mo"


def test_normalize_timeframe_ccxt_one_minute() -> None:
    assert normalize_timeframe("1m", "ccxt") == "1m"


def test_normalize_timeframe_yfinance_week() -> None:
    assert normalize_timeframe("1wk", "yfinance") == "1w"


def test_normalize_timeframe_ccxt_non_canonical_casing_raises() -> None:
    with pytest.raises(ValueError):
        normalize_timeframe("1H", "ccxt")


def test_normalize_timeframe_unknown_source_raises() -> None:
    with pytest.raises(ValueError) as exc_info:
        normalize_timeframe("1m", "unknown_source")
    message = str(exc_info.value)
    assert "1m" in message
    assert "unknown_source" in message


def test_normalize_timeframe_unknown_token_raises() -> None:
    with pytest.raises(ValueError) as exc_info:
        normalize_timeframe("banana", "ccxt")
    message = str(exc_info.value)
    assert "banana" in message
    assert "ccxt" in message


def test_to_epoch_ms_int_zero() -> None:
    assert to_epoch_ms(0) == 0


def test_to_epoch_ms_int_passthrough() -> None:
    assert to_epoch_ms(EPOCH_MS_2025_01_01_UTC) == EPOCH_MS_2025_01_01_UTC


def test_to_epoch_ms_aware_utc_datetime() -> None:
    dt = datetime.datetime(2025, 1, 1, tzinfo=datetime.UTC)
    assert to_epoch_ms(dt) == EPOCH_MS_2025_01_01_UTC


def test_to_epoch_ms_aware_non_utc_datetime() -> None:
    tz_plus_8 = datetime.timezone(datetime.timedelta(hours=8))
    dt = datetime.datetime(2025, 1, 1, 8, 0, tzinfo=tz_plus_8)
    assert to_epoch_ms(dt) == EPOCH_MS_2025_01_01_UTC


def test_to_epoch_ms_iso_string_z_suffix() -> None:
    assert to_epoch_ms("2025-01-01T00:00:00Z") == EPOCH_MS_2025_01_01_UTC


def test_to_epoch_ms_iso_string_offset_suffix() -> None:
    assert to_epoch_ms("2025-01-01T00:00:00+00:00") == EPOCH_MS_2025_01_01_UTC


def test_to_epoch_ms_naive_datetime_raises() -> None:
    naive = datetime.datetime(2025, 1, 1)
    with pytest.raises(ValueError) as exc_info:
        to_epoch_ms(naive)
    assert "naive" in str(exc_info.value).lower()


def test_to_epoch_ms_float_raises_type_error() -> None:
    with pytest.raises(TypeError) as exc_info:
        to_epoch_ms(1.5)
    assert "float" in str(exc_info.value).lower()


def test_to_epoch_ms_none_raises_type_error() -> None:
    with pytest.raises(TypeError) as exc_info:
        to_epoch_ms(None)
    assert "NoneType" in str(exc_info.value)
