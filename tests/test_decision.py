from __future__ import annotations

import numpy as np
import pytest

from fwta.decision import cvar, evaluate_actions


def test_cvar_and_action_ranking() -> None:
    assert cvar(np.array([0.0, 1.0, 2.0, 10.0]), 0.75) == pytest.approx(10.0)
    actions = {
        "reversible": {
            "base": {"npv": 10.0, "learning": 2.0, "option": 3.0, "loss": 1.0},
            "accelerated": {"npv": 18.0, "learning": 2.0, "option": 5.0, "loss": 2.0},
        },
        "fragile": {
            "base": {"npv": 16.0, "loss": 12.0},
            "accelerated": {"npv": 24.0, "loss": 20.0},
        },
    }
    result = evaluate_actions(actions, {"base": 0.6, "accelerated": 0.4}, risk_aversion=0.5, cvar_alpha=0.5)
    assert result[0].action == "reversible"
    assert result[0].maximum_regret >= 0


def test_decision_validation() -> None:
    with pytest.raises(ValueError):
        cvar(np.array([]))
    with pytest.raises(ValueError):
        cvar(np.array([1.0]), 1.0)
    with pytest.raises(ValueError):
        evaluate_actions({"a": {"s": {"npv": 1.0}}}, {"s": 0.8})
