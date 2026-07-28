from __future__ import annotations

import argparse
import copy
import gzip
import os
import shutil
import tarfile
import tempfile
from pathlib import Path

from setuptools import build_meta

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EPOCH = 1785254400
SDIST_INPUTS = ("pyproject.toml", "README.md", "LICENSE", "LICENSE.md", "NOTICE", "LICENSES", "src")


def source_epoch() -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    return int(raw) if raw is not None else DEFAULT_EPOCH


def normalize_sdist(path: Path) -> None:
    """Rewrite a setuptools sdist with stable gzip and tar metadata."""
    temporary = path.with_name(f".{path.name}.normalized")
    with tarfile.open(path, "r:gz") as source:
        members = sorted(source.getmembers(), key=lambda item: item.name)
        with temporary.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=source_epoch(), compresslevel=9) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as destination:
                    for member in members:
                        if member.issym() or member.islnk():
                            raise RuntimeError(f"refusing to normalize linked sdist member: {member.name}")
                        stable = copy.copy(member)
                        stable.uid = 0
                        stable.gid = 0
                        stable.uname = "root"
                        stable.gname = "root"
                        stable.mtime = source_epoch()
                        stable.pax_headers = {}
                        payload = source.extractfile(member) if member.isfile() else None
                        destination.addfile(stable, payload)
    temporary.replace(path)


def remove_build_artifacts(root: Path) -> None:
    for path in (root / "build", root / "src" / "forecasting_a_world_that_accelerates.egg-info"):
        if path.exists():
            shutil.rmtree(path)


def copy_sdist_inputs(destination: Path) -> None:
    for name in SDIST_INPUTS:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        else:
            shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build wheel and source distribution with the declared PEP 517 backend.")
    parser.add_argument("--outdir", default="dist")
    args = parser.parse_args()
    destination = (ROOT / args.outdir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.whl", "*.tar.gz"):
        for path in destination.glob(pattern):
            path.unlink()

    original = Path.cwd()
    try:
        os.chdir(ROOT)
        wheel = build_meta.build_wheel(str(destination))
        remove_build_artifacts(ROOT)
        with tempfile.TemporaryDirectory(prefix="fwaa-sdist-") as temporary:
            source_root = Path(temporary)
            copy_sdist_inputs(source_root)
            os.chdir(source_root)
            sdist = build_meta.build_sdist(str(destination))
            normalize_sdist(destination / sdist)
    finally:
        os.chdir(original)
        remove_build_artifacts(ROOT)

    print(destination / wheel)
    print(destination / sdist)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
