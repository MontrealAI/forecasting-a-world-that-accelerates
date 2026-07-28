from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EPOCH = 1785254400
PAPER_DIRECTORIES = ("appendices", "figures", "sections", "tables")
PAPER_FILES = ("latexmkrc", "main.tex", "references.bib")
GENERATED_SUFFIXES = {".aux", ".blg", ".fdb_latexmk", ".fls", ".log", ".out", ".toc", ".xdv"}
SPOTCHECK_PAGES = (1, 2, 10, 30, 53)


def source_epoch() -> int:
    return int(os.environ.get("SOURCE_DATE_EPOCH", DEFAULT_EPOCH))


def release_date() -> tuple[int, int, int, int, int, int]:
    stamp = dt.datetime.fromtimestamp(source_epoch(), tz=dt.UTC)
    return (max(stamp.year, 1980), stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second - stamp.second % 2)


def reproducible_iso() -> str:
    return dt.datetime.fromtimestamp(source_epoch(), tz=dt.UTC).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("build", "__pycache__", "*.pyc", "*.png"))


def add_to_zip(archive: zipfile.ZipFile, source: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, date_time=release_date())
    info.create_system = 3
    info.external_attr = 0o644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(f"{name} is required to compile-check the preprint source bundle")
    return executable


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    label = Path(command[0]).name
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as log:
        process = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, text=True)
        while process.poll() is None:
            print(f"[arXiv validation] {label} is running...", flush=True)
            time.sleep(8)
        log.seek(0)
        output = log.read()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, command, output=output)
    print(f"[arXiv validation] {label} completed.", flush=True)
    return subprocess.CompletedProcess(command, process.returncode, output, None)


def pdf_pages(pdf: Path) -> int:
    completed = run([require_tool("pdfinfo"), str(pdf)], cwd=pdf.parent)
    for line in completed.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise SystemExit("unable to determine compiled PDF page count")


def extracted_text(pdf: Path, output: Path) -> bytes:
    run([require_tool("pdftotext"), "-layout", str(pdf), str(output)], cwd=pdf.parent)
    return output.read_bytes()


def render_page(pdf: Path, page: int, output_prefix: Path) -> Path:
    run(
        [
            require_tool("pdftoppm"),
            "-f",
            str(page),
            "-l",
            str(page),
            "-singlefile",
            "-r",
            "150",
            "-png",
            str(pdf),
            str(output_prefix),
        ],
        cwd=output_prefix.parent,
    )
    output = output_prefix.with_suffix(".png")
    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit(f"rendering page {page} did not produce a PNG")
    return output


def clean_generated(stage: Path, preserve: set[Path]) -> None:
    for path in list(stage.rglob("*")):
        if path.is_file() and path not in preserve and path.suffix in GENERATED_SUFFIXES:
            path.unlink()


def compile_and_validate(stage: Path, version: str) -> dict[str, object]:
    latexmk = require_tool("latexmk")
    build = stage / "_validation_build"
    build.mkdir()
    run(
        [
            latexmk,
            "-r",
            "paper/latexmkrc",
            "-xelatex",
            "-bibtex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            f"-outdir={build}",
            "main.tex",
        ],
        cwd=stage,
    )
    compiled_pdf = build / "main.pdf"
    compiled_bbl = build / "main.bbl"
    if not compiled_pdf.is_file() or not compiled_pdf.read_bytes().startswith(b"%PDF"):
        raise SystemExit("preprint source validation did not produce a valid PDF")
    if not compiled_bbl.is_file() or compiled_bbl.stat().st_size == 0:
        raise SystemExit("preprint source validation did not produce main.bbl")
    shutil.copy2(compiled_bbl, stage / "main.bbl")

    release_pdf = ROOT / "paper/preprint.pdf"
    with tempfile.TemporaryDirectory(prefix="fwaa-arxiv-compare-") as temporary:
        compare = Path(temporary)
        compiled_text = extracted_text(compiled_pdf, compare / "compiled.txt")
        release_text = extracted_text(release_pdf, compare / "release.txt")
        spotchecks: list[dict[str, object]] = []
        for page in SPOTCHECK_PAGES:
            compiled_png = render_page(compiled_pdf, page, compare / f"compiled-{page}")
            release_png = render_page(release_pdf, page, compare / f"release-{page}")
            spotchecks.append(
                {
                    "page": page,
                    "pixel_identical": compiled_png.read_bytes() == release_png.read_bytes(),
                    "compiled_png_sha256": sha256(compiled_png),
                    "release_png_sha256": sha256(release_png),
                }
            )

    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "package_version": version,
        "generated_at": reproducible_iso(),
        "claim_boundary": "Clean-room XeLaTeX/BibTeX source compilation and render equivalence; not arXiv acceptance or an externally assigned preprint identifier.",
        "compile_result": "passed",
        "compiler": "XeLaTeX with BibTeX via latexmk",
        "pages": pdf_pages(compiled_pdf),
        "compiled_pdf_bytes": compiled_pdf.stat().st_size,
        "compiled_pdf_sha256": sha256(compiled_pdf),
        "release_preprint_bytes": release_pdf.stat().st_size,
        "release_preprint_sha256": sha256(release_pdf),
        "extracted_text_byte_identical": compiled_text == release_text,
        "extracted_text_sha256": hashlib.sha256(compiled_text).hexdigest(),
        "render_spotcheck_pages": list(SPOTCHECK_PAGES),
        "render_spotchecks_pixel_identical": all(bool(item["pixel_identical"]) for item in spotchecks),
        "render_spotchecks": spotchecks,
        "source_contents": [
            "main.tex",
            "main.bbl",
            "paper/",
            "protocol/prompt.txt",
            "README.txt",
            "CC-BY-NC-SA-4.0.txt",
        ],
        "source_stage": "ephemeral clean-room staging directory outside the repository",
    }
    if payload["pages"] != pdf_pages(release_pdf):
        raise SystemExit("clean-room source compilation changed the paper page count")
    if not payload["extracted_text_byte_identical"]:
        raise SystemExit("clean-room source compilation changed extracted text")
    if not payload["render_spotchecks_pixel_identical"]:
        raise SystemExit("clean-room source compilation changed one or more render spot checks")

    release_json = ROOT / "release/ARXIV_COMPILE_VALIDATION.json"
    release_md = ROOT / "release/ARXIV_COMPILE_VALIDATION.md"
    release_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    release_md.write_text(
        "\n".join(
            [
                "# arXiv Source Compile Validation",
                "",
                f"**Package version:** {version}  ",
                "**Result:** passed",
                "",
                "- Clean-room XeLaTeX/BibTeX compilation completed.",
                f"- Final compiled length: **{payload['pages']} pages**.",
                "- Extracted text: **byte-identical** to the release preprint.",
                f"- Render spot checks on pages {', '.join(str(page) for page in SPOTCHECK_PAGES)}: **pixel-identical**.",
                "- A generated `main.bbl` is included in the upload archive for compatibility.",
                "",
                "> This confirms source compilability. It does not assert arXiv acceptance or an assigned identifier.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    preserve = {stage / "main.bbl"}
    shutil.rmtree(build)
    clean_generated(stage, preserve)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and compile-check an arXiv-compatible source archive.")
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--skip-compile-check",
        action="store_true",
        help="package without the clean-room compile check; use only after an independently successful paper build",
    )
    args = parser.parse_args()

    version = args.version
    if version != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
        raise SystemExit("--version must match VERSION")

    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    output = dist / f"Forecasting_A_World_That_Accelerates_preprint_source_v{version}.zip"

    with tempfile.TemporaryDirectory(prefix="fwaa-arxiv-stage-") as temporary:
        stage = Path(temporary) / "preprint-source"
        (stage / "paper").mkdir(parents=True)
        (stage / "protocol").mkdir(parents=True)
        for name in PAPER_FILES:
            shutil.copy2(ROOT / "paper" / name, stage / "paper" / name)
        for name in PAPER_DIRECTORIES:
            copy_tree(ROOT / "paper" / name, stage / "paper" / name)
        shutil.copy2(ROOT / "protocol/prompt.txt", stage / "protocol/prompt.txt")
        shutil.copy2(ROOT / "LICENSES/CC-BY-NC-SA-4.0.txt", stage / "CC-BY-NC-SA-4.0.txt")
        (stage / "main.tex").write_text("\\input{paper/main.tex}\n", encoding="utf-8")
        (stage / "README.txt").write_text(
            "Forecasting a World That Accelerates - preprint source v"
            f"{version}\n\nCompile main.tex with XeLaTeX and BibTeX. "
            "The complete protocol prompt is included in protocol/prompt.txt and embedded by Appendix A.\n",
            encoding="utf-8",
        )

        if not args.skip_compile_check:
            compile_and_validate(stage, version)
        else:
            verified_bbl = ROOT / "paper/main.bbl"
            if not verified_bbl.is_file() or verified_bbl.stat().st_size == 0:
                raise SystemExit("--skip-compile-check requires verified paper/main.bbl")
            shutil.copy2(verified_bbl, stage / "main.bbl")
        with zipfile.ZipFile(output, "w") as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    add_to_zip(archive, path, path.relative_to(stage).as_posix())

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
