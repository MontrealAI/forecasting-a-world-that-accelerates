from __future__ import annotations

import os
from datetime import datetime, timezone


def reproducible_utc_now() -> datetime:
    """Return UTC now, honoring SOURCE_DATE_EPOCH for reproducible builds."""

    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw is None:
        return datetime.now(timezone.utc).replace(microsecond=0)
    try:
        epoch = int(raw)
    except ValueError as exc:
        raise ValueError("SOURCE_DATE_EPOCH must be an integer Unix timestamp") from exc
    if epoch < 0:
        raise ValueError("SOURCE_DATE_EPOCH must be nonnegative")
    return datetime.fromtimestamp(epoch, timezone.utc).replace(microsecond=0)


def reproducible_utc_iso() -> str:
    return reproducible_utc_now().isoformat()
