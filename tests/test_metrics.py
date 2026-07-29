import math

import numpy as np
import pytest

from fwta.metrics import (
    acceleration,
    aicc,
    akaike_weights,
    annual_improvement,
    doubling_time,
    log_growth_rate,
    logit,
    smape,
)


def test_growth_helpers() -> None:
    growth = log_growth_rate(4.0, 2.0, 1.0)
    assert growth == pytest.approx(math.log(2.0))
    assert annual_improvement(growth) == pytest.approx(1.0)
    assert doubling_time(growth) == pytest.approx(1.0)
    assert acceleration(4.0, 2.0, 1.0, 1.0) == pytest.approx(0.0)


def test_logit_and_smape() -> None:
    assert logit(0.5) == pytest.approx(0.0)
    assert smape(np.array([1.0, 2.0]), np.array([1.0, 2.0])) == 0.0


def test_aicc_and_weights() -> None:
    assert math.isfinite(aicc(-10.0, 30, 3))
    weights = akaike_weights({"a": 10.0, "b": 12.0})
    assert sum(weights.values()) == pytest.approx(1.0)
    assert weights["a"] > weights["b"]
