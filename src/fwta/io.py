from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


def _json_compatible(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _json_compatible(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_compatible(item) for item in value]
    return value


def load_structured(path: str | Path) -> Any:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        return _json_compatible(yaml.safe_load(text))
    raise ValueError(f"unsupported file extension {suffix!r}")


def dump_json(data: Any, path: str | Path) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def schema_registry(schema_directory: str | Path) -> Registry:
    registry = Registry()
    for path in sorted(Path(schema_directory).glob("*.schema.json")):
        contents = load_structured(path)
        identifier = contents.get("$id")
        if identifier:
            registry = registry.with_resource(identifier, Resource.from_contents(contents))
    return registry


def validate_instance(instance_path: str | Path, schema_path: str | Path) -> list[str]:
    instance_file = Path(instance_path)
    schema_file = Path(schema_path)
    instance = load_structured(instance_file)
    schema = load_structured(schema_file)
    validator = Draft202012Validator(
        schema,
        registry=schema_registry(schema_file.parent),
        format_checker=FormatChecker(),
    )
    return [
        f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]
