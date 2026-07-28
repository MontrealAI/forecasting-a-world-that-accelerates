from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from .metrics import akaike_weights
from .models import DEFAULT_MODELS, FitResult, fit_all_models, fit_model, predict_model


@dataclass(frozen=True)
class PredictiveSimulation:
    samples: np.ndarray
    fits: dict[str, FitResult]
    model_weights: dict[str, float]
    seed: int
    draws: int


def _validate_series(time: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    if t.ndim != 1 or y.ndim != 1 or t.size != y.size or t.size < 4:
        raise ValueError("time and values must be equal-length one-dimensional arrays with at least four points")
    if np.any(~np.isfinite(t)) or np.any(~np.isfinite(y)) or np.any(y <= 0) or np.any(np.diff(t) <= 0):
        raise ValueError("time must increase strictly and values must be finite and positive")
    return t, y


def predictive_samples(
    time: np.ndarray | list[float],
    values: np.ndarray | list[float],
    forecast_time: np.ndarray | list[float],
    *,
    models: tuple[str, ...] = DEFAULT_MODELS,
    draws: int = 500,
    seed: int = 20260728,
    include_observation_noise: bool = False,
    anchor_latest: bool = True,
) -> PredictiveSimulation:
    """Generate deterministic residual-bootstrap, model-averaged forecast samples.

    Each draw selects a model using AICc weights, resamples centered log residuals,
    refits the selected model, and forecasts the requested time grid. This captures
    model, parameter, and residual uncertainty without claiming a Bayesian posterior.
    """

    t, y = _validate_series(np.asarray(time), np.asarray(values))
    future = np.asarray(forecast_time, dtype=float)
    if future.ndim != 1 or future.size == 0 or np.any(~np.isfinite(future)) or np.any(np.diff(future) < 0):
        raise ValueError("forecast_time must be a finite, sorted one-dimensional array")
    if draws < 20:
        raise ValueError("draws must be at least 20")

    fits = fit_all_models(t, y, models)
    raw_weights = akaike_weights({name: fit.aicc for name, fit in fits.items()})
    valid = [name for name in models if fits[name].converged and fits[name].parameters and raw_weights.get(name, 0) > 0]
    if not valid:
        raise RuntimeError("no converged model is available for simulation")
    probabilities = np.asarray([raw_weights[name] for name in valid], dtype=float)
    probabilities /= probabilities.sum()
    weights = {name: (float(probabilities[valid.index(name)]) if name in valid else 0.0) for name in models}

    rng = np.random.default_rng(seed)
    output = np.empty((draws, future.size), dtype=float)
    for index in range(draws):
        model = str(rng.choice(valid, p=probabilities))
        reference_fit = fits[model]
        fitted = predict_model(model, t, reference_fit.parameters)
        residuals = np.log(y) - np.log(fitted)
        residuals -= residuals.mean()
        boot_residuals = rng.choice(residuals, size=residuals.size, replace=True)
        boot_values = fitted * np.exp(boot_residuals)
        try:
            boot_fit = fit_model(model, t, boot_values)
            if not boot_fit.converged or not boot_fit.parameters:
                raise RuntimeError("bootstrap fit did not converge")
        except (ValueError, RuntimeError, FloatingPointError, OverflowError):
            boot_fit = reference_fit
        path = predict_model(model, future, boot_fit.parameters)
        if anchor_latest:
            at_latest = float(predict_model(model, [t[-1]], boot_fit.parameters)[0])
            path = path * (y[-1] / max(at_latest, np.finfo(float).tiny))
        if include_observation_noise:
            sigma = max(float(np.std(residuals, ddof=1)), 1e-12)
            distance = np.maximum(future - t[-1], 0.0)
            scale = sigma * np.sqrt(1.0 + distance / max(t[-1] - t[0], 1e-9))
            path = path * np.exp(rng.normal(0.0, scale))
        output[index] = np.maximum(path, np.finfo(float).tiny)
    return PredictiveSimulation(output, fits, weights, seed, draws)


def quantile_points(samples: np.ndarray, labels: list[str] | tuple[str, ...] | None = None) -> list[dict[str, Any]]:
    values = np.asarray(samples, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or np.any(~np.isfinite(values)):
        raise ValueError("samples must be a finite two-dimensional array")
    if labels is not None and len(labels) != values.shape[1]:
        raise ValueError("labels must match the number of forecast columns")
    probabilities = np.array([0.025, 0.10, 0.25, 0.50, 0.75, 0.90, 0.975])
    quantiles = np.quantile(values, probabilities, axis=0)
    points: list[dict[str, Any]] = []
    for index in range(values.shape[1]):
        point: dict[str, Any] = {
            "p02_5": float(quantiles[0, index]),
            "p10": float(quantiles[1, index]),
            "p25": float(quantiles[2, index]),
            "median": float(quantiles[3, index]),
            "p75": float(quantiles[4, index]),
            "p90": float(quantiles[5, index]),
            "p97_5": float(quantiles[6, index]),
        }
        if labels is not None:
            point["date"] = labels[index]
        points.append(point)
    return points


def sample_crps(samples: np.ndarray | list[float], observation: float) -> float:
    values = np.sort(np.asarray(samples, dtype=float))
    if values.ndim != 1 or values.size < 2 or np.any(~np.isfinite(values)) or not math.isfinite(observation):
        raise ValueError("samples must be a finite one-dimensional array and observation finite")
    first = float(np.mean(np.abs(values - observation)))
    coefficients = 2.0 * np.arange(1, values.size + 1) - values.size - 1.0
    pairwise_half = float(np.sum(coefficients * values) / values.size**2)
    return first - pairwise_half


def weighted_interval_score(samples: np.ndarray | list[float], observation: float) -> float:
    values = np.asarray(samples, dtype=float)
    if values.ndim != 1 or values.size < 2 or np.any(~np.isfinite(values)) or not math.isfinite(observation):
        raise ValueError("samples must be finite and observation finite")
    median = float(np.quantile(values, 0.5))
    total = 0.5 * abs(observation - median)
    normalizer = 0.5
    for alpha in (0.5, 0.2, 0.05):
        lower, upper = np.quantile(values, [alpha / 2.0, 1.0 - alpha / 2.0])
        interval = float(upper - lower)
        penalty = (2.0 / alpha) * max(float(lower - observation), 0.0)
        penalty += (2.0 / alpha) * max(float(observation - upper), 0.0)
        weight = alpha / 2.0
        total += weight * (interval + penalty)
        normalizer += weight
    return float(total / normalizer)


def brier_score(probability: float, outcome: bool | int) -> float:
    if not 0 <= probability <= 1:
        raise ValueError("probability must be in [0,1]")
    observed = 1.0 if bool(outcome) else 0.0
    return float((probability - observed) ** 2)


def probabilistic_rolling_origin_hindcast(
    time: np.ndarray | list[float],
    values: np.ndarray | list[float],
    *,
    min_train: int = 7,
    horizon_steps: int = 1,
    models: tuple[str, ...] = DEFAULT_MODELS,
    draws: int = 120,
    seed: int = 20260728,
) -> dict[str, Any]:
    t, y = _validate_series(np.asarray(time), np.asarray(values))
    if min_train < 4 or min_train + horizon_steps > y.size:
        raise ValueError("invalid min_train or horizon_steps")
    records: list[dict[str, Any]] = []
    rng = np.random.default_rng(seed)
    for end in range(min_train, y.size - horizon_steps + 1):
        test_time = t[end : end + horizon_steps]
        simulation = predictive_samples(
            t[:end],
            y[:end],
            test_time,
            models=models,
            draws=draws,
            seed=int(rng.integers(0, np.iinfo(np.int32).max)),
            include_observation_noise=True,
        )
        for step, actual in enumerate(y[end : end + horizon_steps]):
            samples = simulation.samples[:, step]
            lower80, upper80 = np.quantile(samples, [0.10, 0.90])
            lower95, upper95 = np.quantile(samples, [0.025, 0.975])
            records.append(
                {
                    "time": float(test_time[step]),
                    "actual": float(actual),
                    "median": float(np.quantile(samples, 0.5)),
                    "lower80": float(lower80),
                    "upper80": float(upper80),
                    "lower95": float(lower95),
                    "upper95": float(upper95),
                    "crps": sample_crps(samples, float(actual)),
                    "wis": weighted_interval_score(samples, float(actual)),
                    "covered80": bool(lower80 <= actual <= upper80),
                    "covered95": bool(lower95 <= actual <= upper95),
                }
            )
    if not records:
        raise RuntimeError("hindcast produced no records")
    actual = np.asarray([row["actual"] for row in records], dtype=float)
    median = np.asarray([row["median"] for row in records], dtype=float)
    return {
        "n": len(records),
        "rmse_log": float(np.sqrt(np.mean((np.log(actual) - np.log(median)) ** 2))),
        "mae_log": float(np.mean(np.abs(np.log(actual) - np.log(median)))),
        "mean_crps": float(np.mean([row["crps"] for row in records])),
        "mean_wis": float(np.mean([row["wis"] for row in records])),
        "coverage80": float(np.mean([row["covered80"] for row in records])),
        "coverage95": float(np.mean([row["covered95"] for row in records])),
        "records": records,
        "draws_per_origin": draws,
        "seed": seed,
    }
