from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from scipy.optimize import least_squares

from .metrics import aicc, akaike_weights, bic, gaussian_log_likelihood, mae, rmse, smape


@dataclass(frozen=True)
class FitResult:
    model: str
    parameters: dict[str, float]
    n_observations: int
    n_parameters: int
    converged: bool
    message: str
    log_likelihood: float
    aicc: float
    bic: float
    rmse_log: float
    mae_log: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate(time: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    if t.ndim != 1 or y.ndim != 1 or t.size != y.size or t.size < 3:
        raise ValueError("time and values must be equal-length one-dimensional arrays with at least three points")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(y)) or np.any(y <= 0):
        raise ValueError("time must be finite and values must be finite and positive")
    if np.any(np.diff(t) <= 0):
        raise ValueError("time must be strictly increasing")
    origin = float(t[0])
    return t - origin, y, origin


def predict_model(model: str, time: np.ndarray | list[float], parameters: dict[str, float]) -> np.ndarray:
    t = np.asarray(time, dtype=float) - float(parameters.get("time_origin", 0.0))
    if model == "linear":
        result = parameters["intercept"] + parameters["slope"] * t
    elif model == "exponential":
        result = np.exp(parameters["log_x0"] + parameters["growth"] * t)
    elif model == "accelerating":
        result = np.exp(
            parameters["log_x0"] + parameters["growth"] * t + 0.5 * parameters["acceleration"] * t**2
        )
    elif model == "decaying_acceleration":
        kappa = parameters["kappa"]
        exponent = (
            parameters["log_x0"]
            + parameters["growth"] * t
            + (parameters["initial_acceleration"] / kappa) * t
            - (parameters["initial_acceleration"] / kappa**2) * (1.0 - np.exp(-kappa * t))
        )
        result = np.exp(exponent)
    elif model == "logistic":
        capacity = parameters["capacity"]
        x0 = parameters["x0"]
        result = capacity / (1.0 + (capacity / x0 - 1.0) * np.exp(-parameters["growth"] * t))
    elif model == "change_point":
        hinge = np.maximum(0.0, t - parameters["change_time"])
        result = np.exp(
            parameters["log_x0"] + parameters["growth_pre"] * t + parameters["growth_delta"] * hinge
        )
    else:
        raise ValueError(f"unknown model {model!r}")
    return np.maximum(np.asarray(result, dtype=float), np.finfo(float).tiny)


def _finish(model: str, parameters: dict[str, float], t_abs: np.ndarray, y: np.ndarray, converged: bool, message: str) -> FitResult:
    pred = predict_model(model, t_abs, parameters)
    residuals = np.log(y) - np.log(pred)
    ll = gaussian_log_likelihood(residuals)
    k = len([key for key in parameters if key != "time_origin"]) + 1
    return FitResult(
        model=model,
        parameters=parameters,
        n_observations=int(y.size),
        n_parameters=k,
        converged=bool(converged),
        message=str(message),
        log_likelihood=ll,
        aicc=aicc(ll, int(y.size), k),
        bic=bic(ll, int(y.size), k),
        rmse_log=rmse(np.log(y), np.log(pred)),
        mae_log=mae(np.log(y), np.log(pred)),
    )


def fit_model(model: str, time: np.ndarray | list[float], values: np.ndarray | list[float]) -> FitResult:
    t_rel, y, origin = _validate(np.asarray(time), np.asarray(values))
    t_abs = t_rel + origin
    log_y = np.log(y)

    if model == "linear":
        design = np.column_stack([np.ones_like(t_rel), t_rel])
        raw_intercept, raw_slope = np.linalg.lstsq(design, y, rcond=None)[0]
        initial_intercept = max(float(raw_intercept), float(np.min(y)) * 0.1, 1e-12)

        def residual(par: np.ndarray) -> np.ndarray:
            intercept = math.exp(float(par[0]))
            slope = float(par[1])
            pred = intercept + slope * t_rel
            if np.any(pred <= 0):
                penalty = np.minimum(pred, 0.0)
                return np.full_like(log_y, 1e3) + 1e3 * penalty
            return np.log(pred) - log_y

        opt = least_squares(
            residual,
            np.array([math.log(initial_intercept), float(raw_slope)]),
            bounds=(np.array([-50.0, -1e12]), np.array([50.0, 1e12])),
            loss="linear",
            max_nfev=5000,
        )
        params = {"intercept": float(math.exp(opt.x[0])), "slope": float(opt.x[1]), "time_origin": origin}
        return _finish(model, params, t_abs, y, opt.success, "Gaussian log-residual maximum likelihood: " + str(opt.message))

    if model == "exponential":
        design = np.column_stack([np.ones_like(t_rel), t_rel])
        log_x0, growth = np.linalg.lstsq(design, log_y, rcond=None)[0]
        params = {"log_x0": float(log_x0), "growth": float(growth), "time_origin": origin}
        return _finish(model, params, t_abs, y, True, "Gaussian log-residual maximum likelihood (closed form)")

    if model == "accelerating":
        design = np.column_stack([np.ones_like(t_rel), t_rel, 0.5 * t_rel**2])
        log_x0, growth, acceleration = np.linalg.lstsq(design, log_y, rcond=None)[0]
        params = {
            "log_x0": float(log_x0),
            "growth": float(growth),
            "acceleration": float(acceleration),
            "time_origin": origin,
        }
        return _finish(model, params, t_abs, y, True, "Gaussian log-residual maximum likelihood (closed form quadratic)")

    if model == "decaying_acceleration":
        acc_fit = fit_model("accelerating", t_abs, y)
        p = acc_fit.parameters
        initial = np.array([p["log_x0"], p["growth"], max(p["acceleration"], 1e-4), math.log(0.5)])

        def residual(par: np.ndarray) -> np.ndarray:
            log_x0, growth, initial_acceleration, log_kappa = par
            kappa = math.exp(log_kappa)
            exponent = (
                log_x0 + growth * t_rel + (initial_acceleration / kappa) * t_rel
                - (initial_acceleration / kappa**2) * (1.0 - np.exp(-kappa * t_rel))
            )
            return exponent - log_y

        opt = least_squares(
            residual,
            initial,
            bounds=(np.array([-50.0, -10.0, -10.0, -8.0]), np.array([50.0, 10.0, 10.0, 5.0])),
            loss="linear",
            max_nfev=5000,
        )
        params = {
            "log_x0": float(opt.x[0]),
            "growth": float(opt.x[1]),
            "initial_acceleration": float(opt.x[2]),
            "kappa": float(math.exp(opt.x[3])),
            "time_origin": origin,
        }
        return _finish(model, params, t_abs, y, opt.success, opt.message)

    if model == "logistic":
        maximum = float(np.max(y))
        initial = np.array([math.log(max(y[0], 1e-9)), math.log(0.5), math.log(max(maximum * 0.5, 1e-6))])

        def unpack(par: np.ndarray) -> tuple[float, float, float]:
            x0 = math.exp(par[0])
            growth = math.exp(par[1])
            capacity = maximum + math.exp(par[2])
            return x0, growth, capacity

        def residual(par: np.ndarray) -> np.ndarray:
            x0, growth, capacity = unpack(par)
            pred = capacity / (1.0 + (capacity / x0 - 1.0) * np.exp(-growth * t_rel))
            return np.log(np.maximum(pred, 1e-300)) - log_y

        opt = least_squares(
            residual,
            initial,
            bounds=(np.array([-50.0, -8.0, -20.0]), np.array([50.0, 5.0, 20.0])),
            loss="linear",
            max_nfev=5000,
        )
        x0, growth, capacity = unpack(opt.x)
        params = {"x0": x0, "growth": growth, "capacity": capacity, "time_origin": origin}
        return _finish(model, params, t_abs, y, opt.success, opt.message)

    if model == "change_point":
        if y.size < 7:
            raise ValueError("change_point requires at least seven observations")
        candidates = t_rel[2:-2]
        best: tuple[float, np.ndarray, float] | None = None
        for change_time in candidates:
            hinge = np.maximum(0.0, t_rel - change_time)
            design = np.column_stack([np.ones_like(t_rel), t_rel, hinge])
            coefficients = np.linalg.lstsq(design, log_y, rcond=None)[0]
            residuals = design @ coefficients - log_y
            score = float(np.mean(residuals**2))
            if best is None or score < best[0]:
                best = (score, coefficients, float(change_time))
        assert best is not None
        _, coefficients, change_time = best
        params = {
            "log_x0": float(coefficients[0]),
            "growth_pre": float(coefficients[1]),
            "growth_delta": float(coefficients[2]),
            "change_time": change_time,
            "time_origin": origin,
        }
        return _finish(model, params, t_abs, y, True, "Gaussian log-residual maximum likelihood with grid-searched continuous change point")

    raise ValueError(f"unknown model {model!r}")


DEFAULT_MODELS = ("linear", "exponential", "accelerating", "decaying_acceleration", "logistic", "change_point")


def fit_all_models(
    time: np.ndarray | list[float],
    values: np.ndarray | list[float],
    models: tuple[str, ...] = DEFAULT_MODELS,
) -> dict[str, FitResult]:
    results: dict[str, FitResult] = {}
    for model in models:
        try:
            results[model] = fit_model(model, time, values)
        except (ValueError, RuntimeError, FloatingPointError) as exc:
            results[model] = FitResult(
                model=model,
                parameters={},
                n_observations=len(values),
                n_parameters=0,
                converged=False,
                message=str(exc),
                log_likelihood=-math.inf,
                aicc=math.inf,
                bic=math.inf,
                rmse_log=math.inf,
                mae_log=math.inf,
            )
    return results


def model_average_prediction(
    fits: dict[str, FitResult], time: np.ndarray | list[float]
) -> tuple[np.ndarray, dict[str, float]]:
    weights = akaike_weights({name: fit.aicc for name, fit in fits.items()})
    predictions = []
    valid_weights = []
    for name, fit in fits.items():
        weight = weights.get(name, 0.0)
        if weight > 0 and fit.converged and fit.parameters:
            predictions.append(predict_model(name, time, fit.parameters))
            valid_weights.append(weight)
    if not predictions:
        raise RuntimeError("no converged models available for averaging")
    w = np.asarray(valid_weights, dtype=float)
    w /= w.sum()
    stacked = np.vstack(predictions)
    return np.average(stacked, axis=0, weights=w), weights


def rolling_origin_hindcast(
    time: np.ndarray | list[float],
    values: np.ndarray | list[float],
    min_train: int = 10,
    horizon_steps: int = 1,
    models: tuple[str, ...] = DEFAULT_MODELS,
) -> dict[str, dict[str, Any]]:
    t = np.asarray(time, dtype=float)
    y = np.asarray(values, dtype=float)
    if min_train < 4 or min_train + horizon_steps > y.size:
        raise ValueError("invalid min_train or horizon_steps")
    records: dict[str, list[tuple[float, float, float]]] = {model: [] for model in models}
    records["model_average"] = []
    for end in range(min_train, y.size - horizon_steps + 1):
        train_t, train_y = t[:end], y[:end]
        test_t, test_y = t[end : end + horizon_steps], y[end : end + horizon_steps]
        fits = fit_all_models(train_t, train_y, models)
        for model, fit in fits.items():
            if fit.converged and fit.parameters:
                pred = predict_model(model, test_t, fit.parameters)
                records[model].extend((float(tt), float(aa), float(pp)) for tt, aa, pp in zip(test_t, test_y, pred))
        try:
            avg_pred, _ = model_average_prediction(fits, test_t)
            records["model_average"].extend(
                (float(tt), float(aa), float(pp)) for tt, aa, pp in zip(test_t, test_y, avg_pred)
            )
        except RuntimeError:
            pass

    output: dict[str, dict[str, Any]] = {}
    for model, rows in records.items():
        if not rows:
            output[model] = {"n": 0, "rmse_log": math.inf, "mae_log": math.inf, "smape": math.inf, "records": []}
            continue
        actual = np.array([row[1] for row in rows])
        predicted = np.array([row[2] for row in rows])
        output[model] = {
            "n": len(rows),
            "rmse_log": rmse(np.log(actual), np.log(np.maximum(predicted, 1e-300))),
            "mae_log": mae(np.log(actual), np.log(np.maximum(predicted, 1e-300))),
            "smape": smape(actual, predicted),
            "records": [{"time": a, "actual": b, "predicted": c} for a, b, c in rows],
        }
    return output
