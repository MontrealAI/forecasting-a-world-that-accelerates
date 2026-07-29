from __future__ import annotations

import math
from pathlib import Path

import pytest

from fwta.ablation import fit_canonical_elasticities
from fwta.canonical import (
    double_counting_audit,
    generalized_bottleneck,
    realized_outcome,
    technical_capacity,
    technical_growth_rate,
)
from fwta.io import dump_json, load_structured, schema_registry, validate_instance
from fwta.metrics import (
    aicc,
    akaike_weights,
    bic,
    doubling_time,
    gaussian_log_likelihood,
    log_growth_rate,
    logit,
    mae,
    mape,
    rmse,
    smape,
)
from fwta.provenance import write_manifest


ELASTICITIES = {"theta": 1.0, "cost": 1.0, "duration": 1.0, "automation": 1.0, "parallelism": 1.0, "reliability": 1.0}


def test_canonical_validation_edges() -> None:
    with pytest.raises(ValueError):
        technical_growth_rate(0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, {})
    with pytest.raises(ValueError):
        technical_growth_rate(0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, ELASTICITIES, eps=0)
    with pytest.raises(ValueError):
        technical_growth_rate(0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, ELASTICITIES)
    with pytest.raises(ValueError):
        technical_capacity([0, 1], -1, [1, 1])
    with pytest.raises(ValueError):
        technical_capacity([1, 0], 1, [1, 1])
    with pytest.raises(ValueError):
        generalized_bottleneck([0.5, 1.1])
    with pytest.raises(ValueError):
        generalized_bottleneck([0.5, 0.8], weights=[0.2, 0.2])
    with pytest.raises(ValueError):
        generalized_bottleneck([0.5, 0.8], rho=0)
    with pytest.raises(ValueError):
        realized_outcome(-1, 1, 0.5, 1, 1)
    with pytest.raises(ValueError):
        realized_outcome(1, 1, 1.5, 1, 1)
    assert double_counting_audit({"x": "unknown"})
    assert double_counting_audit({"x": "technical,diagnostic"}) == []


def test_metric_validation_and_secondary_metrics() -> None:
    assert mae([1, 3], [2, 1]) == pytest.approx(1.5)
    assert mape([1, 2], [1, 3]) == pytest.approx(0.25)
    assert smape([0, 0], [0, 0]) == 0.0
    assert gaussian_log_likelihood([0.0, 0.0]) < 100
    assert math.isinf(doubling_time(0.0))
    assert math.isinf(aicc(-1, 3, 2))
    assert bic(-10, 20, 2) > 0
    assert akaike_weights({"a": math.inf, "b": math.inf}) == {"a": 0.0, "b": 0.0}
    assert logit(-1) < 0 and logit(2) > 0
    for call in (
        lambda: log_growth_rate(0, 1, 1),
        lambda: log_growth_rate(1, 1, 0),
        lambda: logit(0.5, 0.5),
        lambda: rmse([], []),
        lambda: rmse([1], [1, 2]),
        lambda: mae([1], [1, 2]),
        lambda: mape([1], [1, 2]),
        lambda: smape([1], [1, 2]),
        lambda: gaussian_log_likelihood([float("nan")]),
        lambda: aicc(0, 0, 1),
        lambda: bic(0, 1, 0),
    ):
        with pytest.raises(ValueError):
            call()


def test_io_manifest_and_ablation_errors(tmp_path: Path) -> None:
    payload = tmp_path / "payload.yaml"
    payload.write_text("when: 2026-07-28\n", encoding="utf-8")
    assert load_structured(payload)["when"] == "2026-07-28"
    dumped = tmp_path / "nested/out.json"
    dump_json({"é": 1}, dumped)
    assert "é" in dumped.read_text(encoding="utf-8")
    unsupported = tmp_path / "unsupported.txt"
    unsupported.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        load_structured(unsupported)
    assert len(list(schema_registry(tmp_path))) == 0
    manifest = tmp_path / "MANIFEST.json"
    write_manifest(tmp_path, manifest)
    assert manifest.exists()

    schema = tmp_path / "schema.json"
    instance = tmp_path / "instance.json"
    schema.write_text('{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","required":["x"]}', encoding="utf-8")
    instance.write_text("{}", encoding="utf-8")
    assert validate_instance(instance, schema)

    with pytest.raises(ValueError):
        fit_canonical_elasticities([1, 2], {"x": [1, float("nan")]}, [1, 1], [1, 1], [1, 1], [1, 1], ("x",))
    with pytest.raises(ValueError):
        fit_canonical_elasticities([1, -2], {"x": [1, 2]}, [1, 1], [1, 1], [1, 1], [1, 1], ("x",))
