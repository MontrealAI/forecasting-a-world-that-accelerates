from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"


def _best_hindcast(output: dict) -> tuple[str, float | None]:
    rows = [row for row in output["model_fit"]["rolling_origin_hindcast"] if row["rmse_log"] is not None]
    if not rows:
        return "—", None
    best = min(rows, key=lambda row: row["rmse_log"])
    return best["model"], best["rmse_log"]


def _escape(text: str) -> str:
    return text.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    result_dir = root / "results/empirical"
    figure_dir = root / "paper/figures"
    table_dir = root / "paper/tables"
    figure_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    cases = [
        ("METR Time Horizon 1.1 excerpt", result_dir / "metr-forecast.json"),
        ("SWE-bench Verified frontier excerpt", result_dir / "swe-bench-forecast.json"),
    ]
    rows = []
    fig, ax = plt.subplots(figsize=(10.8, 5.6))
    for label, path in cases:
        output = json.loads(path.read_text(encoding="utf-8"))
        best_model, best_rmse = _best_hindcast(output)
        base = next(scenario for scenario in output["scenarios"] if scenario["kind"] == "base")
        horizon = base["horizon_summary"]
        p80 = horizon["intervals"]["p80"]
        rows.append(
            {
                "case": label,
                "observations": len(output["observations"]),
                "best_hindcast_model": best_model,
                "best_hindcast_log_rmse": best_rmse,
                "recent_annualized_change": output["current_pace"]["annualized_recent_change"],
                "base_horizon_median": horizon["median"],
                "base_horizon_p80_lower": p80["lower"],
                "base_horizon_p80_upper": p80["upper"],
                "unit": output["target"]["unit"],
            }
        )
        observed_dates = pd.to_datetime([record["date"] for record in output["observations"]])
        observed_values = [record["value"] for record in output["observations"]]
        forecast_dates = pd.to_datetime([point["date"] for point in base["forecast_points"]])
        forecast_values = [point["median"] for point in base["forecast_points"]]
        normalized_observed = [100.0 * value / observed_values[-1] for value in observed_values]
        normalized_forecast = [100.0 * value / observed_values[-1] for value in forecast_values]
        ax.plot(observed_dates, normalized_observed, marker="o", linewidth=1.7, label=f"{label} — observed")
        ax.plot(forecast_dates, normalized_forecast, linestyle="--", linewidth=2.0, label=f"{label} — base median")
    ax.axhline(100.0, linewidth=0.9, alpha=0.35)
    ax.set_ylabel("Index (last observation = 100)")
    ax.set_xlabel("Date")
    ax.set_title("Public-evidence demonstrations: normalized observed and base forecast paths")
    ax.grid(True, alpha=0.2)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(figure_dir / "empirical_cases.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "empirical_cases.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    frame = pd.DataFrame(rows)
    frame.to_csv(result_dir / "empirical_case_summary.csv", index=False)
    tex_rows = []
    for row in rows:
        recent = "--" if row["recent_annualized_change"] is None else f"{100 * row['recent_annualized_change']:.1f}\\%"
        rmse = "--" if row["best_hindcast_log_rmse"] is None else f"{row['best_hindcast_log_rmse']:.3f}"
        tex_rows.append(
            f"{_escape(row['case'])} & {row['observations']} & {_escape(row['best_hindcast_model'])} & {rmse} & {recent} & {row['base_horizon_median']:.1f} [{row['base_horizon_p80_lower']:.1f}, {row['base_horizon_p80_upper']:.1f}] \\\\"
        )
    (table_dir / "generated-empirical-cases.tex").write_text("\n".join(tex_rows) + "\n", encoding="utf-8")

    github = pd.read_csv(root / "data/public/github_operational_evidence.csv")
    github_rows = []
    for record in github.itertuples():
        value = f"{record.value:,.0f}" if float(record.value) >= 1 else f"{100 * float(record.value):.0f}\\%"
        github_rows.append(
            f"{_escape(str(record.measurement_period))} & {_escape(str(record.metric))} & {value} & {_escape(str(record.unit))} \\\\ "
        )
    (table_dir / "generated-github-evidence.tex").write_text("\n".join(github_rows) + "\n", encoding="utf-8")

    summary = {
        "cases": rows,
        "interpretation": "These are source-linked demonstrations of bounded and unbounded trajectory modelling, not prospective validation of future AI or economic outcomes.",
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
