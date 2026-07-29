from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from scipy.optimize import least_squares

from .canonical import realized_outcome
from .metrics import rmse


def _matrix(features: dict[str, Iterable[float]], selected: tuple[str, ...]) -> np.ndarray:
    columns = [np.asarray(features[name], dtype=float) for name in selected]
    if not columns:
        return np.empty((len(next(iter(features.values()))), 0), dtype=float)
    matrix = np.column_stack(columns)
    if not np.all(np.isfinite(matrix)):
        raise ValueError("features contain non-finite values")
    return matrix


def fit_canonical_elasticities(
    target: Iterable[float],
    features: dict[str, Iterable[float]],
    market: Iterable[float],
    adoption: Iterable[float],
    utilization: Iterable[float],
    bottleneck: Iterable[float],
    selected: tuple[str, ...],
) -> dict[str, object]:
    y = np.asarray(target, dtype=float)
    x = _matrix(features, selected)
    m = np.asarray(market, dtype=float)
    d = np.asarray(adoption, dtype=float)
    u = np.asarray(utilization, dtype=float)
    b = np.asarray(bottleneck, dtype=float)
    if any(arr.shape != y.shape for arr in (m, d, u, b)) or np.any(y <= 0):
        raise ValueError("all series must share shape and target must be positive")

    def residual(parameters: np.ndarray) -> np.ndarray:
        log_q0 = parameters[0]
        betas = parameters[1:]
        technical = np.exp(log_q0 + (x @ betas if x.shape[1] else 0.0))
        predicted = realized_outcome(technical, m, d, u, b)
        return np.log(np.maximum(predicted, 1e-300)) - np.log(y)

    initial = np.zeros(1 + x.shape[1], dtype=float)
    initial[0] = np.log(max(float(y[0] / max(b[0], 1e-9)), 1e-9))
    lower = np.concatenate(([-50.0], np.full(x.shape[1], -5.0)))
    upper = np.concatenate(([50.0], np.full(x.shape[1], 5.0)))
    fit = least_squares(residual, initial, bounds=(lower, upper), loss="linear", max_nfev=50000)
    predictions = y * np.exp(residual(fit.x))
    return {
        "selected": list(selected),
        "converged": bool(fit.success),
        "log_q0": float(fit.x[0]),
        "elasticities": {name: float(value) for name, value in zip(selected, fit.x[1:], strict=True)},
        "rmse_log": rmse(np.log(y), np.log(np.maximum(predictions, 1e-300))),
        "predictions": predictions.tolist(),
    }


def canonical_ablation_suite(
    target: Iterable[float],
    features: dict[str, Iterable[float]],
    market: Iterable[float],
    adoption: Iterable[float],
    utilization: Iterable[float],
    bottleneck: Iterable[float],
) -> dict[str, dict[str, object]]:
    names = tuple(features)
    specifications = {"full": names, "intercept_only": ()}
    specifications.update({f"without_{name}": tuple(item for item in names if item != name) for name in names})
    return {
        label: fit_canonical_elasticities(target, features, market, adoption, utilization, bottleneck, selected)
        for label, selected in specifications.items()
    }
