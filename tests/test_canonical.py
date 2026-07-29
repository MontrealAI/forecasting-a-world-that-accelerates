import numpy as np
import pytest

from fwta.canonical import (
    double_counting_audit,
    generalized_bottleneck,
    generalized_realized_outcome,
    realized_outcome,
    technical_capacity,
    technical_growth_rate,
)


def test_generalized_bottleneck_is_near_weakest_link() -> None:
    factors = np.array([0.9, 0.55, 0.8])
    value = generalized_bottleneck(factors, rho=40.0)
    assert 0.55 <= value < 0.58


def test_realized_outcome_uses_minimum_branch() -> None:
    result = realized_outcome(technical=100.0, market=20.0, adoption=0.5, utilization=2.0, bottleneck=0.8)
    assert float(result) == pytest.approx(16.0)


def test_technical_growth_and_capacity() -> None:
    t = np.linspace(0.0, 1.0, 6)
    ones = np.ones_like(t)
    zeros = np.zeros_like(t)
    growth = technical_growth_rate(
        theta_dot=ones,
        cost=ones,
        cost_dot=zeros,
        duration=ones,
        duration_dot=zeros,
        automation=ones,
        automation_dot=zeros,
        parallelism=ones,
        parallelism_dot=zeros,
        reliability=ones,
        reliability_dot=zeros,
        elasticities={
            "theta": 0.5,
            "cost": 0.0,
            "duration": 0.0,
            "automation": 0.0,
            "parallelism": 0.0,
            "reliability": 0.0,
        },
    )
    capacity = technical_capacity(t, 2.0, growth)
    assert capacity[-1] == pytest.approx(2.0 * np.exp(0.5), rel=1e-5)


def test_double_counting_audit() -> None:
    assert double_counting_audit({"reliability": "technical", "authority": "bottleneck"}) == []
    errors = double_counting_audit({"trust": "demand,bottleneck"})
    assert errors


def test_generalized_realized_outcome_exact_and_soft_min() -> None:
    exact = generalized_realized_outcome(10.0, 20.0, rho=float("inf"))
    soft = generalized_realized_outcome(10.0, 20.0, rho=20.0)
    assert float(exact) == pytest.approx(10.0)
    assert float(soft) == pytest.approx(10.0, rel=0.04)
