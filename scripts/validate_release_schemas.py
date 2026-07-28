from __future__ import annotations

from pathlib import Path

from fwta.io import validate_instance

ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ("protocol/examples/example-input.yaml", "protocol/input.schema.json"),
    ("protocol/examples/example-output.yaml", "protocol/output.schema.json"),
    ("protocol/examples/example-evidence-record.yaml", "protocol/evidence-record.schema.json"),
    ("protocol/examples/example-workflow.yaml", "protocol/task-graph.schema.json"),
    ("protocol/examples/example-hindcast-case.yaml", "protocol/hindcast-case.schema.json"),
    ("protocol/examples/example-protocol-envelope.yaml", "protocol/protocol-envelope.schema.json"),
    ("protocol/v2/examples/canonical-reference-input.yaml", "protocol/v2/input.schema.json"),
    ("protocol/v2/examples/metr-time-horizon-input.yaml", "protocol/v2/input.schema.json"),
    ("protocol/v2/examples/smoke-input.yaml", "protocol/v2/input.schema.json"),
    ("examples/metr-time-horizon-forecast.yaml", "protocol/v2/input.schema.json"),
    ("examples/swe-bench-verified-frontier-forecast.yaml", "protocol/v2/input.schema.json"),
    ("results/ceiling/reference-forecast.json", "protocol/v2/output.schema.json"),
    ("results/ceiling/registry-record.json", "protocol/v2/registry-record.schema.json"),
)


def main() -> int:
    for instance, schema in CASES:
        errors = validate_instance(ROOT / instance, ROOT / schema)
        if errors:
            joined = "\n".join(f"- {error}" for error in errors)
            raise SystemExit(f"schema validation failed for {instance} against {schema}:\n{joined}")
        print(f"validated {instance} against {schema}")
    print(f"validated {len(CASES)} release schema instances")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
