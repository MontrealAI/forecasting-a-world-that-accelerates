from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from .metrics import akaike_weights
from .models import DEFAULT_MODELS, FitResult, fit_all_models, fit_model, predict_model


@dataclass(frozen=True)
class ForecastBand:
    level: float
    lower: np.ndarray
    upper: np.ndarray


@dataclass(frozen=True)
class EnsembleForecast:
    median: np.ndarray
    mean: np.ndarray
    bands: tuple[ForecastBand, ...]
    samples: np.ndarray
    model_weights: dict[str, float]
    successful_samples: int
    requested_samples: int


def _validate_levels(levels: tuple[float, ...] | list[float]) -> tuple[float, ...]:
    clean = tuple(sorted({float(level) for level in levels}))
    if not clean or any(level <= 0 or level >= 1 for level in clean):
        raise ValueError("interval levels must lie strictly between 0 and 1")
    return clean


def summarize_samples(
    samples: np.ndarray, levels: tuple[float, ...] | list[float]
) -> tuple[np.ndarray, np.ndarray, tuple[ForecastBand, ...]]:
    values = np.asarray(samples, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 1:
        raise ValueError("samples must be a two-dimensional array with at least two rows")
    if not np.all(np.isfinite(values)) or np.any(values < 0):
        raise ValueError("samples must contain finite nonnegative values")
    clean = _validate_levels(levels)
    median = np.quantile(values, 0.5, axis=0)
    mean = np.mean(values, axis=0)
    bands = []
    for level in clean:
        alpha = (1.0 - level) / 2.0
        bands.append(
            ForecastBand(
                level=level,
                lower=np.quantile(values, alpha, axis=0),
                upper=np.quantile(values, 1.0 - alpha, axis=0),
            )
        )
    return median, mean, tuple(bands)


def _valid_fits(fits: dict[str, FitResult]) -> tuple[list[str], np.ndarray]:
    scores = {
        name: fit.aicc for name, fit in fits.items() if fit.converged and fit.parameters and math.isfinite(fit.aicc)
    }
    if not scores:
        raise RuntimeError("no converged finite-AICc models are available")
    weight_map = akaike_weights(scores)
    names = list(weight_map)
    weights = np.asarray([weight_map[name] for name in names], dtype=float)
    weights /= weights.sum()
    return names, weights


def residual_bootstrap_model_average(
    time: np.ndarray | list[float],
    values: np.ndarray | list[float],
    forecast_time: np.ndarray | list[float],
    *,
    models: tuple[str, ...] = DEFAULT_MODELS,
    n_samples: int = 1000,
    seed: int = 20260728,
    levels: tuple[float, ...] = (0.5, 0.8, 0.95),
    include_process_noise: bool = True,
    maximum_log_value: float = 650.0,
) -> EnsembleForecast:
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    future = np.asarray(forecast_time, dtype=float)
    if t.ndim != 1 or y.ndim != 1 or t.size != y.size or t.size < 4:
        raise ValueError("time and values must be equal-length one-dimensional arrays with at least four observations")
    if future.ndim != 1 or future.size < 1 or np.any(np.diff(future) < 0):
        raise ValueError("forecast_time must be a nondecreasing one-dimensional array")
    if np.any(y <= 0) or not np.all(np.isfinite(y)) or not np.all(np.isfinite(t)):
        raise ValueError("observed values must be finite and strictly positive")
    if n_samples < 50:
        raise ValueError("n_samples must be at least 50")

    fits = fit_all_models(t, y, models)
    names, weights = _valid_fits(fits)
    rng = np.random.default_rng(seed)
    generated: list[np.ndarray] = []

    residuals_by_model: dict[str, np.ndarray] = {}
    for name in names:
        fit = fits[name]
        fitted = np.maximum(predict_model(name, t, fit.parameters), 1e-300)
        residuals = np.log(y) - np.log(fitted)
        residuals_by_model[name] = residuals - np.mean(residuals)

    attempts = 0
    maximum_attempts = max(n_samples * 4, n_samples + 100)
    while len(generated) < n_samples and attempts < maximum_attempts:
        attempts += 1
        name = str(rng.choice(names, p=weights))
        original = fits[name]
        fitted = np.maximum(predict_model(name, t, original.parameters), 1e-300)
        residuals = residuals_by_model[name]
        resampled = rng.choice(residuals, size=t.size, replace=True)
        boot_y = np.exp(np.clip(np.log(fitted) + resampled, -700.0, maximum_log_value))
        try:
            refit = fit_model(name, t, boot_y)
            params = refit.parameters if refit.converged and refit.parameters else original.parameters
            path = np.maximum(predict_model(name, future, params), 0.0)
        except (ValueError, RuntimeError, FloatingPointError, OverflowError):
            continue
        if include_process_noise and residuals.size:
            path = path * np.exp(rng.choice(residuals, size=future.size, replace=True))
        path = np.exp(np.clip(np.log(np.maximum(path, 1e-300)), -700.0, maximum_log_value))
        if np.all(np.isfinite(path)):
            generated.append(path)

    if len(generated) < max(50, n_samples // 2):
        raise RuntimeError(f"only {len(generated)} of {n_samples} requested bootstrap samples converged")

    matrix = np.vstack(generated[:n_samples])
    median, mean, bands = summarize_samples(matrix, levels)
    return EnsembleForecast(
        median=median,
        mean=mean,
        bands=bands,
        samples=matrix,
        model_weights={name: float(weight) for name, weight in zip(names, weights, strict=True)},
        successful_samples=int(matrix.shape[0]),
        requested_samples=n_samples,
    )


def transform_scenario_samples(
    base_samples: np.ndarray,
    horizon_years: np.ndarray | list[float],
    *,
    kind: str,
    parameters: dict[str, float] | None = None,
    seed: int = 20260728,
    maximum_extra_log: float = 30.0,
) -> np.ndarray:
    samples = np.asarray(base_samples, dtype=float)
    horizon = np.asarray(horizon_years, dtype=float)
    if samples.ndim != 2 or horizon.ndim != 1 or samples.shape[1] != horizon.size:
        raise ValueError("base_samples and horizon_years have incompatible dimensions")
    if np.any(samples <= 0) or np.any(horizon < 0) or np.any(np.diff(horizon) < 0):
        raise ValueError("samples must be positive and horizon_years nonnegative and nondecreasing")
    params = parameters or {}
    if kind == "base":
        return samples.copy()

    if kind == "accelerated":
        growth_shift = float(params.get("annual_growth_shift", 0.08))
        acceleration_shift = float(params.get("annual_acceleration_shift", 0.05))
        extra_log = growth_shift * horizon + 0.5 * acceleration_shift * horizon**2
        return samples * np.exp(np.clip(extra_log, -maximum_extra_log, maximum_extra_log))[None, :]

    if kind == "downside":
        annual_drag = float(params.get("annual_drag", 0.12))
        shock = float(params.get("immediate_multiplier", 0.95))
        floor_multiplier = float(params.get("floor_multiplier", 0.05))
        multiplier = np.maximum(floor_multiplier, shock * np.exp(-annual_drag * horizon))
        return samples * multiplier[None, :]

    if kind == "discontinuous":
        hazard = float(params.get("annual_transition_hazard", 0.25))
        jump = float(params.get("jump_multiplier", 1.20))
        q = float(params.get("growth_rate_compounding", 0.45))
        growth_bonus = float(params.get("initial_growth_bonus", 0.18))
        if hazard < 0 or jump <= 0 or q < 0:
            raise ValueError("discontinuity parameters must satisfy hazard>=0, jump>0, and q>=0")
        rng = np.random.default_rng(seed)
        output = samples.copy()
        for row in range(samples.shape[0]):
            tau = math.inf if hazard == 0 else float(rng.exponential(1.0 / hazard))
            active = horizon >= tau
            if not np.any(active):
                continue
            elapsed = horizon[active] - tau
            if q > 1e-12:
                recursive_log = (growth_bonus / q) * (np.exp(np.minimum(q * elapsed, 20.0)) - 1.0)
            else:
                recursive_log = growth_bonus * elapsed
            extra_log = math.log(jump) + np.minimum(recursive_log, maximum_extra_log)
            output[row, active] *= np.exp(extra_log)
        return output

    raise ValueError(f"unknown scenario kind {kind!r}")


def interval_payload(forecast: EnsembleForecast) -> dict[str, Any]:
    return {
        "median": forecast.median.tolist(),
        "mean": forecast.mean.tolist(),
        "intervals": {
            f"p{int(round(band.level * 100))}": {
                "level": band.level,
                "lower": band.lower.tolist(),
                "upper": band.upper.tolist(),
            }
            for band in forecast.bands
        },
        "model_weights": forecast.model_weights,
        "successful_samples": forecast.successful_samples,
        "requested_samples": forecast.requested_samples,
    }


def crossing_distribution(
    samples: np.ndarray, dates: list[str], threshold: float, direction: str = "at_least"
) -> dict[str, Any]:
    values = np.asarray(samples, dtype=float)
    if values.ndim != 2 or values.shape[1] != len(dates):
        raise ValueError("samples and dates have incompatible dimensions")
    if not math.isfinite(threshold):
        raise ValueError("threshold must be finite")
    crossings: list[int] = []
    for row in values:
        mask = row >= threshold if direction == "at_least" else row <= threshold
        indices = np.flatnonzero(mask)
        crossings.append(int(indices[0]) if indices.size else -1)
    crossed = np.asarray([index >= 0 for index in crossings], dtype=bool)
    probability = float(np.mean(crossed))
    if not np.any(crossed):
        return {
            "probability_by_horizon": probability,
            "median_crossing_date": None,
            "p10_crossing_date": None,
            "p90_crossing_date": None,
        }
    valid = np.asarray([index for index in crossings if index >= 0], dtype=int)
    return {
        "probability_by_horizon": probability,
        "median_crossing_date": dates[int(np.quantile(valid, 0.5, method="nearest"))],
        "p10_crossing_date": dates[int(np.quantile(valid, 0.1, method="nearest"))],
        "p90_crossing_date": dates[int(np.quantile(valid, 0.9, method="nearest"))],
    }
