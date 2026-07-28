import math

import numpy as np
import pytest

from fwta.regimes import accelerated_exponential, cumulative_transition_probability, double_exponential, milestone_time


def test_accelerated_exponential() -> None:
    values = accelerated_exponential([0.0, 1.0], 2.0, 0.3, 0.2)
    assert values[0] == pytest.approx(2.0)
    assert values[1] == pytest.approx(2.0 * math.exp(0.4))


def test_double_exponential_at_transition() -> None:
    values = double_exponential([2.0, 3.0], 5.0, 2.0, 1.2, 0.4, 0.5)
    assert values[0] == pytest.approx(6.0)
    assert values[1] > values[0]


def test_hazard_and_milestone() -> None:
    t = np.linspace(0.0, 2.0, 5)
    probability = cumulative_transition_probability(t, np.full_like(t, 0.2))
    assert probability[-1] == pytest.approx(1.0 - math.exp(-0.4), rel=1e-4)
    assert milestone_time(t, [1, 2, 3, 4, 5], 3.5) == pytest.approx(1.25)
