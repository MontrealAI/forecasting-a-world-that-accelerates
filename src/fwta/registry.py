from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .timeutil import reproducible_utc_iso

_ALLOWED_STATUSES = {"prospective-unscored", "demonstration-unscored", "matured-scored", "superseded"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def build_registry_record(
    forecast: dict[str, Any],
    previous_record_hash: str | None = None,
    *,
    registered_at: str | None = None,
    status: str = "prospective-unscored",
) -> dict[str, Any]:
    if status not in _ALLOWED_STATUSES:
        raise ValueError(f"unknown registry status {status!r}")
    content_hash = sha256_json(forecast)
    record = {
        "registry_version": "2.0.0",
        "forecast_id": forecast["forecast_id"],
        "research_cutoff": forecast["research_cutoff"],
        "target": forecast["target"],
        "input_sha256": forecast.get("reproducibility", {}).get("input_sha256"),
        "forecast_sha256": content_hash,
        "previous_record_sha256": previous_record_hash,
        "registered_at": registered_at or reproducible_utc_iso(),
        "status": status,
        "score": None,
    }
    record["record_sha256"] = sha256_json(record)
    return record


def append_registry(
    forecast: dict[str, Any],
    registry_path: str | Path,
    *,
    registered_at: str | None = None,
    status: str = "prospective-unscored",
) -> dict[str, Any]:
    path = Path(registry_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    if path.exists():
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError("registry file must contain a JSON array")
    previous = records[-1]["record_sha256"] if records else None
    record = build_registry_record(forecast, previous, registered_at=registered_at, status=status)
    records.append(record)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def verify_registry(registry_path: str | Path) -> list[str]:
    path = Path(registry_path)
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        return ["registry root must be an array"]
    errors: list[str] = []
    previous: str | None = None
    for index, record in enumerate(records):
        if record.get("previous_record_sha256") != previous:
            errors.append(f"record {index}: previous_record_sha256 mismatch")
        if record.get("status") not in _ALLOWED_STATUSES:
            errors.append(f"record {index}: unknown status")
        claimed = record.get("record_sha256")
        unsigned = {key: value for key, value in record.items() if key != "record_sha256"}
        actual = sha256_json(unsigned)
        if claimed != actual:
            errors.append(f"record {index}: record_sha256 mismatch")
        previous = claimed
    return errors
