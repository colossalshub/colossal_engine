"""Tests for quant.logging_setup.configure_logging."""

from __future__ import annotations

import importlib
import io
import json
import logging
from unittest.mock import patch

import pytest

import quant.logging_setup as ls


def test_configure_logging_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("QUANT_LOG_JSON", raising=False)
    importlib.reload(ls)
    ls.configure_logging()
    ls.configure_logging()
    assert len(logging.getLogger().handlers) == 1


def test_configure_logging_json_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QUANT_LOG_JSON", "1")

    importlib.reload(ls)

    stderr = io.StringIO()
    with patch("sys.stderr", stderr):
        ls.configure_logging()
        logging.getLogger("test").info("hello")

    output = stderr.getvalue().strip()
    payload = json.loads(output)
    assert payload["level"] == "INFO"
    assert payload["message"] == "hello"
    assert payload["logger"] == "test"
    assert "ts" in payload
