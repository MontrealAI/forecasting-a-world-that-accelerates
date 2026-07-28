from pathlib import Path

import pytest

from fwta.experiments import run_all
from fwta.io import validate_instance
from fwta.provenance import build_manifest


def test_example_input_validates() -> None:
    root = Path(__file__).resolve().parents[1]
    errors = validate_instance(root / "protocol/examples/example-input.yaml", root / "protocol/input.schema.json")
    assert errors == []


@pytest.mark.slow
def test_experiments_are_reproducible(tmp_path: Path) -> None:
    summary = run_all(tmp_path / "results", tmp_path / "figures", seed=20260728)
    assert summary["best_ablation"] == "full_canonical"
    assert (tmp_path / "results/summary.json").exists()
    assert (tmp_path / "figures/regime_paths.pdf").exists()


def test_manifest(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    records = build_manifest(tmp_path)
    assert records[0]["path"] == "a.txt"
    assert len(records[0]["sha256"]) == 64
