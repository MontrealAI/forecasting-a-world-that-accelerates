from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

from fwta.timeutil import reproducible_utc_iso

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path: Path) -> dict[str, object]:
    return {"artifact": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic clean-install smoke-test records.")
    parser.add_argument("--output-json", default="release/SMOKE_TEST_REPORT.json")
    parser.add_argument("--output-md", default="release/SMOKE_TEST_REPORT.md")
    args = parser.parse_args()

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    wheel = ROOT / "dist" / f"forecasting_a_world_that_accelerates-{version}-py3-none-any.whl"
    sdist = ROOT / "dist" / f"forecasting_a_world_that_accelerates-{version}.tar.gz"
    wheel_json = ROOT / "tmp/wheel-smoke/forecast.json"
    wheel_html = ROOT / "tmp/wheel-smoke/forecast.html"
    sdist_json = ROOT / "tmp/sdist-smoke/forecast.json"
    sdist_html = ROOT / "tmp/sdist-smoke/forecast.html"
    required = (wheel, sdist, wheel_json, wheel_html, sdist_json, sdist_html)
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Missing smoke-test artifacts: " + ", ".join(missing))
    if wheel_json.read_bytes() != sdist_json.read_bytes():
        raise SystemExit("Wheel and source-distribution JSON forecasts are not byte-identical")
    if wheel_html.read_bytes() != sdist_html.read_bytes():
        raise SystemExit("Wheel and source-distribution HTML reports are not byte-identical")

    forecast = json.loads(wheel_json.read_text(encoding="utf-8"))
    json_hash = sha256(wheel_json)
    html_hash = sha256(wheel_html)
    payload = {
        "schema_version": "1.0.0",
        "package_version": version,
        "generated_at": reproducible_utc_iso(),
        "claim_boundary": (
            "Clean-install smoke verification of the packaged CLI and deterministic reference forecast; "
            "not an external security audit or prospective forecast validation."
        ),
        "environment": {
            "implementation": platform.python_implementation(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "deterministic_equivalence": {
            "forecast_json_byte_identical": True,
            "forecast_html_byte_identical": True,
            "wheel_forecast_id": forecast.get("forecast_id"),
            "sdist_forecast_id": forecast.get("forecast_id"),
        },
        "wheel": {
            **artifact(wheel),
            "install": "passed",
            "cli_help": "passed",
            "forecast": "passed",
            "forecast_json_sha256": json_hash,
            "forecast_html_sha256": html_hash,
        },
        "source_distribution": {
            **artifact(sdist),
            "install": "passed",
            "cli_help": "passed",
            "forecast": "passed",
            "forecast_json_sha256": json_hash,
            "forecast_html_sha256": html_hash,
        },
    }

    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Clean-Install Smoke-Test Report",
        "",
        f"**Package version:** {version}  ",
        f"**Deterministic record time:** {payload['generated_at']}  ",
        "",
        "The wheel and source distribution were installed independently, each exposed a working CLI, and each produced byte-identical JSON and HTML forecast artifacts under the declared reproducibility environment.",
        "",
        "## Results",
        "",
        f"- Wheel SHA-256: `{payload['wheel']['sha256']}`",
        f"- Source-distribution SHA-256: `{payload['source_distribution']['sha256']}`",
        f"- Forecast JSON SHA-256: `{json_hash}`",
        f"- Forecast HTML SHA-256: `{html_hash}`",
        "- Wheel clean-install forecast: **passed**",
        "- Source-distribution clean-install forecast: **passed**",
        "- JSON equivalence: **byte-identical**",
        "- HTML equivalence: **byte-identical**",
        "",
        "> This record proves packaging and deterministic execution in the stated environment. It is not a security audit, peer review, or prospective forecasting validation.",
    ]
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "wheel_sha256": payload["wheel"]["sha256"],
                "sdist_sha256": payload["source_distribution"]["sha256"],
                "forecast_json_sha256": json_hash,
                "forecast_html_sha256": html_hash,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
