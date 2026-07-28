from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from fwta.timeutil import reproducible_utc_iso

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REPOSITORY = "https://github.com/MontrealAI/forecasting-a-world-that-accelerates"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the deterministic final local release-gate record.")
    parser.add_argument("--pdfium-pages", type=int, required=True)
    parser.add_argument("--poppler-pages", type=int, required=True)
    parser.add_argument("--contact-sheets-reviewed", type=int, required=True)
    parser.add_argument("--blank-pages", type=int, default=0)
    parser.add_argument("--compileall-passed", action="store_true")
    parser.add_argument("--preflight-passed", action="store_true")
    parser.add_argument("--output-json", default="release/FINALIZATION_RECORD.json")
    parser.add_argument("--output-md", default="release/FINALIZATION_RECORD.md")
    args = parser.parse_args()

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    validation = json.loads((ROOT / "release/VALIDATION_REPORT.json").read_text(encoding="utf-8"))
    smoke = json.loads((ROOT / "release/SMOKE_TEST_REPORT.json").read_text(encoding="utf-8"))
    arxiv = json.loads((ROOT / "release/ARXIV_COMPILE_VALIDATION.json").read_text(encoding="utf-8"))
    publication = json.loads((ROOT / "release/PUBLICATION_STATUS.json").read_text(encoding="utf-8"))
    mechanical = validation["mechanical_verification"]

    paper = ROOT / "paper/preprint.pdf"
    prompt = ROOT / "protocol/prompt.txt"
    prompt_md = ROOT / "protocol/prompt.md"
    reference = ROOT / "results/ceiling/reference-forecast.json"
    wheel = ROOT / "dist" / f"forecasting_a_world_that_accelerates-{version}-py3-none-any.whl"
    sdist = ROOT / "dist" / f"forecasting_a_world_that_accelerates-{version}.tar.gz"
    arxiv_archive = ROOT / "dist" / f"Forecasting_A_World_That_Accelerates_preprint_source_v{version}.zip"
    required = (paper, prompt, reference, wheel, sdist, arxiv_archive)
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing finalization artifacts: " + ", ".join(missing))

    local_gates = {
        "full_test_suite_passed": bool(mechanical.get("tests_passed")),
        "coverage_gate_passed": float(mechanical.get("branch_coverage_percent", 0.0)) >= 90.0,
        "schema_suite_passed": bool(mechanical.get("schemas_passed")),
        "python_compileall_passed": bool(args.compileall_passed),
        "release_preflight_passed": bool(args.preflight_passed),
        "wheel_clean_install_passed": bool(mechanical.get("wheel_smoke_passed")),
        "sdist_clean_install_passed": bool(mechanical.get("sdist_smoke_passed")),
        "wheel_sdist_json_byte_identical": bool(smoke["deterministic_equivalence"]["forecast_json_byte_identical"]),
        "wheel_sdist_html_byte_identical": bool(smoke["deterministic_equivalence"]["forecast_html_byte_identical"]),
        "paper_compiled": int(mechanical.get("paper_pages") or 0) == args.pdfium_pages == args.poppler_pages,
        "paper_has_no_blank_pages": int(args.blank_pages) == 0,
        "prompt_byte_identical": prompt.read_bytes() == prompt_md.read_bytes(),
        "arxiv_clean_compile_passed": arxiv.get("compile_result") == "passed",
        "arxiv_text_equivalence_passed": bool(arxiv.get("extracted_text_byte_identical")),
        "arxiv_render_spotchecks_passed": bool(arxiv.get("render_spotchecks_pixel_identical")),
        "live_registry_empty": json.loads((ROOT / "registry/records.json").read_text(encoding="utf-8")) == [],
    }
    if not all(local_gates.values()):
        failed = [name for name, passed in local_gates.items() if not passed]
        raise SystemExit("Finalization gates not complete: " + ", ".join(failed))

    external = {
        "public_github_repository_created": bool(publication.get("repository_published")),
        "signed_tag_verified": bool(publication.get("signed_tag_verified")),
        "github_release_published": bool(publication.get("github_release_published")),
        "zenodo_doi": publication.get("doi"),
        "preprint_identifier": publication.get("preprint_identifier"),
        "peer_reviewed": bool(publication.get("peer_reviewed")),
        "independent_replication": bool(publication.get("independent_replication")),
        "prospective_validation_complete": bool(publication.get("prospective_validation_complete")),
        "status_note": (
            "These are authenticated external publication events and remain unclaimed until an actual provider record exists."
        ),
    }

    payload = {
        "schema_version": "2.0.0",
        "package_version": version,
        "generated_at": reproducible_utc_iso(),
        "canonical_repository": CANONICAL_REPOSITORY,
        "classification": "locally finalized, source-frozen, publication-ready Ceiling Edition research package",
        "claim_boundary": (
            "All declared local build, test, packaging, schema, PDF, clean-install, and arXiv-source compilation gates passed. "
            "This does not prove future forecast accuracy, peer review, independent replication, patentability, freedom to operate, "
            "legal approval, regulatory acceptance, or commercial results. External publication identifiers are never asserted before issuance."
        ),
        "local_release_gates": local_gates,
        "mechanical_metrics": {
            "tests_collected": int(mechanical.get("tests_collected") or 0),
            "combined_line_plus_branch_coverage_percent": float(mechanical.get("branch_coverage_percent") or 0.0),
            "line_coverage_percent": float(mechanical.get("line_coverage_percent") or 0.0),
            "branch_condition_coverage_percent": float(mechanical.get("branch_condition_coverage_percent") or 0.0),
            "schema_instances_validated": 13,
            "paper_pages": int(mechanical.get("paper_pages") or 0),
            "pdfium_pages_rendered": args.pdfium_pages,
            "poppler_pages_rendered": args.poppler_pages,
            "blank_pages_detected": args.blank_pages,
            "visual_contact_sheets_reviewed": args.contact_sheets_reviewed,
        },
        "artifact_hashes": {
            "paper_pdf": sha256(paper),
            "complete_prompt": sha256(prompt),
            "reference_forecast_json": sha256(reference),
            "wheel": sha256(wheel),
            "source_distribution": sha256(sdist),
            "arxiv_source_archive": sha256(arxiv_archive),
            "clean_smoke_forecast_json": smoke["wheel"]["forecast_json_sha256"],
            "clean_smoke_forecast_html": smoke["wheel"]["forecast_html_sha256"],
        },
        "artifacts": [artifact(path) for path in required],
        "external_publication_status": external,
        "manifest_policy": (
            "release/MANIFEST.json is regenerated after this record and excludes its own self-reference, dist/, caches, and transient build directories."
        ),
    }

    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = [f"- {name.replace('_', ' ').capitalize()}: **passed**" for name in local_gates]
    hashes = payload["artifact_hashes"]
    output_md.write_text(
        "\n".join(
            [
                "# Finalization Record - Forecasting a World That Accelerates",
                "",
                f"**Package version:** {version}  ",
                f"**Deterministic record time:** {payload['generated_at']}  ",
                "**Classification:** Locally finalized, source-frozen, publication-ready Ceiling Edition research package.",
                "",
                "> All declared local verification and packaging gates passed. Public repository creation, release publication, DOI issuance, and preprint identifier assignment are external authenticated events and are not asserted until they actually occur.",
                "",
                "## Completed local gates",
                "",
                *rows,
                "",
                "## Principal immutable hashes",
                "",
                f"- Paper PDF: `{hashes['paper_pdf']}`",
                f"- Complete protocol prompt: `{hashes['complete_prompt']}`",
                f"- Reference forecast: `{hashes['reference_forecast_json']}`",
                f"- Python wheel: `{hashes['wheel']}`",
                f"- Python source distribution: `{hashes['source_distribution']}`",
                f"- arXiv source archive: `{hashes['arxiv_source_archive']}`",
                "",
                "## External publication status",
                "",
                f"- Public GitHub repository: **{'complete' if external['public_github_repository_created'] else 'not yet issued'}**",
                f"- Verified signed tag: **{'complete' if external['signed_tag_verified'] else 'not yet issued'}**",
                f"- GitHub release: **{'complete' if external['github_release_published'] else 'not yet issued'}**",
                f"- Zenodo DOI: **{external['zenodo_doi'] or 'not yet issued'}**",
                f"- Timestamped preprint identifier: **{external['preprint_identifier'] or 'not yet issued'}**",
                "",
                "## Claim boundary",
                "",
                payload["claim_boundary"],
                "",
                "The final all-files manifest is generated after this record so it can include this record without circular self-hashing.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "local_gates": len(local_gates), "artifact_count": len(required)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
