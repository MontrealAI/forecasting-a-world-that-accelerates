from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .canonical import generalized_bottleneck, realized_outcome
from .metrics import rmse, smape
from .models import DEFAULT_MODELS, fit_model, predict_model, rolling_origin_hindcast
from .regimes import accelerated_exponential, double_exponential, exponential_path, logistic_path
from .workflow import Task, analyze_workflow

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"


def generate_synthetic_series(regime: str, seed: int = 20260728, n: int = 48) -> pd.DataFrame:
    if n < 20:
        raise ValueError("n must be at least 20")
    rng = np.random.default_rng(seed + sum(ord(char) for char in regime))
    time = np.arange(n, dtype=float) / 12.0
    if regime == "linear":
        truth = 1.0 + 0.58 * time
    elif regime == "exponential":
        truth = exponential_path(time, 1.0, 0.44)
    elif regime == "accelerating":
        truth = accelerated_exponential(time, 1.0, 0.18, 0.15)
    elif regime == "logistic":
        truth = logistic_path(time, 0.55, 1.25, 7.5)
    elif regime == "change_point":
        transition = 2.1
        truth = np.exp(math.log(0.9) + 0.12 * time + 0.82 * np.maximum(0.0, time - transition))
    else:
        raise ValueError(f"unknown regime {regime!r}")
    observed = truth * np.exp(rng.normal(0.0, 0.045, size=n))
    return pd.DataFrame({"time_years": time, "truth": truth, "observed": observed, "regime": regime})


def run_hindcast_suite(output_dir: str | Path, seed: int = 20260728) -> pd.DataFrame:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    regimes = ("linear", "exponential", "accelerating", "logistic", "change_point")
    for regime in regimes:
        frame = generate_synthetic_series(regime, seed=seed)
        frame.to_csv(destination / f"synthetic_{regime}.csv", index=False)
        scores = rolling_origin_hindcast(
            frame["time_years"].to_numpy(),
            frame["observed"].to_numpy(),
            min_train=14,
            horizon_steps=3,
            models=DEFAULT_MODELS,
        )
        for model, score in scores.items():
            rows.append(
                {
                    "regime": regime,
                    "model": model,
                    "n_predictions": score["n"],
                    "rmse_log": score["rmse_log"],
                    "mae_log": score["mae_log"],
                    "smape": score["smape"],
                }
            )
    results = pd.DataFrame(rows)
    results.to_csv(destination / "hindcast_scores.csv", index=False)
    winners = (
        results.replace([np.inf, -np.inf], np.nan)
        .dropna(subset=["rmse_log"])
        .sort_values(["regime", "rmse_log"])
        .groupby("regime", as_index=False)
        .first()
    )
    winners.to_csv(destination / "hindcast_winners.csv", index=False)
    return results


def _canonical_components(seed: int = 20260728, n: int = 48) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float) / 12.0
    theta = 0.46 * t + 0.065 * t**2
    cost = 100.0 * np.exp(-0.55 * t)
    duration = 20.0 * np.exp(-0.42 * t)
    automation = 0.14 + 0.69 * (1.0 - np.exp(-0.64 * t))
    parallelism = 1.0 + 7.0 * (1.0 - np.exp(-0.48 * t))
    reliability = 0.70 + 0.275 * (1.0 - np.exp(-0.78 * t))
    elasticities = {
        "theta": 0.85,
        "cost": 0.32,
        "duration": 0.38,
        "automation": 0.45,
        "parallelism": 0.27,
        "reliability": 1.25,
    }
    q0 = 12.0
    technical = (
        q0
        * np.exp(elasticities["theta"] * (theta - theta[0]))
        * (cost[0] / cost) ** elasticities["cost"]
        * (duration[0] / duration) ** elasticities["duration"]
        * ((automation + 0.02) / (automation[0] + 0.02)) ** elasticities["automation"]
        * (parallelism / parallelism[0]) ** elasticities["parallelism"]
        * (reliability / reliability[0]) ** elasticities["reliability"]
    )
    market = 280.0 * np.exp(0.12 * t)
    adoption = 1.0 / (1.0 + np.exp(-(1.28 * t - 2.65)))
    utilization = 0.85 + 0.24 * t
    authority = 0.55 + 0.34 * (1.0 - np.exp(-0.46 * t))
    trust = 0.49 + 0.40 * (1.0 - np.exp(-0.58 * t))
    compute = 0.70 + 0.24 * (1.0 - np.exp(-0.32 * t))
    physical = np.full_like(t, 0.90)
    bottleneck = generalized_bottleneck(np.column_stack([authority, trust, compute, physical]), rho=8.0)
    expected = realized_outcome(technical, market, adoption, utilization, bottleneck)
    observed = expected * np.exp(rng.normal(0.0, 0.035, size=n))
    return pd.DataFrame(
        {
            "time_years": t,
            "theta": theta,
            "cost": cost,
            "duration": duration,
            "automation": automation,
            "parallelism": parallelism,
            "reliability": reliability,
            "technical": technical,
            "market": market,
            "adoption": adoption,
            "utilization": utilization,
            "authority": authority,
            "trust": trust,
            "compute": compute,
            "physical": physical,
            "bottleneck": bottleneck,
            "expected": expected,
            "observed": observed,
        }
    )


def run_ablation_suite(output_dir: str | Path, seed: int = 20260728) -> pd.DataFrame:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    frame = _canonical_components(seed=seed)
    frame.to_csv(destination / "canonical_components.csv", index=False)
    t = frame["time_years"].to_numpy()
    observed = frame["observed"].to_numpy()
    expected = frame["expected"].to_numpy()
    technical = frame["technical"].to_numpy()
    demand = frame["market"].to_numpy() * frame["adoption"].to_numpy() * frame["utilization"].to_numpy()
    bottleneck = frame["bottleneck"].to_numpy()

    reliability_adjusted = technical / (frame["reliability"].to_numpy() / frame["reliability"].iloc[0]) ** 1.25
    ap_adjusted = technical / (
        ((frame["automation"].to_numpy() + 0.02) / (frame["automation"].iloc[0] + 0.02)) ** 0.45
        * (frame["parallelism"].to_numpy() / frame["parallelism"].iloc[0]) ** 0.27
    )
    initial_fit = fit_model("exponential", t[:14], observed[:14])
    stale = predict_model("exponential", t, initial_fit.parameters)
    capability_only = 12.0 * np.exp(0.85 * (frame["theta"].to_numpy() - frame["theta"].iloc[0]))
    predictions = {
        "full_canonical": expected,
        "capability_only": capability_only,
        "no_demand_ceiling": bottleneck * technical,
        "no_bottlenecks": np.minimum(technical, demand),
        "no_reliability_gain": bottleneck * np.minimum(reliability_adjusted, demand),
        "no_automation_or_parallelism": bottleneck * np.minimum(ap_adjusted, demand),
        "stale_constant_exponential": stale,
    }
    rows = []
    for name, prediction in predictions.items():
        rows.append(
            {
                "ablation": name,
                "rmse_log": rmse(np.log(observed), np.log(np.maximum(prediction, 1e-300))),
                "smape": smape(observed, prediction),
                "terminal_ratio_predicted_to_observed": float(prediction[-1] / observed[-1]),
            }
        )
        frame[f"prediction_{name}"] = prediction
    frame.to_csv(destination / "ablation_predictions.csv", index=False)
    results = pd.DataFrame(rows).sort_values("rmse_log")
    results.to_csv(destination / "ablation_scores.csv", index=False)
    return results


def _workflow_demo() -> list[Task]:
    return [
        Task("scope", 0.96, 2, 0.35, 0.20, 2.0, 0.35, ai_cost=1.0, verification_cost=0.5, human_fallback_cost=8.0),
        Task(
            "research_a",
            0.90,
            3,
            1.10,
            0.35,
            4.0,
            dependencies=("scope",),
            ai_cost=2.0,
            verification_cost=0.7,
            human_fallback_cost=15.0,
        ),
        Task(
            "research_b",
            0.88,
            3,
            1.25,
            0.40,
            4.5,
            dependencies=("scope",),
            ai_cost=2.2,
            verification_cost=0.8,
            human_fallback_cost=16.0,
        ),
        Task(
            "model",
            0.84,
            3,
            1.60,
            0.65,
            6.0,
            dependencies=("research_a", "research_b"),
            ai_cost=3.4,
            verification_cost=1.1,
            human_fallback_cost=22.0,
        ),
        Task(
            "review",
            0.94,
            2,
            0.70,
            0.80,
            3.0,
            authority_latency=1.50,
            dependencies=("model",),
            ai_cost=1.5,
            verification_cost=2.0,
            human_fallback_cost=12.0,
        ),
        Task(
            "release",
            0.98,
            2,
            0.30,
            0.35,
            2.0,
            authority_latency=3.00,
            external_latency=1.00,
            dependencies=("review",),
            ai_cost=0.7,
            verification_cost=0.7,
            human_fallback_cost=8.0,
        ),
    ]


def run_workflow_suite(output_dir: str | Path) -> pd.DataFrame:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    for workers in (1, 2, 4, 8, 16, 32, 64):
        result = analyze_workflow(
            _workflow_demo(),
            parallel_workers=workers,
            parallel_efficiency=0.82,
            coordination_coefficient=0.18,
            correlated_failure_penalty=0.035,
        )
        rows.append(
            {
                "workers": workers,
                "total_work_hours": result.total_work,
                "critical_path_hours": result.critical_path,
                "coordination_overhead_hours": result.coordination_overhead,
                "estimated_duration_hours": result.estimated_duration,
                "workflow_reliability": result.workflow_reliability,
                "expected_cost": result.expected_cost,
                "cost_per_verified_success": result.cost_per_verified_success,
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(destination / "workflow_parallelism.csv", index=False)
    return frame


def generate_figures(results_dir: str | Path, figures_dir: str | Path) -> None:
    results = Path(results_dir)
    figures = Path(figures_dir)
    figures.mkdir(parents=True, exist_ok=True)

    t = np.linspace(0.0, 5.0, 240)
    base = exponential_path(t, 1.0, 0.42)
    accelerated = accelerated_exponential(t, 1.0, 0.30, 0.13)
    pre = exponential_path(t, 1.0, 0.26)
    transition_time = 2.4
    x_tau = float(exponential_path(np.array([transition_time]), 1.0, 0.26)[0])
    discontinuous = pre.copy()
    mask = t >= transition_time
    discontinuous[mask] = double_exponential(t[mask], x_tau, transition_time, 1.16, 0.34, 0.52)
    cap = 70.0 * (1.0 + 0.18 * t)
    base = np.minimum(base, cap)
    accelerated = np.minimum(accelerated, cap)
    discontinuous = np.minimum(discontinuous, cap)
    plt.figure(figsize=(8.0, 4.8))
    plt.plot(t, base, label="Base")
    plt.plot(t, accelerated, label="Accelerated")
    plt.plot(t, discontinuous, label="Discontinuous")
    plt.plot(t, cap, linestyle="--", label="Moving constraint ceiling")
    plt.yscale("log")
    plt.xlabel("Years from forecast origin")
    plt.ylabel("Normalized output (log scale)")
    plt.title("Three regimes under a moving constraint ceiling")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "regime_paths.pdf")
    plt.savefig(figures / "regime_paths.png", dpi=180)
    plt.close()

    scores = pd.read_csv(results / "hindcast_scores.csv")
    pivot = scores.pivot(index="model", columns="regime", values="rmse_log")
    plt.figure(figsize=(8.2, 5.0))
    image = plt.imshow(pivot.to_numpy(), aspect="auto")
    plt.colorbar(image, label="Rolling-origin log RMSE")
    plt.xticks(range(len(pivot.columns)), [str(value) for value in pivot.columns], rotation=25, ha="right")
    plt.yticks(range(len(pivot.index)), [str(value) for value in pivot.index])
    plt.title("Controlled hindcasts: model error by generating regime")
    plt.tight_layout()
    plt.savefig(figures / "hindcast_heatmap.pdf")
    plt.savefig(figures / "hindcast_heatmap.png", dpi=180)
    plt.close()

    ablations = pd.read_csv(results / "ablation_scores.csv").sort_values("rmse_log", ascending=True)
    plt.figure(figsize=(8.2, 4.8))
    plt.barh(ablations["ablation"], ablations["rmse_log"])
    plt.xlabel("Log RMSE (lower is better)")
    plt.title("Ablation error in the controlled canonical-model experiment")
    plt.tight_layout()
    plt.savefig(figures / "ablation_error.pdf")
    plt.savefig(figures / "ablation_error.png", dpi=180)
    plt.close()

    workflow = pd.read_csv(results / "workflow_parallelism.csv")
    plt.figure(figsize=(8.0, 4.8))
    plt.plot(workflow["workers"], workflow["estimated_duration_hours"], marker="o", label="Estimated completion")
    plt.axhline(workflow["critical_path_hours"].iloc[0], linestyle="--", label="Critical path floor")
    plt.xscale("log", base=2)
    plt.xlabel("Parallel workers / agents")
    plt.ylabel("Expected duration (hours)")
    plt.title("Parallelism cannot remove the critical path")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "workflow_parallelism.pdf")
    plt.savefig(figures / "workflow_parallelism.png", dpi=180)
    plt.close()

    components = pd.read_csv(results / "canonical_components.csv")
    plt.figure(figsize=(8.0, 4.8))
    plt.plot(components["time_years"], components["technical"], label="Technical capacity")
    demand = components["market"] * components["adoption"] * components["utilization"]
    plt.plot(components["time_years"], demand, label="Absorptive demand")
    plt.plot(components["time_years"], components["expected"], label="Realized outcome")
    plt.yscale("log")
    plt.xlabel("Years")
    plt.ylabel("Normalized units (log scale)")
    plt.title("The canonical model separates capacity, absorption, and realization")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "canonical_branches.pdf")
    plt.savefig(figures / "canonical_branches.png", dpi=180)
    plt.close()


def run_all(output_dir: str | Path, figures_dir: str | Path, seed: int = 20260728) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    hindcasts = run_hindcast_suite(output, seed=seed)
    ablations = run_ablation_suite(output, seed=seed)
    workflow = run_workflow_suite(output)
    generate_figures(output, figures_dir)
    summary = {
        "seed": seed,
        "hindcast_rows": int(len(hindcasts)),
        "ablation_rows": int(len(ablations)),
        "workflow_rows": int(len(workflow)),
        "best_hindcast_models": (
            hindcasts.replace([np.inf, -np.inf], np.nan)
            .dropna(subset=["rmse_log"])
            .sort_values(["regime", "rmse_log"])
            .groupby("regime")
            .first()["model"]
            .to_dict()
        ),
        "best_ablation": str(ablations.sort_values("rmse_log").iloc[0]["ablation"]),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary
