from __future__ import annotations

import math
from collections.abc import Callable, Iterable

import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_ivp


def exponential_path(time: Iterable[float], x0: float, growth: float) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    if x0 <= 0 or not np.all(np.isfinite(t)):
        raise ValueError("x0 must be positive and time finite")
    return x0 * np.exp(growth * t)


def accelerated_exponential(time: Iterable[float], x0: float, g0: float, acceleration: float) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    if x0 <= 0 or not np.all(np.isfinite(t)):
        raise ValueError("x0 must be positive and time finite")
    return x0 * np.exp(g0 * t + 0.5 * acceleration * t**2)


def decaying_acceleration_path(time: Iterable[float], x0: float, g0: float, a0: float, kappa: float) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    if x0 <= 0 or kappa <= 0:
        raise ValueError("x0 and kappa must be positive")
    exponent = g0 * t + (a0 / kappa) * t - (a0 / kappa**2) * (1.0 - np.exp(-kappa * t))
    return x0 * np.exp(exponent)


def logistic_path(time: Iterable[float], x0: float, growth: float, capacity: float) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    if not 0 < x0 < capacity or growth <= 0:
        raise ValueError("require 0 < x0 < capacity and positive growth")
    return capacity / (1.0 + (capacity / x0 - 1.0) * np.exp(-growth * t))


def double_exponential(
    time: Iterable[float],
    x_transition: float,
    transition_time: float,
    jump: float,
    growth_at_transition: float,
    growth_compounding: float,
) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    if x_transition <= 0 or jump <= 0 or growth_compounding <= 0:
        raise ValueError("x_transition, jump, and growth_compounding must be positive")
    elapsed = np.maximum(t - transition_time, 0.0)
    exponent = (growth_at_transition / growth_compounding) * (np.exp(growth_compounding * elapsed) - 1.0)
    post = jump * x_transition * np.exp(exponent)
    return np.where(t < transition_time, np.nan, post)


def constrained_growth(
    time: Iterable[float],
    x0: float,
    growth_rate: Callable[[float], float],
    bottleneck: Callable[[float], float],
    capacity: Callable[[float], float],
    nu: float = 1.0,
) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    if t.ndim != 1 or t.size < 2 or np.any(np.diff(t) < 0):
        raise ValueError("time must be a sorted one-dimensional array with at least two points")
    if x0 <= 0 or nu <= 0:
        raise ValueError("x0 and nu must be positive")

    def rhs(current_t: float, y: np.ndarray) -> np.ndarray:
        k = float(capacity(current_t))
        b = float(bottleneck(current_t))
        if k <= 0 or not 0 < b <= 1:
            raise ValueError("capacity must be positive and bottleneck in (0,1]")
        saturation = max(0.0, 1.0 - (max(y[0], 0.0) / k) ** nu)
        return np.array([float(growth_rate(current_t)) * y[0] * b * saturation])

    sol = solve_ivp(rhs, (float(t[0]), float(t[-1])), np.array([x0]), t_eval=t, rtol=1e-9, atol=1e-11)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y[0]


def cumulative_transition_probability(time: Iterable[float], hazard: Iterable[float]) -> np.ndarray:
    t = np.asarray(time, dtype=float)
    lam = np.asarray(hazard, dtype=float)
    if t.ndim != 1 or lam.ndim != 1 or t.size != lam.size or np.any(lam < 0):
        raise ValueError("time and hazard must be equal-length one-dimensional arrays; hazard nonnegative")
    cumulative = cumulative_trapezoid(lam, t, initial=0.0)
    return 1.0 - np.exp(-cumulative)


def milestone_time(time: Iterable[float], values: Iterable[float], threshold: float) -> float:
    t = np.asarray(time, dtype=float)
    x = np.asarray(values, dtype=float)
    if t.ndim != 1 or x.ndim != 1 or t.size != x.size or threshold <= 0:
        raise ValueError("invalid milestone inputs")
    indices = np.flatnonzero(x >= threshold)
    if indices.size == 0:
        return math.inf
    index = int(indices[0])
    if index == 0:
        return float(t[0])
    t0, t1 = t[index - 1], t[index]
    x0, x1 = x[index - 1], x[index]
    if x1 == x0:
        return float(t1)
    return float(t0 + (threshold - x0) * (t1 - t0) / (x1 - x0))
