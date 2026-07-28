from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "paper" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def esc(value: object) -> str:
    text = str(value).replace("_", " ")
    for old, new in (("&", r"\&"), ("%", r"\%"), ("#", r"\#")):
        text = text.replace(old, new)
    return text


def write_table(path: Path, header: list[str], rows: list[list[str]], spec: str) -> None:
    row_end = chr(92) * 2
    lines = [f"\\begin{{tabular}}{{{spec}}}", r"\toprule", " & ".join(header) + " " + row_end, r"\midrule"]
    lines.extend(" & ".join(row) + " " + row_end for row in rows)
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


hind = pd.read_csv(ROOT / "results/reference/hindcast_winners.csv")
write_table(
    TABLES / "generated-hindcast-winners.tex",
    ["Generating regime", "Lowest-error model", "Log RMSE"],
    [[esc(r.regime), esc(r.model), f"{r.rmse_log:.3f}"] for r in hind.itertuples()],
    "lll",
)

abl = pd.read_csv(ROOT / "results/reference/ablation_scores.csv").sort_values("rmse_log")
write_table(
    TABLES / "generated-ablation.tex",
    ["Specification", "Log RMSE", "Terminal ratio"],
    [
        [esc(r.ablation), f"{r.rmse_log:.3f}", f"{r.terminal_ratio_predicted_to_observed:.2f}x"]
        for r in abl.itertuples()
    ],
    "lrr",
)

flow = pd.read_csv(ROOT / "results/reference/workflow_parallelism.csv")
selected = flow[flow["workers"].isin([1, 2, 4, 8, 32, 64])]
write_table(
    TABLES / "generated-workflow.tex",
    ["Workers", "Duration (h)", "Critical path (h)", "Coord. overhead (h)"],
    [
        [
            str(int(r.workers)),
            f"{r.estimated_duration_hours:.2f}",
            f"{r.critical_path_hours:.2f}",
            f"{r.coordination_overhead_hours:.2f}",
        ]
        for r in selected.itertuples()
    ],
    "rrrr",
)
