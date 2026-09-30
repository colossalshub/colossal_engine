"""Capture git SHA and dirty flag at run creation time."""

from __future__ import annotations

import subprocess
from pathlib import Path

__all__ = ["capture_git_state"]


def capture_git_state(repo_root: Path) -> tuple[str | None, bool]:
    """Return (sha, dirty) from the given repo root.

    Returns (None, False) if git is unavailable, the repo has no commits,
    or any subprocess call fails. Never raises.
    """
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout.strip()
        porcelain = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout
        return sha or None, bool(porcelain.strip())
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return None, False
