from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .engine import run_forecast
from .experiments import run_all
from .io import dump_json, load_structured, validate_instance
from .models import DEFAULT_MODELS, fit_all_models, rolling_origin_hindcast
from .provenance import write_manifest
from .registry import append_registry, verify_registry
from .report import render_html_report
from .sbom import generate_cyclonedx_sbom
from .synthetic import canonical_system_series, regime_shift_series
from .workflow import analyze_workflow, task_from_mapping

_TRUE_VALUES = frozenset({"1", "true", "yes", "y", "include", "included"})


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _read_frame(path: str | Path, include_column: str | None = None) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if include_column is None:
        return frame
    if include_column not in frame.columns:
        raise ValueError(f"include column not found: {include_column}")
    series = frame[include_column]
    if pd.api.types.is_bool_dtype(series):
        mask = series.fillna(False).astype(bool)
    elif pd.api.types.is_numeric_dtype(series):
        mask = series.fillna(0).astype(float).ne(0.0)
    else:
        mask = series.fillna("").astype(str).str.strip().str.lower().isin(_TRUE_VALUES)
    filtered = frame.loc[mask].reset_index(drop=True)
    if filtered.empty:
        raise ValueError(f"include column '{include_column}' selected no rows")
    return filtered


def _time_from_frame(frame: pd.DataFrame, time_column: str) -> np.ndarray:
    series = frame[time_column]
    if pd.api.types.is_numeric_dtype(series):
        return series.to_numpy(dtype=float)
    dates = pd.to_datetime(series, utc=True)
    return ((dates - dates.iloc[0]).dt.total_seconds() / (365.2425 * 86400.0)).to_numpy(dtype=float)


def command_fit(args: argparse.Namespace) -> int:
    frame = _read_frame(args.csv, args.include_column)
    time = _time_from_frame(frame, args.time)
    values = frame[args.value].to_numpy(dtype=float)
    models = tuple(args.models.split(",")) if args.models else DEFAULT_MODELS
    results = {name: fit.to_dict() for name, fit in fit_all_models(time, values, models).items()}
    dump_json(_json_safe(results), args.output)
    return 0


def command_hindcast(args: argparse.Namespace) -> int:
    frame = _read_frame(args.csv, args.include_column)
    time = _time_from_frame(frame, args.time)
    values = frame[args.value].to_numpy(dtype=float)
    models = tuple(args.models.split(",")) if args.models else DEFAULT_MODELS
    result = rolling_origin_hindcast(time, values, min_train=args.min_train, horizon_steps=args.horizon, models=models)
    dump_json(_json_safe(result), args.output)
    return 0


def command_forecast(args: argparse.Namespace) -> int:
    payload = load_structured(args.input)
    if args.schema:
        errors = validate_instance(args.input, args.schema)
        if errors:
            raise ValueError("input schema validation failed: " + "; ".join(errors))
    run = run_forecast(payload)
    dump_json(_json_safe(run.output), args.output)
    if args.report:
        render_html_report(run.output, args.report)
    if args.output_schema:
        errors = validate_instance(args.output, args.output_schema)
        if errors:
            raise ValueError("output schema validation failed: " + "; ".join(errors))
    print(json.dumps({"forecast": str(args.output), "report": str(args.report) if args.report else None, "forecast_id": run.output["forecast_id"]}, indent=2))
    return 0


def command_workflow(args: argparse.Namespace) -> int:
    payload = load_structured(args.input)
    tasks = [task_from_mapping(record) for record in payload["tasks"]]
    result = analyze_workflow(
        tasks,
        parallel_workers=int(payload.get("parallel_workers", 1)),
        parallel_efficiency=float(payload.get("parallel_efficiency", 1.0)),
        coordination_coefficient=float(payload.get("coordination_coefficient", 0.0)),
        correlated_failure_penalty=float(payload.get("correlated_failure_penalty", 0.0)),
    )
    dump_json(_json_safe(asdict(result)), args.output)
    return 0


def command_validate(args: argparse.Namespace) -> int:
    errors = validate_instance(args.instance, args.schema)
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 1
    print(json.dumps({"valid": True, "errors": []}, indent=2))
    return 0


def command_synthetic(args: argparse.Namespace) -> int:
    series = regime_shift_series(args.seed, args.periods) if args.kind == "regime" else canonical_system_series(args.seed, args.periods)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    series.frame.to_csv(destination, index=False)
    print(series.description)
    return 0


def command_run_all(args: argparse.Namespace) -> int:
    summary = run_all(args.output, args.figures, seed=args.seed)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def command_manifest(args: argparse.Namespace) -> int:
    write_manifest(args.root, args.output)
    return 0


def command_register(args: argparse.Namespace) -> int:
    forecast = load_structured(args.forecast)
    record = append_registry(forecast, args.registry, registered_at=args.registered_at, status=args.status)
    if args.record:
        dump_json(record, args.record)
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


def command_registry_verify(args: argparse.Namespace) -> int:
    errors = verify_registry(args.registry)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 1 if errors else 0


def command_sbom(args: argparse.Namespace) -> int:
    version = Path(args.version_file).read_text(encoding="utf-8").strip()
    path = generate_cyclonedx_sbom(
        args.output,
        "forecasting-a-world-that-accelerates",
        version,
        requirements_path=args.requirements_lock,
    )
    print(path)
    return 0


def _add_series_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("csv", help="CSV file containing the historical series")
    parser.add_argument("--time", default="time_years", help="numeric time or parseable date column")
    parser.add_argument("--value", default="value", help="strictly positive target-value column")
    parser.add_argument("--include-column", default=None, help="optional boolean/0-1 column used to select comparable, in-scope rows")
    parser.add_argument("--models", default=None, help=f"comma-separated models; default: {','.join(DEFAULT_MODELS)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fwta", description="Acceleration-aware forecasting research and production tools")
    sub = parser.add_subparsers(dest="command", required=True)

    forecast = sub.add_parser("forecast", help="run the complete probabilistic forecasting protocol")
    forecast.add_argument("input", help="schema-valid JSON or YAML forecast specification")
    forecast.add_argument("--schema", default="protocol/v2/input.schema.json")
    forecast.add_argument("--output", default="results/forecast/forecast.json")
    forecast.add_argument("--report", default="results/forecast/forecast.html")
    forecast.add_argument("--output-schema", default="protocol/v2/output.schema.json")
    forecast.set_defaults(func=command_forecast)

    fit = sub.add_parser("fit", help="fit candidate growth models to a CSV")
    _add_series_arguments(fit)
    fit.add_argument("--output", default="results/fit.json")
    fit.set_defaults(func=command_fit)

    hindcast = sub.add_parser("hindcast", help="run rolling-origin hindcasts")
    _add_series_arguments(hindcast)
    hindcast.add_argument("--min-train", type=int, default=7)
    hindcast.add_argument("--horizon", type=int, default=1)
    hindcast.add_argument("--output", default="results/hindcast.json")
    hindcast.set_defaults(func=command_hindcast)

    workflow = sub.add_parser("workflow", help="analyze a workflow JSON or YAML")
    workflow.add_argument("input")
    workflow.add_argument("--output", default="results/workflow.json")
    workflow.set_defaults(func=command_workflow)

    validate = sub.add_parser("validate", help="validate a JSON/YAML instance against JSON Schema")
    validate.add_argument("instance")
    validate.add_argument("schema")
    validate.set_defaults(func=command_validate)

    synthetic = sub.add_parser("synthetic", help="generate deterministic synthetic validation data")
    synthetic.add_argument("--kind", choices=("regime", "canonical"), default="regime")
    synthetic.add_argument("--seed", type=int, default=20260728)
    synthetic.add_argument("--periods", type=int, default=48)
    synthetic.add_argument("--output", default="data/synthetic/series.csv")
    synthetic.set_defaults(func=command_synthetic)

    run_everything = sub.add_parser("run-all", help="run controlled hindcasts, ablations, workflow analysis, and figures")
    run_everything.add_argument("--output", default="results/reference")
    run_everything.add_argument("--figures", default="paper/figures")
    run_everything.add_argument("--seed", type=int, default=20260728)
    run_everything.set_defaults(func=command_run_all)

    manifest = sub.add_parser("manifest", help="write a SHA-256 provenance manifest")
    manifest.add_argument("--root", default=".")
    manifest.add_argument("--output", default="release/MANIFEST.json")
    manifest.set_defaults(func=command_manifest)

    register = sub.add_parser("register", help="append a forecast to the local hash-chained prospective registry")
    register.add_argument("forecast")
    register.add_argument("--registry", default="registry/records.json")
    register.add_argument("--status", choices=("prospective-unscored", "demonstration-unscored", "matured-scored", "superseded"), default="prospective-unscored")
    register.add_argument("--registered-at", default=None, help="optional ISO timestamp; omit for current time or SOURCE_DATE_EPOCH")
    register.add_argument("--record", default=None, help="optional path for the appended record as a standalone JSON file")
    register.set_defaults(func=command_register)

    registry_verify = sub.add_parser("registry-verify", help="verify a local prospective registry hash chain")
    registry_verify.add_argument("--registry", default="registry/records.json")
    registry_verify.set_defaults(func=command_registry_verify)

    sbom = sub.add_parser("sbom", help="generate a CycloneDX software bill of materials")
    sbom.add_argument("--output", default="release/sbom.cdx.json")
    sbom.add_argument("--version-file", default="VERSION")
    sbom.add_argument("--requirements-lock", default="requirements-lock.txt")
    sbom.set_defaults(func=command_sbom)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))
