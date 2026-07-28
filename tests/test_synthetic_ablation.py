import numpy as np

from fwta.ablation import canonical_ablation_suite
from fwta.synthetic import canonical_system_series, regime_shift_series


def test_synthetic_series_are_reproducible() -> None:
    one = regime_shift_series().frame
    two = regime_shift_series().frame
    assert one.equals(two)
    assert canonical_system_series().frame.equals(canonical_system_series().frame)


def test_full_canonical_ablation_beats_intercept_only() -> None:
    frame = canonical_system_series(periods=37).frame
    features = {
        "capability": frame["theta"],
        "cost_efficiency": -np.log(frame["cost"]),
        "time_compression": -np.log(frame["duration"]),
        "automation": np.log(frame["automation"]),
        "parallelism": np.log(frame["parallelism"]),
        "reliability": np.log(frame["reliability"]),
    }
    result = canonical_ablation_suite(frame["value"], features, frame["market"], frame["adoption"], frame["utilization"], frame["bottleneck"])
    assert result["full"]["rmse_log"] < result["intercept_only"]["rmse_log"]
