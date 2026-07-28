import numpy as np
import pytest

from fwta.models import fit_all_models, fit_model, predict_model, rolling_origin_hindcast


def test_fit_exponential_recovers_growth() -> None:
    t = np.linspace(0.0, 3.0, 25)
    y = 2.0 * np.exp(0.45 * t)
    fit = fit_model("exponential", t, y)
    assert fit.converged
    assert fit.parameters["growth"] == pytest.approx(0.45, abs=1e-8)
    predicted = predict_model("exponential", t, fit.parameters)
    assert np.allclose(predicted, y)


def test_fit_accelerating_recovers_acceleration() -> None:
    t = np.linspace(0.0, 3.0, 30)
    y = 1.3 * np.exp(0.2 * t + 0.5 * 0.18 * t**2)
    fit = fit_model("accelerating", t, y)
    assert fit.parameters["acceleration"] == pytest.approx(0.18, abs=1e-8)


def test_fit_all_and_hindcast() -> None:
    t = np.arange(24) / 12.0
    y = np.exp(0.35 * t)
    fits = fit_all_models(t, y, models=("linear", "exponential", "accelerating"))
    assert all(name in fits for name in ("linear", "exponential", "accelerating"))
    hindcast = rolling_origin_hindcast(t, y, min_train=10, horizon_steps=2, models=("linear", "exponential"))
    assert hindcast["exponential"]["n"] > 0
    assert hindcast["exponential"]["rmse_log"] < hindcast["linear"]["rmse_log"]
