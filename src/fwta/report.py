from __future__ import annotations

import base64
import html
import io
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.1f}"
        return f"{value:,.{digits}f}"
    return html.escape(str(value))


def _pct(value: Any) -> str:
    return "—" if value is None else f"{100.0 * float(value):.1f}%"


def _chart(output: dict[str, Any]) -> str:
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    observations = output["observations"]
    ax.plot(
        pd.to_datetime([row["date"] for row in observations]),
        [row["value"] for row in observations],
        marker="o",
        linewidth=1.8,
        label="Observed",
    )
    for scenario in output["scenarios"]:
        dates = pd.to_datetime([point["date"] for point in scenario["forecast_points"]])
        median = np.asarray([point["median"] for point in scenario["forecast_points"]], dtype=float)
        ax.plot(dates, median, linewidth=2.0, label=scenario["label"])
        if scenario["kind"] == "base":
            lower = np.asarray(
                [point["intervals"]["p80"]["lower"] for point in scenario["forecast_points"]], dtype=float
            )
            upper = np.asarray(
                [point["intervals"]["p80"]["upper"] for point in scenario["forecast_points"]], dtype=float
            )
            ax.fill_between(dates, lower, upper, alpha=0.16, label="Base 80% interval")
    ax.set_title(f"{output['target']['metric']} — observed and scenario paths")
    ax.set_xlabel("Date")
    ax.set_ylabel(output["target"]["unit"])
    ax.grid(True, alpha=0.2)
    ax.legend(ncol=2, frameon=False)
    fig.tight_layout()
    stream = io.BytesIO()
    fig.savefig(stream, format="png", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(stream.getvalue()).decode("ascii")


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "".join(f"<th>{html.escape(item)}</th>" for item in headers)
    body = "".join("<tr>" + "".join(f"<td>{item}</td>" for item in row) + "</tr>" for row in rows)
    return f"<div class='table-wrap'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def render_html_report(output: dict[str, Any], destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    target = output["target"]
    pace = output["current_pace"]
    chart = _chart(output)
    scenario_rows = []
    for scenario in output["scenarios"]:
        summary = scenario["horizon_summary"]
        interval = summary["intervals"].get("p80")
        scenario_rows.append(
            [
                html.escape(scenario["label"]),
                _pct(scenario["probability"]),
                _fmt(summary["median"]),
                f"{_fmt(interval['lower'])} – {_fmt(interval['upper'])}" if interval else "—",
                html.escape("; ".join(scenario.get("assumptions", [])) or "—"),
            ]
        )
    model_rows = []
    for fit in sorted(
        output["model_fit"]["fits"], key=lambda row: float("inf") if row["aicc"] is None else row["aicc"]
    ):
        model_rows.append(
            [
                html.escape(fit["model"]),
                "Yes" if fit["converged"] else "No",
                _fmt(fit["aicc"]),
                _fmt(fit["rmse_log"]),
                _fmt(fit["horizon_prediction"]),
            ]
        )
    milestone_rows = []
    for milestone in output.get("milestones", []):
        for scenario_id, result in milestone["scenario_results"].items():
            milestone_rows.append(
                [
                    html.escape(milestone["label"]),
                    html.escape(scenario_id),
                    _pct(result["probability_by_horizon"]),
                    html.escape(result["median_crossing_date"] or "Not crossed"),
                    html.escape(result["p10_crossing_date"] or "—"),
                    html.escape(result["p90_crossing_date"] or "—"),
                ]
            )
    evidence_rows = [
        [
            html.escape(record["id"]),
            html.escape(record["title"]),
            html.escape(record["quality_grade"]),
            html.escape(record["measurement_date"]),
            html.escape(record.get("publisher", "—")),
        ]
        for record in output.get("evidence", [])
    ]
    bottleneck_rows = [
        [
            html.escape(item["name"]),
            html.escape(item["severity"]),
            html.escape(item["mechanism"]),
            html.escape(item["release_condition"]),
            html.escape(item["mitigation"]),
        ]
        for item in output.get("bottlenecks", [])
    ]
    trigger_rows = [
        [
            html.escape(item["name"]),
            html.escape(item["direction"]),
            html.escape(str(item["threshold"])),
            html.escape(item["forecast_effect"]),
            html.escape(item["action"]),
        ]
        for item in output.get("triggers", [])
    ]
    embedded_json = json.dumps(output, ensure_ascii=False, indent=2).replace("</", "<\\/")
    base = output["executive_forecast"]
    html_text = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{html.escape(target["metric"])} — FWAA Forecast</title>
<style>
:root{{--navy:#14233d;--blue:#2c6174;--gold:#a88446;--ivory:#f7f3ea;--ink:#1d2738;--muted:#626b79;--line:#d9d0c2;--green:#286a55;--red:#8e3c48;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--ivory);color:var(--ink);font:16px/1.52 Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}} a{{color:var(--blue)}}
.hero{{background:var(--navy);color:white;padding:58px 24px 46px;border-bottom:6px solid var(--gold)}} .wrap{{max-width:1180px;margin:auto}} .eyebrow{{letter-spacing:.16em;text-transform:uppercase;color:#d9c392;font-size:12px;font-weight:800}} h1{{font-size:clamp(34px,5vw,66px);line-height:1.03;margin:12px 0 16px}} .subtitle{{max-width:850px;color:#d8dfeb;font-size:19px}} .badges{{display:flex;gap:8px;flex-wrap:wrap;margin-top:24px}} .badge{{border:1px solid #ffffff38;padding:6px 10px;border-radius:999px;font-size:12px}}
main{{padding:30px 24px 80px}} section{{background:#fffdfa;border:1px solid var(--line);padding:26px;margin:18px 0;box-shadow:0 10px 30px #13213a0a}} h2{{color:var(--navy);font-size:27px;margin:0 0 18px}} h3{{color:var(--blue)}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}} .card{{border:1px solid var(--line);padding:17px;background:white}} .label{{text-transform:uppercase;letter-spacing:.08em;font-size:11px;color:var(--muted);font-weight:800}} .value{{font-size:28px;font-weight:800;color:var(--navy);margin-top:5px}} .small{{font-size:13px;color:var(--muted)}}
.equation{{overflow:auto;background:var(--navy);color:white;padding:22px;text-align:center;font-family:"Times New Roman",serif;font-size:21px;line-height:1.7;border-left:5px solid var(--gold)}} .equation small{{display:block;color:#d8dfeb;font:14px/1.5 ui-sans-serif,system-ui;margin-top:8px}} img.chart{{width:100%;height:auto;border:1px solid var(--line);background:white}}
table{{width:100%;border-collapse:collapse;font-size:14px}} th{{background:var(--navy);color:white;text-align:left;padding:10px}} td{{border-bottom:1px solid var(--line);padding:10px;vertical-align:top}} .table-wrap{{overflow:auto}} .notice{{border-left:5px solid var(--gold);background:#f4eddf;padding:16px}} .warning{{border-left:5px solid var(--red);background:#fbf0f1;padding:16px}} pre{{white-space:pre-wrap;word-break:break-word;background:#101827;color:#e8edf5;padding:18px;max-height:520px;overflow:auto}}
.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}} button{{appearance:none;border:0;background:var(--gold);color:#101827;padding:11px 15px;font-weight:800;cursor:pointer}} button.secondary{{background:white;border:1px solid var(--line)}} footer{{padding:35px 24px;background:var(--navy);color:#cbd4e2;font-size:13px}} @media print{{.actions{{display:none}} section{{box-shadow:none;break-inside:avoid}}}}
</style></head><body>
<header class='hero'><div class='wrap'><div class='eyebrow'>Forecasting a World That Accelerates Ω · Engine v{html.escape(output["engine_version"])}</div><h1>{html.escape(target["metric"])}</h1><div class='subtitle'>{html.escape(target["question"])}</div><div class='badges'><span class='badge'>Cutoff {html.escape(output["research_cutoff"][:10])}</span><span class='badge'>Horizon {html.escape(target["horizon_end"])}</span><span class='badge'>{html.escape(target["scope"])}</span><span class='badge'>Forecast ID {html.escape(output["forecast_id"])}</span></div></div></header>
<main><div class='wrap'>
<section><h2>Executive forecast</h2><div class='grid'><div class='card'><div class='label'>Base horizon median</div><div class='value'>{_fmt(base["base_horizon_median"])}</div><div class='small'>{html.escape(target["unit"])}</div></div><div class='card'><div class='label'>Base 80% interval</div><div class='value'>{_fmt(base["base_horizon_p80"]["lower"])}–{_fmt(base["base_horizon_p80"]["upper"])}</div><div class='small'>Model, residual and scenario uncertainty</div></div><div class='card'><div class='label'>Recent annualized pace</div><div class='value'>{_pct(pace.get("annualized_recent_change"))}</div><div class='small'>Log-interpolated six-month window</div></div><div class='card'><div class='label'>Recalculate</div><div class='value' style='font-size:21px'>{html.escape(output["recalculation"]["scheduled_date"])}</div><div class='small'>Earlier if a trigger fires</div></div></div><p class='notice'><strong>Decision implication.</strong> {html.escape(base["decision_implication"])}</p></section>
<section><h2>Compact Canonical Model</h2><div class='equation'>Y<sub>s</sub>(t) = B<sub>s</sub>(t) min &#123; Q<sub>0</sub> exp[∫<sub>0</sub><sup>t</sup> g<sub>Q,s</sub>(u)du], M<sub>s</sub>(t)D<sub>s</sub>(t)U<sub>s</sub>(t) &#125;<small>{html.escape(output["compact_canonical_model"]["plain_language"])}</small></div><h3>Generalized realization family</h3><div class='equation'>Y = B<sup>X</sup>[ α(B<sup>Q</sup>Q)<sup>−ρ</sup> + (1−α)(B<sup>Z</sup>Z)<sup>−ρ</sup> ]<sup>−1/ρ</sup><small>As ρ → ∞, the generalized family converges to the compact hard minimum.</small></div></section>
<section><h2>Scenario forecast</h2>{_table(["Scenario", "Probability", "Horizon median", "80% interval", "Assumptions"], scenario_rows)}<img class='chart' alt='Forecast chart' src='data:image/png;base64,{chart}'></section>
<section><h2>Current pace</h2><div class='grid'><div class='card'><div class='label'>Current</div><div class='value'>{_fmt(pace["anchor_values"]["current"])}</div></div><div class='card'><div class='label'>6 months ago</div><div class='value'>{_fmt(pace["anchor_values"]["six_months_ago"])}</div></div><div class='card'><div class='label'>12 months ago</div><div class='value'>{_fmt(pace["anchor_values"]["twelve_months_ago"])}</div></div><div class='card'><div class='label'>Log-growth acceleration</div><div class='value'>{_fmt(pace.get("log_growth_acceleration"))}</div><div class='small'>per year²</div></div></div><p class='small'>{html.escape(pace.get("note", ""))}</p></section>
<section><h2>Model competition</h2>{_table(["Model", "Converged", "AICc", "Log RMSE", "Horizon prediction"], model_rows)}</section>
<section><h2>Milestones</h2>{_table(["Milestone", "Scenario", "Probability", "Median crossing", "Early 10%", "Late 90%"], milestone_rows) if milestone_rows else "<p>No milestones supplied.</p>"}</section>
<section><h2>Bottlenecks</h2>{_table(["Constraint", "Severity", "Mechanism", "Release condition", "Mitigation"], bottleneck_rows) if bottleneck_rows else "<p>No bottlenecks supplied.</p>"}</section>
<section><h2>Trigger dashboard</h2>{_table(["Trigger", "Direction", "Threshold", "Forecast effect", "Action"], trigger_rows) if trigger_rows else "<p>No triggers supplied.</p>"}</section>
<section><h2>Optimal plan for today’s regime</h2><div class='grid'>{"".join(f"<div class='card'><div class='label'>{html.escape(key.replace('_', ' '))}</div><div>{html.escape('; '.join(value) if isinstance(value, list) else str(value))}</div></div>" for key, value in output.get("optimal_plan", {}).items())}</div></section>
<section><h2>Evidence ledger</h2>{_table(["ID", "Evidence", "Grade", "Measurement date", "Publisher"], evidence_rows) if evidence_rows else "<p>No evidence records supplied.</p>"}</section>
<section><h2>Confidence and limitations</h2><div class='grid'><div class='card'><div class='label'>Evidence quality score</div><div class='value'>{_fmt(output["confidence"]["evidence_quality_score"])}</div></div><div class='card'><div class='label'>Model disagreement</div><div class='value'>{_fmt(output["confidence"]["horizon_log_model_disagreement"])}</div></div><div class='card'><div class='label'>Base p80 relative width</div><div class='value'>{_pct(output["confidence"]["base_horizon_p80_relative_width"])}</div></div></div><p class='warning'><strong>Boundary.</strong> {html.escape(output["legal_notice"])}</p></section>
<section><h2>Reproducibility</h2><div class='grid'><div class='card'><div class='label'>Input SHA-256</div><div class='small' style='word-break:break-all'>{html.escape(output["reproducibility"]["input_sha256"])}</div></div><div class='card'><div class='label'>Seed</div><div class='value'>{output["reproducibility"]["random_seed"]}</div></div><div class='card'><div class='label'>Bootstrap samples</div><div class='value'>{output["reproducibility"]["bootstrap_samples_successful"]}</div></div></div><div class='actions'><button onclick='downloadJSON()'>Download forecast JSON</button><button class='secondary' onclick='window.print()'>Print / Save PDF</button></div><details><summary>Open complete machine-readable result</summary><pre id='json'>{html.escape(embedded_json)}</pre></details></section>
</div></main><footer><div class='wrap'>Forecasting a World That Accelerates Ω · MONTREAL.AI &amp; QUEBEC.AI · Version {html.escape(output["engine_version"])}. This report is a reproducible decision-support artifact, not a guarantee.</div></footer>
<script>const DATA={embedded_json};function downloadJSON(){{const blob=new Blob([JSON.stringify(DATA,null,2)],{{type:'application/json'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`${{DATA.forecast_id}}.json`;a.click();URL.revokeObjectURL(a.href);}}</script></body></html>"""
    path.write_text(html_text, encoding="utf-8")
    return path
