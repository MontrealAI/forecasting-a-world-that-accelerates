from __future__ import annotations

import math

import numpy as np
import pytest

from fwta.models import (
    FitResult,
    fit_all_models,
    fit_model,
    model_average_prediction,
    predict_model,
    rolling_origin_hindcast,
)


def test_all_prediction_branches_and_fit_failures() -> None:
    t = np.linspace(0, 2, 10)
    parameters = {
        "decaying_acceleration": {"log_x0": 0.0, "growth": 0.2, "initial_acceleration": 0.1, "kappa": 0.5},
        "logistic": {"x0": 1.0, "growth": 0.5, "capacity": 10.0},
        "change_point": {"log_x0": 0.0, "growth_pre": 0.2, "growth_delta": 0.3, "change_time": 1.0},
    }
    for name, params in parameters.items():
        assert np.all(predict_model(name, t, params) > 0)
    with pytest.raises(ValueError):
        predict_model("missing", t, {})
    with pytest.raises(ValueError):
        fit_model("exponential", [0, 1], [1, 2])
    with pytest.raises(ValueError):
        fit_model("exponential", [0, 0, 1], [1, 2, 3])
    with pytest.raises(ValueError):
        fit_model("change_point", np.arange(6), np.arange(1, 7))
    with pytest.raises(ValueError):
        fit_model("missing", [0, 1, 2], [1, 2, 3])


def test_model_average_and_hindcast_error_paths() -> None:
    bad = FitResult("bad", {}, 3, 0, False, "bad", -math.inf, math.inf, math.inf, math.inf, math.inf)
    with pytest.raises(RuntimeError):
        model_average_prediction({"bad": bad}, [3])
    fits = fit_all_models([0, 1, 2], [1, 2, 3], models=("missing",))
    assert fits["missing"].converged is False
    with pytest.raises(ValueError):
        rolling_origin_hindcast([0, 1, 2, 3], [1, 2, 3, 4], min_train=3)


def test_linear_positive_fallback_and_model_average() -> None:
    t = np.arange(8, dtype=float)
    y = np.array([10, 9, 8, 7, 6, 5, 4, 3], dtype=float)
    fit = fit_model("linear", t, y)
    assert fit.converged
    fits = fit_all_models(t, y, models=("linear", "exponential"))
    prediction, weights = model_average_prediction(fits, [8, 9])
    assert prediction.shape == (2,)
    assert sum(weights.values()) == pytest.approx(1)
