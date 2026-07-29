from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fwta.registry import append_registry, build_registry_record, verify_registry
from fwta.sbom import generate_cyclonedx_sbom
from fwta.timeutil import reproducible_utc_iso, reproducible_utc_now


def _forecast() -> dict[str, object]:
    return {
        "forecast_id": "test-forecast",
        "research_cutoff": "2026-07-28T12:00:00-04:00",
        "target": {"name": "test", "unit": "units"},
        "reproducibility": {"input_sha256": "a" * 64},
    }


def test_reproducible_time_and_sbom(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    assert reproducible_utc_now() == datetime(1970, 1, 1, tzinfo=UTC)
    assert reproducible_utc_iso() == "1970-01-01T00:00:00+00:00"
    lock = tmp_path / "requirements-lock.txt"
    lock.write_text("numpy==2.3.5\nPyYAML==6.0.3\n", encoding="utf-8")
    path = generate_cyclonedx_sbom(tmp_path / "sbom.json", "fwta", "2.0.0", lock)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["bomFormat"] == "CycloneDX"
    assert payload["metadata"]["timestamp"] == "1970-01-01T00:00:00+00:00"
    assert payload["metadata"]["component"]["version"] == "2.0.0"
    assert [component["name"] for component in payload["components"]] == ["numpy", "PyYAML"]
    assert all(component["version"] != "1.0.0" for component in payload["components"])


def test_reproducible_time_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "invalid")
    with pytest.raises(ValueError, match="integer"):
        reproducible_utc_now()
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "-1")
    with pytest.raises(ValueError, match="nonnegative"):
        reproducible_utc_now()
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    assert reproducible_utc_now().tzinfo == UTC


def test_sbom_rejects_non_exact_or_duplicate_lock(tmp_path: Path) -> None:
    bad = tmp_path / "bad.txt"
    bad.write_text("numpy>=2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported requirements-lock entry"):
        generate_cyclonedx_sbom(tmp_path / "bad.json", "fwta", "2.0.0", bad)
    duplicate = tmp_path / "duplicate.txt"
    duplicate.write_text("PyYAML==6.0.3\npyyaml==6.0.3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate locked dependency"):
        generate_cyclonedx_sbom(tmp_path / "duplicate.json", "fwta", "2.0.0", duplicate)


def test_registry_validation_paths(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown registry status"):
        build_registry_record(_forecast(), status="invalid")
    path = tmp_path / "registry.json"
    append_registry(_forecast(), path, registered_at="2026-07-28T16:00:00+00:00")
    assert verify_registry(path) == []
    records = json.loads(path.read_text(encoding="utf-8"))
    records[0]["status"] = "invalid"
    records[0]["previous_record_sha256"] = "bad"
    records[0]["record_sha256"] = "bad"
    path.write_text(json.dumps(records), encoding="utf-8")
    errors = verify_registry(path)
    assert any("previous_record_sha256" in error for error in errors)
    assert any("unknown status" in error for error in errors)
    assert any("record_sha256" in error for error in errors)


def test_registry_root_validation(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    path.write_text("{}", encoding="utf-8")
    assert verify_registry(path) == ["registry root must be an array"]
    with pytest.raises(ValueError, match="JSON array"):
        append_registry(_forecast(), path)
