"""Shared lookup from strategy name to Nautilus strategy class."""

from __future__ import annotations

from quant.strategies.buy_hold import BuyHold
from quant.strategies.ema_cross import EmaCross

STRATEGY_CLASSES: dict[str, type] = {
    "buy_hold": BuyHold,
    "ema_cross": EmaCross,
}


def is_deterministic(strategy_name: str) -> bool:
    cls = STRATEGY_CLASSES.get(strategy_name)
    return bool(getattr(cls, "deterministic", False))


__all__ = ["STRATEGY_CLASSES", "is_deterministic"]
