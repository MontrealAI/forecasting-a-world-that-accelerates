from __future__ import annotations

import numpy as np
import pytest

from fwta.probabilistic import (
    brier_score,
    predictive_samples,
    probabilistic_rolling_origin_hindcast,
    quantile_points,
    sample_crps,
    weighted_interval_score,
)


def _series() -> tuple[np.ndarray, np.ndarray]:
    time = np.linspace(0.0, 1.4, 8)
    values = 3.0 * np.exp(0.22 * time)
    return time, values


def test_predictive_samples_quantiles_and_scores() -> None:
    time, values = _series()
    future = np.array([1.4, 1.6, 1.8])
    simulation = predictive_samples(
        time,
        values,
        future,
        models=("exponential",),
        draws=20,
        seed=11,
        include_observation_noise=True,
    )
    assert simulation.samples.shape == (20, 3)
    assert simulation.draws == 20
    assert simulation.model_weights["exponential"] == pytest.approx(1.0)
    points = quantile_points(simulation.samples, ["a", "b", "c"])
    assert [point["date"] for point in points] == ["a", "b", "c"]
    assert all(point["p02_5"] <= point["median"] <= point["p97_5"] for point in points)
    samples = simulation.samples[:, -1]
    observation = float(np.median(samples))
    assert sample_crps(samples, observation) >= 0
    assert weighted_interval_score(samples, observation) >= 0
    assert brier_score(0.8, True) == pytest.approx(0.04)
    assert brier_score(0.2, False) == pytest.approx(0.04)


def test_probabilistic_hindcast() -> None:
    time, values = _series()
    result = probabilistic_rolling_origin_hindcast(
        time,
        values,
        min_train=6,
        horizon_steps=1,
        models=("exponential",),
        draws=20,
        seed=17,
    )
    assert result["n"] == 2
    assert 0 <= result["coverage80"] <= 1
    assert 0 <= result["coverage95"] <= 1
    assert result["mean_crps"] >= 0
    assert result["mean_wis"] >= 0


@pytest.mark.parametrize(
    ("time", "values"),
    [
        ([0.0, 1.0, 2.0], [1.0, 2.0, 3.0]),
        ([0.0, 1.0, 1.0, 2.0], [1.0, 2.0, 3.0, 4.0]),
        ([0.0, 1.0, 2.0, 3.0], [1.0, 0.0, 3.0, 4.0]),
    ],
)
def test_probabilistic_validation(time: list[float], values: list[float]) -> None:
    with pytest.raises(ValueError):
        predictive_samples(time, values, [4.0], models=("exponential",), draws=20)


def test_probabilistic_argument_validation() -> None:
    time, values = _series()
    with pytest.raises(ValueError):
        predictive_samples(time, values, [], models=("exponential",), draws=20)
    with pytest.raises(ValueError):
        predictive_samples(time, values, [1.8, 1.7], models=("exponential",), draws=20)
    with pytest.raises(ValueError):
        predictive_samples(time, values, [1.8], models=("exponential",), draws=19)
    with pytest.raises(ValueError):
        quantile_points(np.array([1.0, 2.0]))
    with pytest.raises(ValueError):
        quantile_points(np.ones((2, 2)), ["one"])
    with pytest.raises(ValueError):
        sample_crps([1.0], 1.0)
    with pytest.raises(ValueError):
        weighted_interval_score([1.0], 1.0)
    with pytest.raises(ValueError):
        brier_score(1.1, True)
    with pytest.raises(ValueError):
        probabilistic_rolling_origin_hindcast(time, values, min_train=3, models=("exponential",), draws=20)
