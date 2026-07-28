from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from fwta.canonical import generalized_realized_outcome
from fwta.engine import run_forecast
from fwta.io import load_structured, validate_instance
from fwta.registry import append_registry, verify_registry
from fwta.report import render_html_report
from fwta.scoring import brier_score, crps_ensemble, interval_score, logarithmic_score
from fwta.uncertainty import crossing_distribution, residual_bootstrap_model_average, transform_scenario_samples


def test_generalized_realization_converges_to_hard_min() -> None:
    q = np.array([10.0, 30.0])
    z = np.array([20.0, 12.0])
    hard = generalized_realized_outcome(q, z, rho=float("inf"))
    soft = generalized_realized_outcome(q, z, rho=120.0)
    assert np.allclose(hard, np.array([10.0, 12.0]))
    assert np.allclose(soft, hard, rtol=0.02)
    constrained = generalized_realized_outcome(q, z, technical_bottleneck=0.5, demand_bottleneck=1.0, realization_bottleneck=0.8, rho=float("inf"))
    assert np.allclose(constrained, np.array([4.0, 9.6]))


def test_probabilistic_ensemble_and_scenarios() -> None:
    t = np.linspace(0.0, 2.0, 16)
    y = 2.0 * np.exp(0.35 * t + 0.04 * t**2)
    future = np.linspace(2.0, 3.0, 8)
    ensemble = residual_bootstrap_model_average(t, y, future, models=("exponential", "accelerating"), n_samples=50, seed=7)
    assert ensemble.samples.shape == (50, 8)
    assert np.all(ensemble.median > 0)
    horizon = future - future[0]
    accelerated = transform_scenario_samples(ensemble.samples, horizon, kind="accelerated", parameters={"annual_growth_shift": 0.2}, seed=8)
    downside = transform_scenario_samples(ensemble.samples, horizon, kind="downside", parameters={"annual_drag": 0.2}, seed=8)
    discontinuous = transform_scenario_samples(ensemble.samples, horizon, kind="discontinuous", parameters={"annual_transition_hazard": 100.0, "jump_multiplier": 1.2, "growth_rate_compounding": 0.2, "initial_growth_bonus": 0.1}, seed=8)
    assert np.median(accelerated[:, -1]) > np.median(ensemble.samples[:, -1])
    assert np.median(downside[:, -1]) < np.median(ensemble.samples[:, -1])
    assert np.median(discontinuous[:, -1]) > np.median(ensemble.samples[:, -1])
    crossing = crossing_distribution(accelerated, [f"2026-{month:02d}-01" for month in range(1, 9)], threshold=float(np.median(accelerated[:, -1]) * 0.9))
    assert 0 <= crossing["probability_by_horizon"] <= 1


def test_complete_engine_report_registry_and_schema(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = load_structured(root / "protocol/v2/examples/canonical-reference-input.yaml")
    payload["modeling"]["bootstrap_samples"] = 50
    run = run_forecast(payload)
    assert run.output["protocol_version"] == "2.0.0"
    assert len(run.output["scenarios"]) == 4
    assert run.output["milestones"]
    p80 = run.output["scenarios"][0]["horizon_summary"]["intervals"]["p80"]
    assert p80["upper"] > p80["lower"]
    diagnostics = run.output["compact_canonical_model"]["diagnostics"]["base"]
    assert diagnostics["transfer_bottleneck"]["p90"][-1] > diagnostics["transfer_bottleneck"]["p10"][-1]
    medians = {scenario["kind"]: scenario["horizon_summary"]["median"] for scenario in run.output["scenarios"]}
    assert medians["downside"] < medians["base"] < medians["accelerated"] < medians["discontinuous"]

    forecast_path = tmp_path / "forecast.json"
    forecast_path.write_text(json.dumps(run.output, indent=2), encoding="utf-8")
    assert validate_instance(forecast_path, root / "protocol/v2/output.schema.json") == []

    report_path = render_html_report(run.output, tmp_path / "forecast.html")
    text = report_path.read_text(encoding="utf-8")
    assert "Compact Canonical Model" in text
    assert "Download forecast JSON" in text

    registry = tmp_path / "registry.json"
    append_registry(run.output, registry, status="demonstration-unscored")
    append_registry({**run.output, "forecast_id": "second-record"}, registry, status="demonstration-unscored")
    assert verify_registry(registry) == []
    records = json.loads(registry.read_text(encoding="utf-8"))
    assert records[1]["previous_record_sha256"] == records[0]["record_sha256"]
    assert records[0]["registry_version"] == "2.0.0"
    assert records[0]["status"] == "demonstration-unscored"


def test_probabilistic_scores() -> None:
    assert brier_score([0.8, 0.2], [1, 0]) == pytest.approx(0.04)
    assert logarithmic_score([0.8, 0.2], [1, 0]) > 0
    assert interval_score(1.0, 3.0, 2.0, 0.8) == pytest.approx(2.0)
    assert crps_ensemble([1.0, 2.0, 3.0], 2.0) >= 0
