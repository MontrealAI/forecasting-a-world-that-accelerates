from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ActionEvaluation:
    action: str
    expected_score: float
    cvar_penalty: float
    objective: float
    maximum_regret: float


def cvar(losses: np.ndarray, alpha: float = 0.95) -> float:
    values = np.asarray(losses, dtype=float)
    if values.ndim != 1 or values.size == 0 or not 0 < alpha < 1:
        raise ValueError("losses must be non-empty and alpha in (0,1)")
    threshold = np.quantile(values, alpha)
    tail = values[values >= threshold]
    return float(np.mean(tail)) if tail.size else float(threshold)


def evaluate_actions(
    actions: Mapping[str, Mapping[str, Mapping[str, float]]],
    scenario_probabilities: Mapping[str, float],
    risk_aversion: float = 1.0,
    cvar_alpha: float = 0.95,
) -> list[ActionEvaluation]:
    if not np.isclose(sum(scenario_probabilities.values()), 1.0):
        raise ValueError("scenario probabilities must sum to one")
    scenarios = list(scenario_probabilities)
    best_by_scenario = {
        scenario: max(
            record[scenario]["npv"] + record[scenario].get("learning", 0.0) + record[scenario].get("option", 0.0)
            for record in actions.values()
        )
        for scenario in scenarios
    }
    evaluations: list[ActionEvaluation] = []
    for action, record in actions.items():
        scores = np.array(
            [
                record[scenario]["npv"] + record[scenario].get("learning", 0.0) + record[scenario].get("option", 0.0)
                for scenario in scenarios
            ],
            dtype=float,
        )
        probs = np.array([scenario_probabilities[scenario] for scenario in scenarios], dtype=float)
        expected = float(np.dot(probs, scores))
        losses = np.array(
            [record[scenario].get("loss", max(0.0, -score)) for scenario, score in zip(scenarios, scores, strict=True)]
        )
        penalty = cvar(losses, cvar_alpha)
        regrets = np.array(
            [best_by_scenario[scenario] - score for scenario, score in zip(scenarios, scores, strict=True)]
        )
        evaluations.append(
            ActionEvaluation(
                action=action,
                expected_score=expected,
                cvar_penalty=penalty,
                objective=expected - risk_aversion * penalty,
                maximum_regret=float(np.max(regrets)),
            )
        )
    return sorted(evaluations, key=lambda item: item.objective, reverse=True)
