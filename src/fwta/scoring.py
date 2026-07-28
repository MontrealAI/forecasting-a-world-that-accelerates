from __future__ import annotations

import math

import numpy as np


def brier_score(probabilities: np.ndarray | list[float], outcomes: np.ndarray | list[float]) -> float:
    p = np.asarray(probabilities, dtype=float)
    o = np.asarray(outcomes, dtype=float)
    if p.shape != o.shape or p.size == 0 or np.any((p < 0) | (p > 1)) or np.any((o < 0) | (o > 1)):
        raise ValueError("probabilities and outcomes must have equal nonempty shapes and lie in [0,1]")
    return float(np.mean((p - o) ** 2))


def logarithmic_score(probabilities: np.ndarray | list[float], outcomes: np.ndarray | list[float], eps: float = 1e-12) -> float:
    p = np.asarray(probabilities, dtype=float)
    o = np.asarray(outcomes, dtype=float)
    if p.shape != o.shape or p.size == 0 or np.any((p < 0) | (p > 1)) or np.any((o < 0) | (o > 1)):
        raise ValueError("probabilities and outcomes must have equal nonempty shapes and lie in [0,1]")
    clipped = np.clip(p, eps, 1.0 - eps)
    return float(-np.mean(o * np.log(clipped) + (1.0 - o) * np.log(1.0 - clipped)))


def interval_score(lower: float, upper: float, observation: float, level: float) -> float:
    if not 0 < level < 1 or lower > upper:
        raise ValueError("level must lie in (0,1) and lower must not exceed upper")
    alpha = 1.0 - level
    score = upper - lower
    if observation < lower:
        score += (2.0 / alpha) * (lower - observation)
    elif observation > upper:
        score += (2.0 / alpha) * (observation - upper)
    return float(score)


def crps_ensemble(samples: np.ndarray | list[float], observation: float) -> float:
    x = np.asarray(samples, dtype=float)
    if x.ndim != 1 or x.size < 2 or not np.all(np.isfinite(x)) or not math.isfinite(observation):
        raise ValueError("samples must be a finite one-dimensional ensemble with at least two members")
    first = np.mean(np.abs(x - observation))
    second = 0.5 * np.mean(np.abs(x[:, None] - x[None, :]))
    return float(first - second)
