from __future__ import annotations

import math
from collections.abc import Iterable, Mapping

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.special import logsumexp


def _array(values: Iterable[float] | float, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def technical_growth_rate(
    theta_dot: Iterable[float] | float,
    cost: Iterable[float] | float,
    cost_dot: Iterable[float] | float,
    duration: Iterable[float] | float,
    duration_dot: Iterable[float] | float,
    automation: Iterable[float] | float,
    automation_dot: Iterable[float] | float,
    parallelism: Iterable[float] | float,
    parallelism_dot: Iterable[float] | float,
    reliability: Iterable[float] | float,
    reliability_dot: Iterable[float] | float,
    elasticities: Mapping[str, float],
    eps: float = 1e-9,
) -> np.ndarray:
    required = {"theta", "cost", "duration", "automation", "parallelism", "reliability"}
    missing = required.difference(elasticities)
    if missing:
        raise ValueError(f"missing elasticities: {sorted(missing)}")
    if eps <= 0:
        raise ValueError("eps must be positive")
    c = _array(cost, "cost")
    tau = _array(duration, "duration")
    a = _array(automation, "automation")
    p = _array(parallelism, "parallelism")
    r = _array(reliability, "reliability")
    if np.any(c <= 0) or np.any(tau <= 0) or np.any(p <= 0) or np.any(r <= 0):
        raise ValueError("cost, duration, parallelism, and reliability must be positive")
    return (
        float(elasticities["theta"]) * _array(theta_dot, "theta_dot")
        - float(elasticities["cost"]) * _array(cost_dot, "cost_dot") / c
        - float(elasticities["duration"]) * _array(duration_dot, "duration_dot") / tau
        + float(elasticities["automation"]) * _array(automation_dot, "automation_dot") / (a + eps)
        + float(elasticities["parallelism"]) * _array(parallelism_dot, "parallelism_dot") / p
        + float(elasticities["reliability"]) * _array(reliability_dot, "reliability_dot") / r
    )


def technical_capacity(time: Iterable[float], q0: float, growth_rate: Iterable[float]) -> np.ndarray:
    t = _array(time, "time")
    g = _array(growth_rate, "growth_rate")
    if t.ndim != 1 or g.ndim != 1 or t.size != g.size:
        raise ValueError("time and growth_rate must be equal-length one-dimensional arrays")
    if q0 <= 0 or np.any(np.diff(t) < 0):
        raise ValueError("q0 must be positive and time must be nondecreasing")
    integral = cumulative_trapezoid(g, t, initial=0.0)
    return q0 * np.exp(integral)


def generalized_bottleneck(
    factors: Iterable[float] | np.ndarray,
    weights: Iterable[float] | np.ndarray | None = None,
    rho: float = 8.0,
    axis: int = -1,
) -> np.ndarray:
    values = _array(factors, "factors")
    if np.any(values <= 0) or np.any(values > 1):
        raise ValueError("bottleneck factors must be in (0, 1]")
    if rho <= 0:
        raise ValueError("rho must be positive")
    count = values.shape[axis]
    if weights is None:
        w = np.full(count, 1.0 / count)
    else:
        w = _array(weights, "weights")
        if w.ndim != 1 or w.size != count or np.any(w < 0) or not np.isclose(w.sum(), 1.0):
            raise ValueError("weights must be nonnegative, sum to 1, and match the selected axis")
    shape = [1] * values.ndim
    shape[axis] = count
    weighted = np.sum(w.reshape(shape) * values ** (-rho), axis=axis)
    return weighted ** (-1.0 / rho)


def generalized_realized_outcome(
    technical: Iterable[float] | float,
    demand: Iterable[float] | float,
    technical_bottleneck: Iterable[float] | float = 1.0,
    demand_bottleneck: Iterable[float] | float = 1.0,
    realization_bottleneck: Iterable[float] | float = 1.0,
    *,
    alpha: float = 0.5,
    rho: float = math.inf,
) -> np.ndarray:
    """Combine capacity and absorptive demand with branch-specific constraints.

    With ``rho=inf`` this is the compact canonical hard-min model. For finite
    positive ``rho`` it is a constant-elasticity soft minimum. The finite-rho
    family is useful for sensitivity analysis where partial substitution is
    plausible; it converges to the hard minimum as ``rho`` grows.
    """

    q = _array(technical, "technical")
    z = _array(demand, "demand")
    bq = _array(technical_bottleneck, "technical_bottleneck")
    bz = _array(demand_bottleneck, "demand_bottleneck")
    bx = _array(realization_bottleneck, "realization_bottleneck")
    if np.any(q < 0) or np.any(z < 0):
        raise ValueError("technical and demand values must be nonnegative")
    for name, values in (("technical_bottleneck", bq), ("demand_bottleneck", bz), ("realization_bottleneck", bx)):
        if np.any(values <= 0) or np.any(values > 1):
            raise ValueError(f"{name} must be in (0, 1]")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0,1)")
    if not math.isinf(rho) and rho <= 0:
        raise ValueError("rho must be positive or infinity")

    effective_q, effective_z, effective_bx = np.broadcast_arrays(bq * q, bz * z, bx)
    if math.isinf(rho):
        aggregate = np.minimum(effective_q, effective_z)
    else:
        aggregate = np.zeros_like(effective_q, dtype=float)
        positive = (effective_q > 0) & (effective_z > 0)
        logs = np.stack(
            [
                math.log(alpha) - rho * np.log(np.maximum(effective_q[positive], np.finfo(float).tiny)),
                math.log(1.0 - alpha) - rho * np.log(np.maximum(effective_z[positive], np.finfo(float).tiny)),
            ],
            axis=0,
        )
        aggregate[positive] = np.exp(-logsumexp(logs, axis=0) / rho)
    return effective_bx * aggregate


def realized_outcome(
    technical: Iterable[float] | float,
    market: Iterable[float] | float,
    adoption: Iterable[float] | float,
    utilization: Iterable[float] | float,
    bottleneck: Iterable[float] | float,
) -> np.ndarray:
    q = _array(technical, "technical")
    m = _array(market, "market")
    d = _array(adoption, "adoption")
    u = _array(utilization, "utilization")
    b = _array(bottleneck, "bottleneck")
    if np.any(q < 0) or np.any(m < 0) or np.any(u < 0):
        raise ValueError("technical, market, and utilization values must be nonnegative")
    if np.any(d < 0) or np.any(d > 1) or np.any(b <= 0) or np.any(b > 1):
        raise ValueError("adoption must be in [0,1] and bottleneck in (0,1]")
    return generalized_realized_outcome(q, m * d * u, realization_bottleneck=b, rho=math.inf)


def double_counting_audit(assignments: Mapping[str, str]) -> list[str]:
    allowed = {"technical", "demand", "bottleneck", "diagnostic"}
    errors: list[str] = []
    seen: dict[str, str] = {}
    for factor, branch in assignments.items():
        branches = [item.strip() for item in branch.split(",") if item.strip()]
        invalid = [item for item in branches if item not in allowed]
        if invalid:
            errors.append(f"{factor}: invalid branches {invalid}")
        substantive = [item for item in branches if item != "diagnostic"]
        if len(set(substantive)) > 1:
            errors.append(f"{factor}: counted in multiple substantive branches {sorted(set(substantive))}")
        if factor in seen and seen[factor] != branch:
            errors.append(f"{factor}: duplicate inconsistent assignment")
        seen[factor] = branch
    return errors

