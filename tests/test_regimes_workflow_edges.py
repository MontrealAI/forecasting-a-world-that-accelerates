from __future__ import annotations

import math

import numpy as np
import pytest

from fwta.regimes import (
    constrained_growth,
    cumulative_transition_probability,
    decaying_acceleration_path,
    double_exponential,
    exponential_path,
    logistic_path,
    milestone_time,
)
from fwta.workflow import Task, analyze_workflow, task_from_mapping


def test_regime_paths_and_constraints() -> None:
    t = np.linspace(0, 2, 9)
    assert exponential_path(t, 2, 0)[-1] == pytest.approx(2)
    assert decaying_acceleration_path(t, 1, 0.2, 0.3, 0.5)[-1] > 1
    logistic = logistic_path(t, 1, 1, 10)
    assert np.all(np.diff(logistic) > 0) and logistic[-1] < 10
    constrained = constrained_growth(t, 1, lambda _: 1.0, lambda _: 0.8, lambda _: 10.0)
    assert constrained[-1] > constrained[0] and constrained[-1] < 10
    assert math.isinf(milestone_time(t, constrained, 100))
    assert milestone_time(t, constrained, 1) == 0
    assert milestone_time([0, 1], [1, 1], 1.0) == 0


def test_regime_validation_edges() -> None:
    calls = [
        lambda: exponential_path([0], 0, 1),
        lambda: exponential_path([float("nan")], 1, 1),
        lambda: decaying_acceleration_path([0], 1, 1, 1, 0),
        lambda: logistic_path([0], 2, 1, 1),
        lambda: double_exponential([0], 0, 0, 1, 1, 1),
        lambda: constrained_growth([0], 1, lambda _: 1, lambda _: 1, lambda _: 2),
        lambda: constrained_growth([1, 0], 1, lambda _: 1, lambda _: 1, lambda _: 2),
        lambda: constrained_growth([0, 1], 0, lambda _: 1, lambda _: 1, lambda _: 2),
        lambda: constrained_growth([0, 1], 1, lambda _: 1, lambda _: 2, lambda _: 2),
        lambda: cumulative_transition_probability([0, 1], [0.1, -0.1]),
        lambda: milestone_time([0], [1, 2], 1),
    ]
    for call in calls:
        with pytest.raises(ValueError):
            call()


def test_task_mapping_reliability_costs_and_errors() -> None:
    task = task_from_mapping({
        "task_id": "a", "success_probability": 0.8, "max_attempts": 2,
        "ai_time": 1, "verification_time": 0.5, "ai_cost": 2,
        "verification_cost": 1, "human_fallback_cost": 10,
        "per_attempt_reliability": 0.9, "dependencies": [],
    })
    assert task.achieved_reliability == pytest.approx(0.99)
    assert task.expected_cost > 0
    result = analyze_workflow([task], parallel_workers=2, parallel_efficiency=0.8, coordination_coefficient=0.2, correlated_failure_penalty=1000)
    assert result.workflow_reliability == 0
    assert math.isinf(result.cost_per_verified_success)

    invalid_tasks = [
        lambda: Task("", 1, 1, 1, 1),
        lambda: Task("a", 0, 1, 1, 1),
        lambda: Task("a", 1, 0, 1, 1),
        lambda: Task("a", 1, 1, -1, 1),
        lambda: Task("a", 1, 1, 1, 1, per_attempt_reliability=0),
    ]
    for call in invalid_tasks:
        with pytest.raises(ValueError):
            call()

    valid = Task("a", 1, 1, 1, 0)
    for kwargs in (
        {"tasks": []},
        {"tasks": [valid], "parallel_workers": 0},
        {"tasks": [valid], "parallel_efficiency": 0},
        {"tasks": [valid], "coordination_coefficient": -1},
        {"tasks": [valid, valid]},
        {"tasks": [Task("b", 1, 1, 1, 0, dependencies=("missing",))]},
    ):
        with pytest.raises(ValueError):
            analyze_workflow(**kwargs)
