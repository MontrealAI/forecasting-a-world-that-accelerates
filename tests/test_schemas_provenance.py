import json
from pathlib import Path

from fwta.io import validate_instance
from fwta.provenance import build_manifest, sha256_file

ROOT = Path(__file__).resolve().parents[1]


def test_protocol_examples_validate() -> None:
    cases = (
        ("example-input.yaml", "input.schema.json"),
        ("example-output.yaml", "output.schema.json"),
        ("example-evidence-record.yaml", "evidence-record.schema.json"),
        ("example-workflow.yaml", "task-graph.schema.json"),
        ("example-hindcast-case.yaml", "hindcast-case.schema.json"),
        ("example-protocol-envelope.yaml", "protocol-envelope.schema.json"),
    )
    for instance, schema in cases:
        errors = validate_instance(ROOT / "protocol/examples" / instance, ROOT / "protocol" / schema)
        assert errors == [], f"{instance}: {errors}"


def test_manifest_is_deterministic_and_excludes_dist(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist/x.txt").write_text("x", encoding="utf-8")
    (tmp_path / "release").mkdir()
    (tmp_path / "release/MANIFEST.json").write_text("old", encoding="utf-8")
    (tmp_path / ".coverage").write_text("cache", encoding="utf-8")
    (tmp_path / "tmp").mkdir()
    (tmp_path / "tmp/smoke.json").write_text("transient", encoding="utf-8")
    (tmp_path / "src/demo.egg-info").mkdir(parents=True)
    (tmp_path / "src/demo.egg-info/PKG-INFO").write_text("generated", encoding="utf-8")
    first = build_manifest(tmp_path)
    second = build_manifest(tmp_path)
    assert first == second
    assert first[0]["sha256"] == sha256_file(tmp_path / "a.txt")
    assert all(not str(record["path"]).startswith("dist/") for record in first)
    assert all(record["path"] != "release/MANIFEST.json" for record in first)
    assert all(record["path"] != ".coverage" for record in first)
    assert all(not str(record["path"]).startswith("tmp/") for record in first)
    assert all(".egg-info/" not in str(record["path"]) for record in first)
    json.dumps(first)
