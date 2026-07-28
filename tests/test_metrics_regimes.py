import math

import numpy as np

from fwta.metrics import acceleration, annual_improvement, doubling_time, log_growth_rate
from fwta.regimes import accelerated_exponential, cumulative_transition_probability, double_exponential, milestone_time


def test_growth_metrics() -> None:
    growth = log_growth_rate(4, 2, 1)
    assert math.isclose(growth, math.log(2))
    assert math.isclose(doubling_time(growth), 1)
    assert math.isclose(annual_improvement(growth), 1)
    assert acceleration(8, 4, 2, 1) == 0


def test_regime_paths_and_hazard() -> None:
    t = np.linspace(0, 3, 31)
    path = accelerated_exponential(t, 1.0, 0.2, 0.1)
    assert np.all(np.diff(path) > 0)
    discontinuous = double_exponential(t, 2.0, 1.0, 1.1, 0.3, 0.4)
    assert np.isnan(discontinuous[t < 1.0]).all()
    probability = cumulative_transition_probability(t, np.full_like(t, 0.2))
    assert np.all(np.diff(probability) >= 0)
    assert math.isfinite(milestone_time(t, path, 1.5))
