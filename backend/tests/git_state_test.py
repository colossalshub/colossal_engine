"""Tests for ``quant.git_state.capture_git_state``."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from quant.git_state import capture_git_state

_SHA_HEX = re.compile(r"^[0-9a-f]{40}$")


def test_capture_git_state_current_repo() -> None:
    sha, dirty = capture_git_state(Path.cwd())
    assert sha is not None
    assert _SHA_HEX.match(sha)
    assert isinstance(dirty, bool)


def test_capture_git_state_non_repo(tmp_path: Path) -> None:
    assert capture_git_state(tmp_path) == (None, False)


def test_capture_git_state_missing_git_binary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_file_not_found(*_args: object, **_kwargs: object) -> None:
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", _raise_file_not_found)
    assert capture_git_state(Path.cwd()) == (None, False)
