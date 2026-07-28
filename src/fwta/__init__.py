"""Forecasting a World That Accelerates reference implementation."""

from .canonical import (
    double_counting_audit,
    generalized_bottleneck,
    generalized_realized_outcome,
    realized_outcome,
    technical_capacity,
    technical_growth_rate,
)
from .engine import ForecastRun, run_forecast
from .models import FitResult, fit_all_models, fit_model, model_average_prediction, rolling_origin_hindcast
from .probabilistic import PredictiveSimulation, predictive_samples, probabilistic_rolling_origin_hindcast
from .regimes import accelerated_exponential, double_exponential, exponential_path
from .uncertainty import EnsembleForecast, residual_bootstrap_model_average
from .workflow import Task, WorkflowResult, analyze_workflow

__all__ = [
    "EnsembleForecast",
    "FitResult",
    "ForecastRun",
    "PredictiveSimulation",
    "Task",
    "WorkflowResult",
    "accelerated_exponential",
    "analyze_workflow",
    "double_counting_audit",
    "double_exponential",
    "exponential_path",
    "fit_all_models",
    "fit_model",
    "generalized_bottleneck",
    "generalized_realized_outcome",
    "model_average_prediction",
    "predictive_samples",
    "probabilistic_rolling_origin_hindcast",
    "realized_outcome",
    "residual_bootstrap_model_average",
    "run_forecast",
    "rolling_origin_hindcast",
    "technical_capacity",
    "technical_growth_rate",
]

__version__ = "2.0.0"
