from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fwta.probabilistic import probabilistic_rolling_origin_hindcast

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"

ROOT = Path(__file__).resolve().parents[1]


def _safe(value: Any) -> Any:
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, np.ndarray):
        return [_safe(item) for item in value.tolist()]
    if isinstance(value, dict):
        return {str(key): _safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_safe(item) for item in value]
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _latex_escape(text: str) -> str:
    replacements = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_"}
    return "".join(replacements.get(char, char) for char in text)


def run_metr(seed: int = 20260728, draws: int = 160) -> dict[str, Any]:
    frame = pd.read_csv(ROOT / "data/public/metr_time_horizon_excerpt.csv")
    usable = frame[frame["use_for_hindcast"].astype(bool)].copy()
    dates = pd.to_datetime(usable["release_date"], utc=True)
    time = ((dates - dates.iloc[0]).dt.total_seconds() / (365.2425 * 86400.0)).to_numpy(dtype=float)
    values = usable["p50_minutes"].to_numpy(dtype=float)
    pools = {
        "exponential_only": ("exponential",),
        "accelerating_only": ("accelerating",),
        "change_point_only": ("change_point",),
        "full_model_average": ("linear", "exponential", "accelerating", "decaying_acceleration", "logistic", "change_point"),
    }
    results: dict[str, Any] = {
        "benchmark": "METR Time Horizon 1.1 compact public excerpt",
        "data_points": int(len(usable)),
        "forecast_origins": int(len(usable) - 7),
        "minimum_training_points": 7,
        "horizon_steps": 1,
        "draws_per_origin": draws,
        "random_seed": seed,
        "measurement_boundary_minutes": 960.0,
        "status": "Limited public-data demonstration; not an authoritative mirror or economy-wide validation.",
        "source": "https://metr.org/time-horizons/",
        "model_pools": {},
    }
    for index, (name, pool) in enumerate(pools.items()):
        results["model_pools"][name] = probabilistic_rolling_origin_hindcast(
            time,
            values,
            min_train=7,
            horizon_steps=1,
            models=pool,
            draws=draws,
            seed=seed + index * 1009,
        )

    destination = ROOT / "results/ceiling/metr_probabilistic_hindcast.json"
    _write_json(destination, results)

    ranking = sorted(
        (
            name,
            record["rmse_log"],
            record["mean_crps"],
            record["mean_wis"],
            record["coverage80"],
            record["coverage95"],
        )
        for name, record in results["model_pools"].items()
    )
    ranking.sort(key=lambda row: row[3])
    lines = [
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Model pool & RMSE (log) & CRPS & WIS & 80\% cov. & 95\% cov. \\",
        r"\midrule",
    ]
    for name, rmse, crps, wis, coverage80, coverage95 in ranking:
        lines.append(
            f"{_latex_escape(name.replace('_', ' '))} & {rmse:.3f} & {crps:.1f} & {wis:.1f} & {100 * coverage80:.0f}\\% & {100 * coverage95:.0f}\\% " + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (ROOT / "paper/tables/metr_probabilistic_hindcast.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    full = results["model_pools"]["full_model_average"]["records"]
    x = np.arange(len(full))
    actual = np.asarray([item["actual"] for item in full], dtype=float)
    median = np.asarray([item["median"] for item in full], dtype=float)
    lower80 = np.asarray([item["lower80"] for item in full], dtype=float)
    upper80 = np.asarray([item["upper80"] for item in full], dtype=float)
    plt.figure(figsize=(8.4, 5.2))
    plt.fill_between(x, lower80, upper80, alpha=0.2, label="80% predictive interval")
    plt.plot(x, median, marker="o", label="Forecast median")
    plt.plot(x, actual, marker="s", label="Observed")
    plt.yscale("log")
    plt.xticks(x, [str(item + 1) for item in x])
    plt.xlabel("Rolling forecast origin")
    plt.ylabel("p50 task horizon in human-expert minutes (log scale)")
    plt.title("Probabilistic rolling-origin hindcast on the public METR excerpt")
    plt.legend()
    plt.tight_layout()
    plt.savefig(ROOT / "paper/figures/metr_probabilistic_hindcast.pdf")
    plt.savefig(ROOT / "paper/figures/metr_probabilistic_hindcast.png", dpi=180)
    plt.close()
    return results


def run_btos_audit() -> dict[str, Any]:
    frame = pd.read_csv(ROOT / "data/public/census_btos_ai_adoption_anchors.csv")
    groups: dict[str, Any] = {}
    for name, subset in frame.groupby("comparability_group", sort=True):
        subset = subset.sort_values("reference_end")
        groups[name] = {
            "measure": str(subset.iloc[0]["measure"]),
            "n_anchors": int(len(subset)),
            "first_anchor": subset.iloc[0].to_dict(),
            "last_anchor": subset.iloc[-1].to_dict(),
            "fit_permitted_within_group": len(subset) >= 4 and bool((subset["exactness"] == "exact").all()),
        }
    result = {
        "audit": "U.S. Census BTOS AI-use measurement break",
        "status": "Comparability audit, not a forecast fit.",
        "groups": groups,
        "break_date": "2025-11-17",
        "break_description": "The core question changed from AI use in producing goods or services to AI use in any business function.",
        "decision": "Do not splice goods_services_v1 and any_business_function_v2 into one adoption-growth series without a validated bridge study.",
        "why_it_matters": "A naive concatenation would attribute a material part of the level jump to adoption rather than to a broader measurement construct.",
        "primary_sources": [
            "https://www.census.gov/library/stories/2023/11/businesses-use-ai.html",
            "https://www.census.gov/library/working-papers/2024/adrm/CES-WP-24-16.html",
            "https://www.census.gov/about/history/stories/monthly/2025/july-2025.html",
            "https://www.census.gov/library/working-papers/2026/adrm/CES-WP-26-25.html",
            "https://www.census.gov/library/stories/2026/05/ai-use-businesses.html",
        ],
    }
    _write_json(ROOT / "results/ceiling/btos_measurement_break_audit.json", result)
    lines = [
        r"\begin{tabular}{p{0.27\linewidth}p{0.28\linewidth}rrp{0.22\linewidth}}",
        r"\toprule",
        r"Comparability group & Construct & First & Last & Decision \\",
        r"\midrule",
    ]
    for name, record in groups.items():
        first = record["first_anchor"]
        last = record["last_anchor"]
        lines.append(
            f"{_latex_escape(name)} & {_latex_escape(record['measure'])} & {float(first['value_percent']):.1f}\\% & {float(last['value_percent']):.1f}\\% & Do not splice across the 2025 wording break. " + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (ROOT / "paper/tables/btos_measurement_break.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    summary = {"metr": run_metr(), "btos": run_btos_audit()}
    _write_json(ROOT / "results/ceiling/benchmark_index.json", summary)
    print(json.dumps({"metr_pools": list(summary["metr"]["model_pools"]), "btos_decision": summary["btos"]["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
