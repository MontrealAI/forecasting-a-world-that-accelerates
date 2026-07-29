from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .canonical import generalized_realized_outcome
from .models import DEFAULT_MODELS, fit_all_models, predict_model, rolling_origin_hindcast
from .timeutil import reproducible_utc_iso
from .uncertainty import (
    crossing_distribution,
    residual_bootstrap_model_average,
    summarize_samples,
    transform_scenario_samples,
)

_ENGINE_VERSION = "2.0.0"
_SECONDS_PER_YEAR = 365.2425 * 86400.0
_QUALITY_WEIGHTS = {"A": 1.0, "B": 0.8, "C": 0.55, "D": 0.25}


@dataclass(frozen=True)
class ForecastRun:
    output: dict[str, Any]
    dates: list[str]
    scenario_samples: dict[str, np.ndarray]


def _parse_date(value: str) -> pd.Timestamp:
    stamp = pd.Timestamp(value)
    stamp = stamp.tz_localize("UTC") if stamp.tzinfo is None else stamp.tz_convert("UTC")
    return stamp


def _year_values(stamps: pd.DatetimeIndex | pd.Series, origin: pd.Timestamp) -> np.ndarray:
    return np.asarray((stamps - origin) / pd.Timedelta(seconds=_SECONDS_PER_YEAR), dtype=float)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _input_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _forecast_dates(cutoff: pd.Timestamp, horizon_end: pd.Timestamp, frequency: str) -> pd.DatetimeIndex:
    if horizon_end <= cutoff:
        raise ValueError("target.horizon_end must be later than research_cutoff")
    if frequency == "weekly":
        dates = pd.date_range(cutoff, horizon_end, freq="7D", tz="UTC")
    elif frequency == "quarterly":
        dates = pd.date_range(cutoff, horizon_end, freq="3MS", tz="UTC")
    else:
        dates = pd.date_range(cutoff, horizon_end, freq="MS", tz="UTC")
    values = [cutoff]
    values.extend(stamp for stamp in dates if stamp > cutoff and stamp < horizon_end)
    values.append(horizon_end)
    return pd.DatetimeIndex(sorted(set(values)))


def _interpolate_log_value(dates: pd.DatetimeIndex, values: np.ndarray, target: pd.Timestamp) -> float | None:
    if target < dates.min() or target > dates.max():
        return None
    x = ((dates - dates[0]).total_seconds() / _SECONDS_PER_YEAR).to_numpy(dtype=float)
    tx = float((target - dates[0]).total_seconds() / _SECONDS_PER_YEAR)
    return float(np.exp(np.interp(tx, x, np.log(values))))


def _pace(dates: pd.DatetimeIndex, values: np.ndarray, cutoff: pd.Timestamp) -> dict[str, Any]:
    anchors = {
        "current": cutoff,
        "six_months_ago": cutoff - pd.DateOffset(months=6),
        "twelve_months_ago": cutoff - pd.DateOffset(months=12),
    }
    levels = {name: _interpolate_log_value(dates, values, stamp) for name, stamp in anchors.items()}
    current, six, twelve = levels["current"], levels["six_months_ago"], levels["twelve_months_ago"]
    output: dict[str, Any] = {
        "anchor_dates": {name: stamp.date().isoformat() for name, stamp in anchors.items()},
        "anchor_values": levels,
        "recent_continuous_growth": None,
        "prior_continuous_growth": None,
        "annualized_recent_change": None,
        "annualized_prior_change": None,
        "log_growth_acceleration": None,
        "recent_doubling_time_years": None,
    }
    if current is None or six is None or twelve is None or min(current, six, twelve) <= 0:
        output["note"] = "Insufficient comparable history to calculate both six-month windows."
        return output
    recent_years = max((anchors["current"] - anchors["six_months_ago"]).total_seconds() / _SECONDS_PER_YEAR, 1e-9)
    prior_years = max(
        (anchors["six_months_ago"] - anchors["twelve_months_ago"]).total_seconds() / _SECONDS_PER_YEAR, 1e-9
    )
    recent = math.log(current / six) / recent_years
    prior = math.log(six / twelve) / prior_years
    acceleration = (recent - prior) / ((recent_years + prior_years) / 2.0)
    output.update(
        {
            "recent_continuous_growth": recent,
            "prior_continuous_growth": prior,
            "annualized_recent_change": math.exp(recent) - 1.0,
            "annualized_prior_change": math.exp(prior) - 1.0,
            "log_growth_acceleration": acceleration,
            "recent_doubling_time_years": math.log(2.0) / recent if recent > 0 else None,
            "note": "Rates use log interpolation at six- and twelve-month anchors.",
        }
    )
    return output


def _bounded_path(baseline: float, annual_logit_change: float, horizon: np.ndarray) -> np.ndarray:
    if not 0 < baseline < 1:
        raise ValueError("bounded-path baseline must lie strictly between 0 and 1")
    odds_log = math.log(baseline / (1.0 - baseline)) + annual_logit_change * horizon
    return 1.0 / (1.0 + np.exp(-odds_log))


def _positive_paths(
    baseline: float,
    annual_growth: float,
    horizon: np.ndarray,
    count: int,
    rng: np.random.Generator,
    baseline_log_sd: float = 0.0,
    annual_growth_sd: float = 0.0,
) -> np.ndarray:
    if baseline <= 0 or baseline_log_sd < 0 or annual_growth_sd < 0:
        raise ValueError("positive-path baseline must be positive and uncertainty must be nonnegative")
    log_baseline = math.log(baseline) + rng.normal(0.0, baseline_log_sd, size=count)
    growth = annual_growth + rng.normal(0.0, annual_growth_sd, size=count)
    return np.exp(np.clip(log_baseline[:, None] + growth[:, None] * horizon[None, :], -700.0, 650.0))


def _bounded_paths(
    baseline: float,
    annual_logit_change: float,
    horizon: np.ndarray,
    count: int,
    rng: np.random.Generator,
    baseline_logit_sd: float = 0.0,
    annual_logit_change_sd: float = 0.0,
) -> np.ndarray:
    if not 0 < baseline < 1 or baseline_logit_sd < 0 or annual_logit_change_sd < 0:
        raise ValueError("bounded-path baseline must lie in (0,1) and uncertainty must be nonnegative")
    logit_baseline = math.log(baseline / (1.0 - baseline)) + rng.normal(0.0, baseline_logit_sd, size=count)
    change = annual_logit_change + rng.normal(0.0, annual_logit_change_sd, size=count)
    logits = np.clip(logit_baseline[:, None] + change[:, None] * horizon[None, :], -700.0, 700.0)
    return 1.0 / (1.0 + np.exp(-logits))


def _diagnostic_paths(values: np.ndarray) -> dict[str, list[float]]:
    matrix = np.asarray(values, dtype=float)
    return {
        "median": np.quantile(matrix, 0.5, axis=0).tolist(),
        "p10": np.quantile(matrix, 0.1, axis=0).tolist(),
        "p90": np.quantile(matrix, 0.9, axis=0).tolist(),
    }


def _apply_realization(
    samples: np.ndarray,
    horizon: np.ndarray,
    configuration: dict[str, Any],
    *,
    seed: int,
    scenario_parameters: dict[str, float] | None = None,
) -> tuple[np.ndarray, dict[str, dict[str, list[float]]]]:
    mode = configuration.get("mode", "reduced_form")
    if mode == "reduced_form":
        return samples, {}
    if mode != "technical_to_realized":
        raise ValueError(f"unknown canonical_model.mode {mode!r}")

    count = int(samples.shape[0])
    rng = np.random.default_rng(seed)
    uncertainty = configuration.get("uncertainty", {})
    shifts = scenario_parameters or {}
    demand = configuration["absorptive_demand"]
    market = _positive_paths(
        float(demand["market_baseline"]) * float(shifts.get("market_baseline_multiplier", 1.0)),
        float(demand.get("market_annual_growth", 0.0)) + float(shifts.get("market_annual_growth_shift", 0.0)),
        horizon,
        count,
        rng,
        float(uncertainty.get("market_baseline_log_sd", 0.0)),
        float(uncertainty.get("market_annual_growth_sd", 0.0)),
    )
    adoption = _bounded_paths(
        1.0
        / (
            1.0
            + math.exp(
                -(
                    math.log(float(demand["adoption_baseline"]) / (1.0 - float(demand["adoption_baseline"])))
                    + float(shifts.get("adoption_baseline_logit_shift", 0.0))
                )
            )
        ),
        float(demand.get("adoption_annual_logit_change", 0.0))
        + float(shifts.get("adoption_annual_logit_change_shift", 0.0)),
        horizon,
        count,
        rng,
        float(uncertainty.get("adoption_baseline_logit_sd", 0.0)),
        float(uncertainty.get("adoption_annual_logit_change_sd", 0.0)),
    )
    utilization = _positive_paths(
        float(demand.get("utilization_baseline", 1.0)) * float(shifts.get("utilization_baseline_multiplier", 1.0)),
        float(demand.get("utilization_annual_growth", 0.0)) + float(shifts.get("utilization_annual_growth_shift", 0.0)),
        horizon,
        count,
        rng,
        float(uncertainty.get("utilization_baseline_log_sd", 0.0)),
        float(uncertainty.get("utilization_annual_growth_sd", 0.0)),
    )
    constraints = configuration.get("branch_constraints", {})
    technical_bottleneck = _bounded_paths(
        1.0
        / (
            1.0
            + math.exp(
                -(
                    math.log(
                        float(constraints.get("technical_baseline", 0.999))
                        / (1.0 - float(constraints.get("technical_baseline", 0.999)))
                    )
                    + float(shifts.get("technical_baseline_logit_shift", 0.0))
                )
            )
        ),
        float(constraints.get("technical_annual_logit_change", 0.0))
        + float(shifts.get("technical_annual_logit_change_shift", 0.0)),
        horizon,
        count,
        rng,
        float(uncertainty.get("technical_baseline_logit_sd", 0.0)),
        float(uncertainty.get("technical_annual_logit_change_sd", 0.0)),
    )
    demand_bottleneck = _bounded_paths(
        1.0
        / (
            1.0
            + math.exp(
                -(
                    math.log(
                        float(constraints.get("demand_baseline", 0.999))
                        / (1.0 - float(constraints.get("demand_baseline", 0.999)))
                    )
                    + float(shifts.get("demand_baseline_logit_shift", 0.0))
                )
            )
        ),
        float(constraints.get("demand_annual_logit_change", 0.0))
        + float(shifts.get("demand_annual_logit_change_shift", 0.0)),
        horizon,
        count,
        rng,
        float(uncertainty.get("demand_baseline_logit_sd", 0.0)),
        float(uncertainty.get("demand_annual_logit_change_sd", 0.0)),
    )
    transfer_bottleneck = _bounded_paths(
        1.0
        / (
            1.0
            + math.exp(
                -(
                    math.log(
                        float(constraints.get("transfer_baseline", 0.999))
                        / (1.0 - float(constraints.get("transfer_baseline", 0.999)))
                    )
                    + float(shifts.get("transfer_baseline_logit_shift", 0.0))
                )
            )
        ),
        float(constraints.get("transfer_annual_logit_change", 0.0))
        + float(shifts.get("transfer_annual_logit_change_shift", 0.0)),
        horizon,
        count,
        rng,
        float(uncertainty.get("transfer_baseline_logit_sd", 0.0)),
        float(uncertainty.get("transfer_annual_logit_change_sd", 0.0)),
    )
    operator = configuration.get("operator", "hard_min")
    rho = math.inf if operator == "hard_min" else float(configuration.get("rho", 8.0))
    alpha = float(configuration.get("alpha", 0.5))
    absorptive_demand = market * adoption * utilization
    realized = generalized_realized_outcome(
        samples,
        absorptive_demand,
        technical_bottleneck,
        demand_bottleneck,
        transfer_bottleneck,
        alpha=alpha,
        rho=rho,
    )
    diagnostics = {
        "market": _diagnostic_paths(market),
        "adoption": _diagnostic_paths(adoption),
        "utilization": _diagnostic_paths(utilization),
        "absorptive_demand": _diagnostic_paths(absorptive_demand),
        "technical_bottleneck": _diagnostic_paths(technical_bottleneck),
        "demand_bottleneck": _diagnostic_paths(demand_bottleneck),
        "transfer_bottleneck": _diagnostic_paths(transfer_bottleneck),
    }
    return realized, diagnostics


def _points(dates: list[str], samples: np.ndarray, levels: tuple[float, ...]) -> list[dict[str, Any]]:
    median, mean, bands = summarize_samples(samples, levels)
    band_map = {f"p{int(round(band.level * 100))}": band for band in bands}
    output = []
    for index, stamp in enumerate(dates):
        intervals = {
            name: {"level": band.level, "lower": float(band.lower[index]), "upper": float(band.upper[index])}
            for name, band in band_map.items()
        }
        output.append(
            {
                "date": stamp,
                "median": float(median[index]),
                "mean": float(mean[index]),
                "intervals": intervals,
            }
        )
    return output


def _quality_score(evidence: list[dict[str, Any]]) -> float | None:
    grades = [
        grade
        for record in evidence
        if isinstance((grade := record.get("quality_grade")), str) and grade in _QUALITY_WEIGHTS
    ]
    if not grades:
        return None
    return float(np.mean([_QUALITY_WEIGHTS[grade] for grade in grades]))


def _model_payload(
    fits: dict[str, Any], time_future: np.ndarray, horizon_index: int
) -> tuple[list[dict[str, Any]], float | None]:
    rows = []
    endpoint_values = []
    for name, fit in fits.items():
        endpoint = None
        if fit.converged and fit.parameters:
            try:
                path = predict_model(name, time_future, fit.parameters)
                endpoint = float(path[horizon_index]) if np.isfinite(path[horizon_index]) else None
                if endpoint is not None and endpoint > 0:
                    endpoint_values.append(endpoint)
            except (ValueError, RuntimeError, FloatingPointError, OverflowError):
                endpoint = None
        rows.append(
            {
                "model": name,
                "converged": fit.converged,
                "parameters": fit.parameters,
                "n_observations": fit.n_observations,
                "n_parameters": fit.n_parameters,
                "log_likelihood": fit.log_likelihood if math.isfinite(fit.log_likelihood) else None,
                "aicc": fit.aicc if math.isfinite(fit.aicc) else None,
                "bic": fit.bic if math.isfinite(fit.bic) else None,
                "rmse_log": fit.rmse_log if math.isfinite(fit.rmse_log) else None,
                "mae_log": fit.mae_log if math.isfinite(fit.mae_log) else None,
                "horizon_prediction": endpoint,
                "message": fit.message,
            }
        )
    disagreement = None
    if len(endpoint_values) >= 2:
        values = np.asarray(endpoint_values)
        disagreement = float(np.std(np.log(values)))
    return rows, disagreement


def run_forecast(payload: dict[str, Any]) -> ForecastRun:
    cutoff = _parse_date(payload["research_cutoff"])
    target = payload["target"]
    horizon_end = _parse_date(target["horizon_end"])
    observations = [record for record in payload["observations"] if record.get("comparable", True)]
    if len(observations) < 6:
        raise ValueError("at least six comparable observations are required")
    observations.sort(key=lambda item: item["date"])
    obs_dates = pd.DatetimeIndex([_parse_date(item["date"]) for item in observations])
    obs_values = np.asarray([float(item["value"]) for item in observations], dtype=float)
    date_ns = obs_dates.to_numpy(dtype="datetime64[ns]").astype("int64")
    if np.any(obs_values <= 0) or np.any(np.diff(date_ns) <= 0):
        raise ValueError("comparable observations must have strictly increasing dates and positive values")
    if obs_dates.max() > cutoff:
        raise ValueError("observations may not occur after research_cutoff")

    modeling = payload.get("modeling", {})
    models = tuple(modeling.get("candidate_models", DEFAULT_MODELS))
    levels = tuple(float(level) for level in modeling.get("interval_levels", [0.5, 0.8, 0.95]))
    seed = int(modeling.get("random_seed", 20260728))
    n_samples = int(modeling.get("bootstrap_samples", 1000))
    frequency = str(modeling.get("forecast_frequency", "monthly"))

    origin = obs_dates[0]
    train_time = _year_values(obs_dates, origin)
    forecast_dates = _forecast_dates(cutoff, horizon_end, frequency)
    forecast_time = _year_values(forecast_dates, origin)
    horizon = _year_values(forecast_dates, cutoff)
    dates = [stamp.date().isoformat() for stamp in forecast_dates]

    base_ensemble = residual_bootstrap_model_average(
        train_time,
        obs_values,
        forecast_time,
        models=models,
        n_samples=n_samples,
        seed=seed,
        levels=levels,
        include_process_noise=bool(modeling.get("include_process_noise", True)),
    )
    fits = fit_all_models(train_time, obs_values, models)
    model_rows, disagreement = _model_payload(fits, forecast_time, -1)
    min_train = int(modeling.get("hindcast_min_train", max(5, min(10, len(obs_values) - 2))))
    hindcast = rolling_origin_hindcast(train_time, obs_values, min_train=min_train, horizon_steps=1, models=models)
    hindcast_summary = [
        {
            "model": name,
            "n": score["n"],
            "rmse_log": score["rmse_log"] if math.isfinite(score["rmse_log"]) else None,
            "mae_log": score["mae_log"] if math.isfinite(score["mae_log"]) else None,
            "smape": score["smape"] if math.isfinite(score["smape"]) else None,
        }
        for name, score in hindcast.items()
    ]

    scenarios = payload["scenarios"]
    probability_sum = sum(float(scenario["probability"]) for scenario in scenarios)
    if not math.isclose(probability_sum, 1.0, rel_tol=0.0, abs_tol=1e-6):
        raise ValueError(f"scenario probabilities must sum to 1; received {probability_sum}")

    scenario_outputs = []
    scenario_samples: dict[str, np.ndarray] = {}
    realization_diagnostics: dict[str, Any] = {}
    for index, scenario in enumerate(scenarios):
        scenario_id = str(scenario["id"])
        transformed = transform_scenario_samples(
            base_ensemble.samples,
            horizon,
            kind=str(scenario["kind"]),
            parameters=dict(scenario.get("parameters", {})),
            seed=seed + 1009 * (index + 1),
        )
        realized, diagnostics = _apply_realization(
            transformed,
            horizon,
            payload.get("canonical_model", {"mode": "reduced_form"}),
            seed=seed + 7919,
            scenario_parameters=dict(scenario.get("parameters", {})),
        )
        lower_bound = target.get("lower_bound")
        upper_bound = target.get("upper_bound")
        if lower_bound is not None:
            realized = np.maximum(realized, float(lower_bound))
        if upper_bound is not None:
            realized = np.minimum(realized, float(upper_bound))
        scenario_samples[scenario_id] = realized
        realization_diagnostics[scenario_id] = diagnostics
        scenario_outputs.append(
            {
                "id": scenario_id,
                "label": scenario["label"],
                "kind": scenario["kind"],
                "probability": float(scenario["probability"]),
                "assumptions": list(scenario.get("assumptions", [])),
                "parameters": dict(scenario.get("parameters", {})),
                "forecast_points": _points(dates, realized, levels),
                "horizon_summary": _points([dates[-1]], realized[:, [-1]], levels)[0],
                "invalidation_conditions": list(scenario.get("invalidation_conditions", [])),
            }
        )

    milestones = []
    for milestone in payload.get("milestones", []):
        scenario_results = {}
        for scenario in scenarios:
            scenario_results[scenario["id"]] = crossing_distribution(
                scenario_samples[scenario["id"]],
                dates,
                float(milestone["threshold"]),
                str(milestone.get("direction", "at_least")),
            )
        milestones.append({**milestone, "scenario_results": scenario_results})

    primary = next((item for item in scenario_outputs if item["kind"] == "base"), scenario_outputs[0])
    primary_width = None
    horizon_point = primary["horizon_summary"]
    p80 = horizon_point["intervals"].get("p80")
    if p80 and horizon_point["median"] > 0:
        primary_width = (p80["upper"] - p80["lower"]) / horizon_point["median"]

    evidence = list(payload.get("evidence", []))
    pace = _pace(obs_dates, obs_values, min(cutoff, obs_dates.max()))
    now = reproducible_utc_iso()
    output: dict[str, Any] = {
        "protocol_version": "2.0.0",
        "engine_version": _ENGINE_VERSION,
        "forecast_id": payload["forecast_id"],
        "generated_at": now,
        "research_cutoff": cutoff.isoformat(),
        "target": target,
        "executive_forecast": {
            "base_horizon_median": primary["horizon_summary"]["median"],
            "base_horizon_p80": primary["horizon_summary"]["intervals"].get("p80"),
            "decision_implication": payload.get(
                "decision_implication",
                "Use no-regret actions, preserve option value, and update at the dated recalculation gate.",
            ),
            "validation_status": "Probabilistic reference forecast; not a guarantee or assurance engagement.",
        },
        "observations": observations,
        "evidence": evidence,
        "current_pace": pace,
        "compact_canonical_model": {
            "equation": "Y_s(t)=B_s(t) min{Q_0 exp[int_0^t g_Q,s(u) du], M_s(t)D_s(t)U_s(t)}",
            "technical_growth_equation": "g_Q,s=beta_theta theta_dot-beta_c c_dot/c-beta_tau tau_dot/tau+beta_A A_dot/(A+epsilon)+beta_P P_dot/P+beta_R R_dot/R",
            "generalized_family": "Y=B_X[alpha(B_Q Q)^(-rho)+(1-alpha)(B_Z Z)^(-rho)]^(-1/rho); rho->infinity yields the hard minimum.",
            "configuration": payload.get("canonical_model", {"mode": "reduced_form"}),
            "diagnostics": realization_diagnostics,
            "plain_language": "Realized output is limited by technical capacity and absorptive demand, with branch-specific and transfer constraints applied exactly once.",
        },
        "model_fit": {
            "candidate_models": list(models),
            "fits": model_rows,
            "base_model_weights": base_ensemble.model_weights,
            "horizon_log_disagreement": disagreement,
            "rolling_origin_hindcast": hindcast_summary,
        },
        "forecast_dates": dates,
        "scenarios": scenario_outputs,
        "milestones": milestones,
        "bottlenecks": list(payload.get("bottlenecks", [])),
        "triggers": list(payload.get("triggers", [])),
        "optimal_plan": payload.get("optimal_plan", {}),
        "confidence": {
            "evidence_quality_score": _quality_score(evidence),
            "horizon_log_model_disagreement": disagreement,
            "base_horizon_p80_relative_width": primary_width,
            "limitations": list(payload.get("limitations", [])),
            "assumptions": list(payload.get("assumptions", [])),
        },
        "recalculation": payload["recalculation"],
        "reproducibility": {
            "input_sha256": _input_hash(payload),
            "random_seed": seed,
            "bootstrap_samples_requested": n_samples,
            "bootstrap_samples_successful": base_ensemble.successful_samples,
            "models": list(models),
            "code_version": _ENGINE_VERSION,
        },
        "legal_notice": "Research and decision-support output only. No warranty, assurance, legal, investment, tax, medical, or regulatory advice is provided.",
    }
    return ForecastRun(output=output, dates=dates, scenario_samples=scenario_samples)
