from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fwta.ablation import canonical_ablation_suite
from fwta.io import load_structured
from fwta.models import DEFAULT_MODELS, fit_all_models, predict_model, rolling_origin_hindcast
from fwta.synthetic import canonical_system_series, regime_shift_series
from fwta.workflow import analyze_workflow, task_from_mapping


def safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, np.floating):
        return safe(float(value))
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return [safe(x) for x in value.tolist()]
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [safe(v) for v in value]
    return value


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def latex_escape(text: str) -> str:
    replacements = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(char, char) for char in text)


def public_experiment() -> dict:
    frame = pd.read_csv(ROOT / "data/public/metr_time_horizon_excerpt.csv")
    usable = frame[frame["use_for_hindcast"]].copy()
    dates = pd.to_datetime(usable["release_date"], utc=True)
    time = ((dates - dates.iloc[0]).dt.total_seconds() / (365.2425 * 86400)).to_numpy(float)
    values = usable["p50_minutes"].to_numpy(float)
    fits = fit_all_models(time, values)
    hindcast = rolling_origin_hindcast(time, values, min_train=7, horizon_steps=1)
    results = {"data_points": len(usable), "fits": {name: fit.to_dict() for name, fit in fits.items()}, "hindcast": hindcast}
    write_json(ROOT / "results/reference/public_metr_results.json", results)

    future = np.linspace(time.min(), time.max() + 1, 250)
    plt.figure(figsize=(8.4, 5.2))
    plt.scatter(dates, values, label="Public excerpt")
    for model in ("exponential", "accelerating", "change_point"):
        fit = fits[model]
        if fit.converged:
            future_dates = dates.iloc[0] + pd.to_timedelta(future * 365.2425, unit="D")
            plt.plot(future_dates, predict_model(model, future, fit.parameters), label=model.replace("_", " "))
    plt.yscale("log")
    plt.ylabel("50% task horizon (human-expert minutes, log scale)")
    plt.xlabel("Model release date")
    plt.title("Illustrative model fits to a public METR excerpt")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ROOT / "paper/figures/metr_excerpt_fits.pdf")
    plt.savefig(ROOT / "paper/figures/metr_excerpt_fits.png", dpi=180)
    plt.close()

    rows = sorted(((name, record["n"], record["rmse_log"], record["smape"]) for name, record in hindcast.items() if record["n"]), key=lambda x: x[2])
    lines = [r"\begin{tabular}{lrrr}", r"\toprule", r"Model & Forecasts & RMSE (log) & sMAPE \\", r"\midrule"]
    for name, n, rmse_log, smape in rows:
        lines.append(f"{latex_escape(name.replace('_',' '))} & {n} & {rmse_log:.3f} & {100*smape:.1f}\\% " + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (ROOT / "paper/tables/metr_hindcast.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return results


def synthetic_regime_experiment() -> dict:
    series = regime_shift_series()
    frame = series.frame
    frame.to_csv(ROOT / "data/synthetic/regime_shift_seed_20260728.csv", index=False)
    time = frame["time_years"].to_numpy(float)
    values = frame["value"].to_numpy(float)
    full = rolling_origin_hindcast(time, values, min_train=12, models=DEFAULT_MODELS)
    stale = rolling_origin_hindcast(time, values, min_train=12, models=("linear", "exponential", "logistic"))
    result = {"description": series.description, "seed": 20260728, "known_transition_year": 2.0, "full": full, "restricted_stale_regimes": stale}
    write_json(ROOT / "results/reference/synthetic_regime_hindcast.json", result)

    plt.figure(figsize=(8.4, 5.2))
    plt.plot(time, frame["truth"], label="Known latent trajectory")
    plt.scatter(time, values, s=18, label="Synthetic observations")
    plt.axvline(2.0, linestyle="--", label="Known regime transition")
    plt.yscale("log")
    plt.xlabel("Years")
    plt.ylabel("Synthetic outcome (log scale)")
    plt.title("Synthetic regime-transition identification test")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ROOT / "paper/figures/synthetic_regime.pdf")
    plt.savefig(ROOT / "paper/figures/synthetic_regime.png", dpi=180)
    plt.close()
    return result


def canonical_ablation_experiment() -> dict:
    series = canonical_system_series()
    frame = series.frame
    frame.to_csv(ROOT / "data/synthetic/canonical_system_seed_20260728.csv", index=False)
    features = {
        "capability": frame["theta"].to_numpy(),
        "cost_efficiency": -np.log(frame["cost"].to_numpy()),
        "time_compression": -np.log(frame["duration"].to_numpy()),
        "automation": np.log(frame["automation"].to_numpy()),
        "parallelism": np.log(frame["parallelism"].to_numpy()),
        "reliability": np.log(frame["reliability"].to_numpy()),
    }
    results = canonical_ablation_suite(frame["value"], features, frame["market"], frame["adoption"], frame["utilization"], frame["bottleneck"])
    write_json(ROOT / "results/reference/canonical_ablation.json", results)
    labels = list(results)
    errors = [results[label]["rmse_log"] for label in labels]
    plt.figure(figsize=(8.4, 5.2))
    plt.barh([label.replace("_", " ") for label in labels], errors)
    plt.xlabel("In-sample RMSE (log outcome; lower is better)")
    plt.title("Synthetic canonical-model ablations")
    plt.tight_layout()
    plt.savefig(ROOT / "paper/figures/canonical_ablation.pdf")
    plt.savefig(ROOT / "paper/figures/canonical_ablation.png", dpi=180)
    plt.close()

    lines = [r"\begin{tabular}{lr}", r"\toprule", r"Specification & RMSE (log) \\", r"\midrule"]
    for label, error in sorted(zip(labels, errors), key=lambda item: item[1]):
        lines.append(f"{latex_escape(label.replace('_',' '))} & {error:.3f} " + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (ROOT / "paper/tables/canonical_ablation.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return results


def workflow_experiment() -> dict:
    payload = load_structured(ROOT / "protocol/examples/example-workflow.yaml")
    tasks = [task_from_mapping(record) for record in payload["tasks"]]
    result = analyze_workflow(tasks, payload["parallel_workers"], payload["parallel_efficiency"], payload["coordination_coefficient"], payload["correlated_failure_penalty"])
    write_json(ROOT / "results/reference/workflow_analysis.json", asdict(result))
    metrics = pd.DataFrame(result.task_metrics).T
    plt.figure(figsize=(8.4, 5.2))
    plt.bar(metrics.index, metrics["expected_duration"])
    plt.ylabel("Expected task duration (illustrative hours)")
    plt.xlabel("Task")
    plt.title("Workflow duration decomposition before critical-path aggregation")
    plt.tight_layout()
    plt.savefig(ROOT / "paper/figures/workflow_duration.pdf")
    plt.savefig(ROOT / "paper/figures/workflow_duration.png", dpi=180)
    plt.close()
    return asdict(result)


def summary_table(results: dict) -> None:
    public = results["public"]["hindcast"]
    best_public = min(((name, rec["rmse_log"]) for name, rec in public.items() if rec["n"] and rec["rmse_log"] is not None), key=lambda item: item[1])
    synthetic = results["synthetic"]["full"]
    best_synthetic = min(((name, rec["rmse_log"]) for name, rec in synthetic.items() if rec["n"] and rec["rmse_log"] is not None), key=lambda item: item[1])
    text = "\n".join([
        r"\begin{tabular}{lll}", r"\toprule", r"Evaluation & Best model by log-RMSE & Score \\", r"\midrule",
        f"Public excerpt (illustrative) & {latex_escape(best_public[0].replace('_',' '))} & {best_public[1]:.3f} " + r"\\",
        f"Synthetic regime shift & {latex_escape(best_synthetic[0].replace('_',' '))} & {best_synthetic[1]:.3f} " + r"\\",
        r"\bottomrule", r"\end{tabular}",
    ])
    (ROOT / "paper/tables/evaluation_summary.tex").write_text(text + "\n", encoding="utf-8")


def main() -> int:
    for directory in (ROOT / "paper/figures", ROOT / "paper/tables", ROOT / "results/reference", ROOT / "data/synthetic"):
        directory.mkdir(parents=True, exist_ok=True)
    results = {
        "public": public_experiment(),
        "synthetic": synthetic_regime_experiment(),
        "ablation": canonical_ablation_experiment(),
        "workflow": workflow_experiment(),
    }
    summary_table(results)
    write_json(ROOT / "results/reference/experiment_index.json", {"generated_at": "2026-07-28T14:00:00-04:00", "experiments": list(results)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
