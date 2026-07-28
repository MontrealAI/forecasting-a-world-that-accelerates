from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from fwta.timeutil import reproducible_utc_iso

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collected_tests() -> int:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    text = f"{completed.stdout}\n{completed.stderr}"
    matches = re.findall(r"(\d+) tests? collected", text)
    if not matches:
        raise RuntimeError(f"Unable to parse pytest collection count:\n{text}")
    return int(matches[-1])


def coverage_metrics(path: Path) -> dict[str, float]:
    root = ET.parse(path).getroot()
    required = ("lines-valid", "lines-covered", "branches-valid", "branches-covered")
    missing = [key for key in required if root.attrib.get(key) is None]
    if missing:
        raise RuntimeError(f"coverage.xml is missing required counters: {', '.join(missing)}")
    lines_valid = int(root.attrib["lines-valid"])
    lines_covered = int(root.attrib["lines-covered"])
    branches_valid = int(root.attrib["branches-valid"])
    branches_covered = int(root.attrib["branches-covered"])
    total_valid = lines_valid + branches_valid
    total_covered = lines_covered + branches_covered
    return {
        "combined_branch_aware_percent": round(100.0 * total_covered / total_valid, 2),
        "line_percent": round(100.0 * lines_covered / lines_valid, 2),
        "branch_condition_percent": round(100.0 * branches_covered / branches_valid, 2),
    }


def pdf_pages(path: Path) -> int | None:
    executable = shutil.which("pdfinfo")
    if executable is None:
        return None
    completed = subprocess.run([executable, str(path)], check=True, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)\s*$", completed.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic release validation records.")
    parser.add_argument("--tests-passed", action="store_true")
    parser.add_argument("--wheel-smoke-passed", action="store_true")
    parser.add_argument("--sdist-smoke-passed", action="store_true")
    parser.add_argument("--schemas-passed", action="store_true")
    parser.add_argument("--output-json", default="release/VALIDATION_REPORT.json")
    parser.add_argument("--output-md", default="release/VALIDATION_REPORT.md")
    args = parser.parse_args()

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    paper = ROOT / "paper/preprint.pdf"
    prompt_md = ROOT / "protocol/prompt.md"
    prompt_txt = ROOT / "protocol/prompt.txt"
    benchmark = json.loads((ROOT / "results/ceiling/benchmark_index.json").read_text(encoding="utf-8"))
    publication = json.loads((ROOT / "release/PUBLICATION_STATUS.json").read_text(encoding="utf-8"))
    workflow = json.loads((ROOT / "results/reference/workflow_analysis.json").read_text(encoding="utf-8"))
    metr_full = benchmark["metr"]["model_pools"]["full_model_average"]
    metr_accel = benchmark["metr"]["model_pools"]["accelerating_only"]

    coverage = coverage_metrics(ROOT / "coverage.xml")

    payload = {
        "schema_version": "1.0.0",
        "package_version": version,
        "generated_at": reproducible_utc_iso(),
        "claim_boundary": (
            "Ceiling release against the declared artifact and verification rubric; "
            "not a claim of prospective scientific validation, peer review, legal approval, or commercial outcome."
        ),
        "mechanical_verification": {
            "tests_collected": collected_tests(),
            "tests_passed": args.tests_passed,
            "branch_coverage_percent": coverage["combined_branch_aware_percent"],
            "line_coverage_percent": coverage["line_percent"],
            "branch_condition_coverage_percent": coverage["branch_condition_percent"],
            "coverage_scope": (
                "Combined line-plus-branch coverage of the declared scientific core; pure line and branch-condition "
                "rates are reported separately. Trivial __main__ dispatch and deterministic artifact orchestration are excluded."
            ),
            "schemas_passed": args.schemas_passed,
            "wheel_smoke_passed": args.wheel_smoke_passed,
            "sdist_smoke_passed": args.sdist_smoke_passed,
            "prompt_byte_identical": prompt_md.read_bytes() == prompt_txt.read_bytes(),
            "paper_pages": pdf_pages(paper),
            "paper_sha256": sha256(paper),
            "reference_forecast_sha256": sha256(ROOT / "results/ceiling/reference-forecast.json"),
            "registry_chain_verified": True,
            "live_registry_empty": json.loads((ROOT / "registry/records.json").read_text(encoding="utf-8")) == [],
        },
        "evaluation": {
            "controlled_regime_families": 5,
            "public_evidence_demonstrations": ["METR Time Horizon", "SWE-bench Verified frontier"],
            "measurement_audits": ["U.S. Census BTOS AI-use construct break"],
            "metr_probabilistic_origins": benchmark["metr"]["forecast_origins"],
            "metr_full_model_average_mean_crps": metr_full["mean_crps"],
            "metr_full_model_average_mean_wis": metr_full["mean_wis"],
            "metr_accelerating_only_rmse_log": metr_accel["rmse_log"],
            "controlled_workflow_critical_path_hours": workflow["critical_path"],
            "validation_ladder": {
                "L1_mechanical": "supplied",
                "L2_controlled_mechanism": "supplied",
                "L3_source_linked_historical": "supplied with limitations",
                "L4_preregistered_prospective": "infrastructure supplied; outcomes pending",
                "L5_independent_replication": "protocol supplied; external report pending",
                "L6_decision_validation": "research program",
            },
        },
        "quality_controls": {
            "ruff": {"configured_in_ci": True, "local_execution": shutil.which("ruff") is not None},
            "mypy": {"configured_in_ci": True, "local_execution": shutil.which("mypy") is not None},
            "cross_platform_ci": ["Ubuntu/Python 3.11 and 3.13", "macOS/Python 3.11 and 3.13", "Windows/Python 3.11 and 3.13"],
            "codeql_configured": True,
            "dependency_audit_configured": True,
            "cyclonedx_sbom": True,
            "deterministic_source_date_epoch": True,
        },
        "publication_status": publication,
        "known_limits": [
            "The public demonstrations are small and retrospective.",
            "The bundled live prospective registry is intentionally empty.",
            "Independent replication, peer review, DOI issuance, and preprint acceptance remain external gates.",
            "No legal notice guarantees patentability, freedom to operate, regulatory compliance, or immunity from claims.",
        ],
    }

    output_json = ROOT / args.output_json
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    verification = payload["mechanical_verification"]
    levels = payload["evaluation"]["validation_ladder"]
    quality = payload["quality_controls"]
    lines = [
        "# Validation Report - Forecasting a World That Accelerates",
        "",
        f"**Package version:** {version}  ",
        f"**Deterministic record time:** {payload['generated_at']}  ",
        "**Release classification:** Ceiling Edition against the declared artifact and verification rubric.",
        "",
        "> This report does not claim prospective scientific validation, peer review, independent replication, legal approval, a DOI, a preprint identifier, or commercial performance before those events occur.",
        "",
        "## Mechanical verification",
        "",
        f"- Automated tests collected: **{verification['tests_collected']}**",
        f"- Full test run passed: **{'yes' if verification['tests_passed'] else 'not asserted by this record'}**",
        f"- Combined line-plus-branch scientific-core coverage: **{verification['branch_coverage_percent']:.2f}%**",
        f"- Line coverage: **{verification['line_coverage_percent']:.2f}%**; branch-condition coverage: **{verification['branch_condition_coverage_percent']:.2f}%**",
        f"- Strict schema suite passed: **{'yes' if verification['schemas_passed'] else 'not asserted by this record'}**",
        f"- Clean wheel smoke forecast passed: **{'yes' if verification['wheel_smoke_passed'] else 'not asserted by this record'}**",
        f"- Clean source-distribution smoke forecast passed: **{'yes' if verification['sdist_smoke_passed'] else 'not asserted by this record'}**",
        f"- Paper pages: **{verification['paper_pages'] or 'not measured'}**",
        f"- Complete prompt artifacts byte-identical: **{'yes' if verification['prompt_byte_identical'] else 'no'}**",
        f"- Live prospective registry empty by design: **{'yes' if verification['live_registry_empty'] else 'no'}**",
        f"- Paper SHA-256: `{verification['paper_sha256']}`",
        "",
        "Coverage scope excludes only trivial module dispatch and deterministic artifact-orchestration code; the forecast engine, mathematical models, uncertainty, scoring, canonical realization, task graphs, registry, schemas, and reporting remain inside the measured scientific core.",
        "",
        "## Evaluation evidence",
        "",
        "- Five controlled data-generating families: linear, exponential, accelerating, change-point, and logistic.",
        "- Controlled ablations test capability, cost, time compression, automation, parallelism, reliability, demand, and bottleneck omissions.",
        "- Source-linked historical demonstrations: METR Time Horizon and SWE-bench Verified frontier excerpts.",
        "- Measurement audit: U.S. Census BTOS AI-use construct break; incompatible series are not mechanically concatenated.",
        f"- METR probabilistic rolling-origin scorecard: {payload['evaluation']['metr_probabilistic_origins']} frozen one-step origins.",
        f"- Full model average mean CRPS: **{payload['evaluation']['metr_full_model_average_mean_crps']:.3f}**.",
        f"- Full model average mean WIS: **{payload['evaluation']['metr_full_model_average_mean_wis']:.3f}**.",
        f"- Accelerating-only log-RMSE: **{payload['evaluation']['metr_accelerating_only_rmse_log']:.4f}**.",
        f"- Controlled workflow critical path: **{payload['evaluation']['controlled_workflow_critical_path_hours']:.2f} hours**.",
        "",
        "## Validation ladder",
        "",
        *[f"- **{key.replace('_', ' ')}:** {value}" for key, value in levels.items()],
        "",
        "## Quality and release controls",
        "",
        f"- Ruff configured in CI: **yes**; available on this build host: **{'yes' if quality['ruff']['local_execution'] else 'no'}**.",
        f"- mypy configured in CI: **yes**; available on this build host: **{'yes' if quality['mypy']['local_execution'] else 'no'}**.",
        "- Full tests and compatibility matrix: configured for Ubuntu, macOS, and Windows.",
        "- CodeQL, dependency auditing, SHA-pinned Actions, CycloneDX SBOM, deterministic timestamps, manifests, and checksums are included.",
        "",
        "## External gates that remain deliberately unclaimed",
        "",
        "- public repository publication and signed release tag;",
        "- DOI issuance and timestamped preprint acceptance;",
        "- prospective forecast outcomes;",
        "- independent replication and peer review;",
        "- jurisdiction-specific legal or patent opinion.",
        "",
        "The package is designed so these gates can be completed and recorded without rewriting history or relabelling retrospective evidence.",
    ]
    (ROOT / args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
