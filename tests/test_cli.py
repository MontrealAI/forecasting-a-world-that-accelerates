from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from fwta import cli


def test_cli_fit_hindcast_and_synthetic(tmp_path: Path) -> None:
    csv_path = tmp_path / "series.csv"
    pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=14, freq="MS"),
            "value": np.exp(np.arange(14) * 0.05),
            "include": [True] * 13 + [False],
        }
    ).to_csv(csv_path, index=False)

    fit_path = tmp_path / "fit.json"
    assert (
        cli.main(
            [
                "fit",
                str(csv_path),
                "--time",
                "date",
                "--include-column",
                "include",
                "--models",
                "linear,exponential",
                "--output",
                str(fit_path),
            ]
        )
        == 0
    )
    fitted = json.loads(fit_path.read_text(encoding="utf-8"))
    assert fitted["exponential"]["converged"] is True

    hindcast_path = tmp_path / "hindcast.json"
    assert (
        cli.main(
            [
                "hindcast",
                str(csv_path),
                "--time",
                "date",
                "--include-column",
                "include",
                "--min-train",
                "7",
                "--models",
                "linear,exponential",
                "--output",
                str(hindcast_path),
            ]
        )
        == 0
    )
    hindcast = json.loads(hindcast_path.read_text(encoding="utf-8"))
    assert hindcast["exponential"]["n"] > 0

    synthetic_path = tmp_path / "synthetic.csv"
    assert cli.main(["synthetic", "--kind", "canonical", "--periods", "13", "--output", str(synthetic_path)]) == 0
    assert synthetic_path.exists()


def test_cli_workflow_validation_manifest_and_run_all(tmp_path: Path, monkeypatch, capsys) -> None:
    root = Path(__file__).resolve().parents[1]
    workflow_output = tmp_path / "workflow.json"
    assert cli.main(["workflow", str(root / "protocol/examples/example-workflow.yaml"), "--output", str(workflow_output)]) == 0
    assert json.loads(workflow_output.read_text(encoding="utf-8"))["estimated_duration"] > 0

    assert cli.main(["validate", str(root / "protocol/examples/example-input.yaml"), str(root / "protocol/input.schema.json")]) == 0
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}", encoding="utf-8")
    assert cli.main(["validate", str(invalid), str(root / "protocol/input.schema.json")]) == 1

    (tmp_path / "tracked.txt").write_text("tracked", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    assert cli.main(["manifest", "--root", str(tmp_path), "--output", str(manifest)]) == 0
    assert json.loads(manifest.read_text(encoding="utf-8"))["algorithm"] == "SHA-256"

    monkeypatch.setattr(cli, "run_all", lambda output, figures, seed: {"seed": seed, "ok": True})
    assert cli.main(["run-all", "--output", str(tmp_path / "out"), "--figures", str(tmp_path / "fig"), "--seed", "9"]) == 0
    assert '"ok": true' in capsys.readouterr().out


def test_cli_helpers_and_module_entry(monkeypatch) -> None:
    assert cli._json_safe({"x": float("inf"), "items": [float("nan"), 2.0]}) == {"x": None, "items": [None, 2.0]}
    numeric = pd.DataFrame({"time": [0, 1, 2]})
    assert np.array_equal(cli._time_from_frame(numeric, "time"), np.array([0.0, 1.0, 2.0]))
    parser = cli.build_parser()
    assert parser.parse_args(["synthetic"]).kind == "regime"


def test_read_frame_include_column_variants(tmp_path: Path) -> None:
    path = tmp_path / "flags.csv"
    pd.DataFrame({"value": [1, 2, 3, 4], "flag": ["yes", "no", "1", "false"]}).to_csv(path, index=False)
    assert cli._read_frame(path, "flag")["value"].tolist() == [1, 3]
    try:
        cli._read_frame(path, "missing")
    except ValueError as exc:
        assert "include column not found" in str(exc)
    else:
        raise AssertionError("missing include column should fail")
