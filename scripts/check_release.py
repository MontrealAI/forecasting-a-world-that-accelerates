from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REPOSITORY = "https://github.com/MontrealAI/forecasting-a-world-that-accelerates"
REQUIRED = (
    "README.md",
    "START_HERE.html",
    "LICENSE.md",
    "DISCLAIMER.md",
    "TRADEMARKS.md",
    "SECURITY.md",
    "paper/main.tex",
    "paper/preprint.pdf",
    "protocol/prompt.md",
    "protocol/prompt.txt",
    "protocol/protocol-specification.json",
    "protocol/protocol-specification.yaml",
    "protocol/v2/input.schema.json",
    "protocol/v2/output.schema.json",
    "protocol/v2/registry-record.schema.json",
    "results/ceiling/reference-forecast.json",
    "results/ceiling/reference-forecast.html",
    "results/ceiling/benchmark_index.json",
    "results/ceiling/registry-record.json",
    "registry/records.json",
    "registry/example-records.json",
    "release/PUBLICATION_STATUS.json",
    "release/VALIDATION_REPORT.md",
    "release/VALIDATION_REPORT.json",
    "release/SMOKE_TEST_REPORT.md",
    "release/SMOKE_TEST_REPORT.json",
    "release/ARXIV_COMPILE_VALIDATION.md",
    "release/PDF_RENDER_VALIDATION.json",
    "release/PDF_RENDER_VALIDATION.md",
    "release/ARXIV_COMPILE_VALIDATION.json",
    "release/FINALIZATION_RECORD.md",
    "release/FINALIZATION_RECORD.json",
    "release/QUALITY_RUBRIC.md",
    "release/KNOWN_LIMITS.md",
    "release/sbom.cdx.json",
    "CITATION.cff",
    ".zenodo.json",
    "codemeta.json",
    "release/MANIFEST.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(message)


def validate(instance_path: str, schema_path: str) -> None:
    instance = json.loads((ROOT / instance_path).read_text(encoding="utf-8"))
    schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(instance)
    except jsonschema.ValidationError as exc:
        fail(f"Schema validation failed for {instance_path}: {exc.message}")


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    if missing:
        fail("Missing release files: " + ", ".join(missing))

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    protocol_json = json.loads((ROOT / "protocol/protocol-specification.json").read_text(encoding="utf-8"))
    protocol_yaml = yaml.safe_load((ROOT / "protocol/protocol-specification.yaml").read_text(encoding="utf-8"))
    versions = {
        "VERSION": version,
        "pyproject": str(pyproject["project"]["version"]),
        "CITATION.cff": str(citation["version"]),
        "protocol.json": str(protocol_json["version"]),
        "protocol.yaml": str(protocol_yaml["protocol"]["version"]),
    }
    if len(set(versions.values())) != 1:
        fail(f"Version mismatch: {versions}")

    prompt_md = (ROOT / "protocol/prompt.md").read_bytes()
    prompt_txt = (ROOT / "protocol/prompt.txt").read_bytes()
    if prompt_md != prompt_txt:
        fail("protocol/prompt.md and protocol/prompt.txt must be byte-identical")

    pdf = ROOT / "paper/preprint.pdf"
    if not pdf.read_bytes().startswith(b"%PDF"):
        fail("paper/preprint.pdf is not a valid PDF header")

    validate("results/ceiling/reference-forecast.json", "protocol/v2/output.schema.json")
    validate("results/ceiling/registry-record.json", "protocol/v2/registry-record.schema.json")

    live_registry = json.loads((ROOT / "registry/records.json").read_text(encoding="utf-8"))
    if live_registry != []:
        fail("The distributed live registry must remain empty until an actual prospective public registration occurs")
    example_registry = json.loads((ROOT / "registry/example-records.json").read_text(encoding="utf-8"))
    if not example_registry or any(record.get("status") != "demonstration-unscored" for record in example_registry):
        fail("The example registry must contain only demonstration-unscored records")

    publication = json.loads((ROOT / "release/PUBLICATION_STATUS.json").read_text(encoding="utf-8"))
    validation_report = json.loads((ROOT / "release/VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    smoke = json.loads((ROOT / "release/SMOKE_TEST_REPORT.json").read_text(encoding="utf-8"))
    arxiv = json.loads((ROOT / "release/ARXIV_COMPILE_VALIDATION.json").read_text(encoding="utf-8"))
    finalization = json.loads((ROOT / "release/FINALIZATION_RECORD.json").read_text(encoding="utf-8"))

    if publication.get("package_version") != version:
        fail("publication status version mismatch")
    if publication.get("repository_published") or publication.get("doi") or publication.get("preprint_identifier"):
        fail("external publication identifiers must not be asserted before they exist")
    if (
        validation_report.get("package_version") != version
        or smoke.get("package_version") != version
        or arxiv.get("package_version") != version
    ):
        fail("validation, smoke, or arXiv record version mismatch")
    if finalization.get("package_version") != version:
        fail("finalization record version mismatch")
    gates = finalization.get("local_release_gates", {})
    if not gates or not all(bool(value) for value in gates.values()):
        fail("finalization record does not assert all local release gates")
    external = finalization.get("external_publication_status", {})
    if any(
        [
            external.get("public_github_repository_created"),
            external.get("signed_tag_verified"),
            external.get("github_release_published"),
            external.get("zenodo_doi"),
            external.get("preprint_identifier"),
        ]
    ):
        fail("finalization record must not assert external publication before identifiers exist")

    mechanical = validation_report.get("mechanical_verification", {})
    required_mechanical = (
        "tests_passed",
        "schemas_passed",
        "wheel_smoke_passed",
        "sdist_smoke_passed",
        "prompt_byte_identical",
        "live_registry_empty",
    )
    if not all(bool(mechanical.get(key)) for key in required_mechanical):
        fail("validation report does not assert all completed mechanical release gates")
    if float(mechanical.get("branch_coverage_percent", 0.0)) < 90.0:
        fail("validation report branch-aware coverage is below the 90% release gate")
    if not all(
        [
            smoke.get("deterministic_equivalence", {}).get("forecast_json_byte_identical"),
            smoke.get("deterministic_equivalence", {}).get("forecast_html_byte_identical"),
            arxiv.get("compile_result") == "passed",
            arxiv.get("extracted_text_byte_identical"),
            arxiv.get("render_spotchecks_pixel_identical"),
        ]
    ):
        fail("smoke or arXiv equivalence records are incomplete")

    artifact_hashes = finalization.get("artifact_hashes", {})
    source_artifacts = {
        "paper_pdf": ROOT / "paper/preprint.pdf",
        "complete_prompt": ROOT / "protocol/prompt.txt",
        "reference_forecast_json": ROOT / "results/ceiling/reference-forecast.json",
    }
    for key, path in source_artifacts.items():
        if artifact_hashes.get(key) != sha256(path):
            fail(f"finalization artifact hash mismatch: {key}")

    # Binary release artifacts are absent from the source-only master archive by design.
    # When they are present in dist/, verify them against both smoke and finalization records.
    binary_artifacts = {
        "wheel": ROOT / "dist" / f"forecasting_a_world_that_accelerates-{version}-py3-none-any.whl",
        "source_distribution": ROOT / "dist" / f"forecasting_a_world_that_accelerates-{version}.tar.gz",
        "arxiv_source_archive": ROOT / "dist" / f"Forecasting_A_World_That_Accelerates_preprint_source_v{version}.zip",
    }
    for key, path in binary_artifacts.items():
        if path.is_file() and artifact_hashes.get(key) != sha256(path):
            fail(f"binary finalization artifact hash mismatch: {key}")
    if binary_artifacts["wheel"].is_file() and smoke.get("wheel", {}).get("sha256") != sha256(
        binary_artifacts["wheel"]
    ):
        fail("wheel hash does not match smoke report")
    if binary_artifacts["source_distribution"].is_file() and smoke.get("source_distribution", {}).get(
        "sha256"
    ) != sha256(binary_artifacts["source_distribution"]):
        fail("source-distribution hash does not match smoke report")

    manifest = json.loads((ROOT / "release/MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("algorithm") != "SHA-256" or manifest.get("canonical_repository") != CANONICAL_REPOSITORY:
        fail("manifest metadata is invalid")
    records = manifest.get("files", [])
    paths = [record["path"] for record in records]
    if len(paths) != len(set(paths)) or "release/MANIFEST.json" in paths:
        fail("manifest contains duplicate paths or a self-reference")
    mismatches: list[str] = []
    for record in records:
        path = ROOT / str(record["path"])
        if not path.is_file() or path.stat().st_size != int(record["bytes"]) or sha256(path) != record["sha256"]:
            mismatches.append(str(record["path"]))
    if mismatches:
        fail("Manifest mismatch: " + ", ".join(mismatches[:20]))

    output = {
        "ok": True,
        "version": version,
        "canonical_repository": CANONICAL_REPOSITORY,
        "preprint_sha256": sha256(pdf),
        "prompt_sha256": hashlib.sha256(prompt_md).hexdigest(),
        "manifest_files": len(records),
        "local_release_gates": len(gates),
        "reference_forecast_sha256": sha256(ROOT / "results/ceiling/reference-forecast.json"),
        "registry_status": "demonstration-only; live registry empty",
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
