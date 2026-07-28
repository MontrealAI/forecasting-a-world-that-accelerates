from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np


def _as_1d(values: Iterable[float] | np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional array")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def log_growth_rate(x_now: float, x_past: float, years: float) -> float:
    if x_now <= 0 or x_past <= 0:
        raise ValueError("growth-rate inputs must be positive")
    if years <= 0:
        raise ValueError("years must be positive")
    return math.log(x_now / x_past) / years


def acceleration(x_now: float, x_mid: float, x_past: float, window_years: float) -> float:
    recent = log_growth_rate(x_now, x_mid, window_years)
    prior = log_growth_rate(x_mid, x_past, window_years)
    return (recent - prior) / window_years


def annual_improvement(growth_rate: float) -> float:
    return math.expm1(growth_rate)


def doubling_time(growth_rate: float) -> float:
    if growth_rate <= 0:
        return math.inf
    return math.log(2.0) / growth_rate


def logit(value: float, eps: float = 1e-12) -> float:
    if eps <= 0 or eps >= 0.5:
        raise ValueError("eps must be in (0, 0.5)")
    clipped = min(max(float(value), eps), 1.0 - eps)
    return math.log(clipped / (1.0 - clipped))


def rmse(actual: Iterable[float], predicted: Iterable[float]) -> float:
    y = _as_1d(actual, "actual")
    p = _as_1d(predicted, "predicted")
    if y.shape != p.shape:
        raise ValueError("actual and predicted must have equal shape")
    return float(np.sqrt(np.mean((y - p) ** 2)))


def mae(actual: Iterable[float], predicted: Iterable[float]) -> float:
    y = _as_1d(actual, "actual")
    p = _as_1d(predicted, "predicted")
    if y.shape != p.shape:
        raise ValueError("actual and predicted must have equal shape")
    return float(np.mean(np.abs(y - p)))


def mape(actual: Iterable[float], predicted: Iterable[float], eps: float = 1e-12) -> float:
    y = _as_1d(actual, "actual")
    p = _as_1d(predicted, "predicted")
    if y.shape != p.shape:
        raise ValueError("actual and predicted must have equal shape")
    denom = np.maximum(np.abs(y), eps)
    return float(np.mean(np.abs((y - p) / denom)))


def smape(actual: Iterable[float], predicted: Iterable[float], eps: float = 1e-12) -> float:
    y = _as_1d(actual, "actual")
    p = _as_1d(predicted, "predicted")
    if y.shape != p.shape:
        raise ValueError("actual and predicted must have equal shape")
    denom = np.maximum(np.abs(y) + np.abs(p), eps)
    return float(np.mean(2.0 * np.abs(y - p) / denom))


def gaussian_log_likelihood(residuals: Iterable[float], sigma: float | None = None) -> float:
    r = _as_1d(residuals, "residuals")
    if sigma is None:
        sigma = float(np.sqrt(np.mean(r**2)))
    sigma = max(float(sigma), np.finfo(float).eps)
    return float(-0.5 * r.size * (math.log(2.0 * math.pi * sigma**2) + 1.0))


def aicc(log_likelihood: float, n: int, k: int) -> float:
    if n <= 0 or k <= 0:
        raise ValueError("n and k must be positive")
    base = 2.0 * k - 2.0 * float(log_likelihood)
    if n <= k + 1:
        return math.inf
    return base + (2.0 * k * (k + 1)) / (n - k - 1)


def bic(log_likelihood: float, n: int, k: int) -> float:
    if n <= 0 or k <= 0:
        raise ValueError("n and k must be positive")
    return k * math.log(n) - 2.0 * float(log_likelihood)


def akaike_weights(aicc_values: dict[str, float]) -> dict[str, float]:
    finite = {name: value for name, value in aicc_values.items() if math.isfinite(value)}
    if not finite:
        return {name: 0.0 for name in aicc_values}
    minimum = min(finite.values())
    raw = {name: math.exp(-0.5 * (value - minimum)) for name, value in finite.items()}
    total = sum(raw.values())
    weights = {name: raw.get(name, 0.0) / total for name in aicc_values}
    return weights
