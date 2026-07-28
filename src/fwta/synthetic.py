from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .canonical import generalized_bottleneck, realized_outcome, technical_capacity, technical_growth_rate


@dataclass(frozen=True)
class SyntheticSeries:
    frame: pd.DataFrame
    description: str


def regime_shift_series(seed: int = 20260728, periods: int = 48) -> SyntheticSeries:
    if periods < 16:
        raise ValueError("periods must be at least 16")
    rng = np.random.default_rng(seed)
    time = np.arange(periods, dtype=float) / 12.0
    transition = 2.0
    growth_pre = 0.45
    growth_post = 1.25
    log_signal = np.log(10.0) + growth_pre * time + (growth_post - growth_pre) * np.maximum(time - transition, 0.0)
    observed = np.exp(log_signal + rng.normal(0.0, 0.075, size=periods))
    return SyntheticSeries(
        pd.DataFrame({"time_years": time, "value": observed, "truth": np.exp(log_signal)}),
        "Synthetic continuous log-linear change point with fixed seed and known transition.",
    )


def canonical_system_series(seed: int = 20260728, periods: int = 37) -> SyntheticSeries:
    if periods < 13:
        raise ValueError("periods must be at least 13")
    rng = np.random.default_rng(seed)
    t = np.arange(periods, dtype=float) / 12.0
    theta = 0.18 * t + 0.035 * t**2
    cost = 1.0 * np.exp(-0.38 * t)
    duration = 1.0 * np.exp(-0.29 * t)
    automation = 0.18 + 0.58 / (1.0 + np.exp(-1.3 * (t - 1.5)))
    parallelism = np.exp(0.23 * t)
    reliability = 0.62 + 0.32 / (1.0 + np.exp(-1.1 * (t - 1.3)))
    gradients = [np.gradient(x, t, edge_order=2) for x in (theta, cost, duration, automation, parallelism, reliability)]
    elasticities = {"theta": 1.0, "cost": 0.34, "duration": 0.42, "automation": 0.25, "parallelism": 0.18, "reliability": 0.50}
    gq = technical_growth_rate(
        gradients[0], cost, gradients[1], duration, gradients[2], automation, gradients[3],
        parallelism, gradients[4], reliability, gradients[5], elasticities,
    )
    technical = technical_capacity(t, 12.0, gq)
    market = 80.0 * np.exp(0.13 * t)
    adoption = 0.12 + 0.77 / (1.0 + np.exp(-1.05 * (t - 1.8)))
    utilization = 0.8 + 0.18 * t
    factors = np.column_stack([
        0.72 + 0.16 * (1.0 - np.exp(-0.6 * t)),
        0.66 + 0.24 * (1.0 - np.exp(-0.45 * t)),
        0.82 - 0.05 * np.exp(-0.3 * t),
    ])
    bottleneck = generalized_bottleneck(factors, rho=8.0)
    truth = realized_outcome(technical, market, adoption, utilization, bottleneck)
    observed = truth * np.exp(rng.normal(0.0, 0.035, size=periods))
    frame = pd.DataFrame({
        "time_years": t, "theta": theta, "cost": cost, "duration": duration,
        "automation": automation, "parallelism": parallelism, "reliability": reliability,
        "technical_capacity": technical, "market": market, "adoption": adoption,
        "utilization": utilization, "bottleneck": bottleneck, "truth": truth, "value": observed,
    })
    return SyntheticSeries(frame, "Synthetic canonical-system trajectory with known factors and deterministic seed.")
