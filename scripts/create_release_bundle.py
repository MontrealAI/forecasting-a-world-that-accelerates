from __future__ import annotations

import argparse
import gzip
import os
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EPOCH = 1785254400
EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".wheel-test",
    ".cache",
    "__pycache__",
    "build",
    "dist",
}
EXCLUDED_PATHS = {".coverage", "coverage.xml", "paper/build", "tmp"}


def source_epoch() -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    return int(raw) if raw is not None else DEFAULT_EPOCH


def ignored(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    text = relative.as_posix()
    if path.suffix == ".pyc" or any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in relative.parts):
        return True
    return any(text == item or text.startswith(f"{item}/") for item in EXCLUDED_PATHS)


def zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    import datetime as dt

    stamp = dt.datetime.fromtimestamp(epoch, tz=dt.UTC)
    year = max(stamp.year, 1980)
    return (year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second - stamp.second % 2)


def add_to_zip(archive: zipfile.ZipFile, source: Path, arcname: str, epoch: int) -> None:
    info = zipfile.ZipInfo(arcname, date_time=zip_datetime(epoch))
    info.create_system = 3
    mode = 0o755 if source.stat().st_mode & 0o111 else 0o644
    info.external_attr = mode << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def add_to_tar(archive: tarfile.TarFile, source: Path, arcname: str, epoch: int) -> None:
    info = archive.gettarinfo(str(source), arcname=arcname)
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mtime = epoch
    with source.open("rb") as handle:
        archive.addfile(info, handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create deterministic complete source archives.")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    version = args.version
    if version != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
        raise SystemExit("--version must match VERSION")

    epoch = source_epoch()
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    zip_output = dist / f"forecasting-a-world-that-accelerates-v{version}-complete.zip"
    tar_output = dist / f"forecasting-a-world-that-accelerates-v{version}-complete.tar.gz"
    prefix = f"forecasting-a-world-that-accelerates-v{version}"

    with tempfile.TemporaryDirectory() as temporary:
        stage_root = Path(temporary) / prefix
        stage_root.mkdir(parents=True)
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or ignored(path):
                continue
            if path.is_symlink():
                raise SystemExit(f"refusing to package symbolic link: {path.relative_to(ROOT)}")
            target = stage_root / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            os.chmod(target, 0o755 if path.stat().st_mode & 0o111 else 0o644)
            os.utime(target, (epoch, epoch))

        with zipfile.ZipFile(zip_output, "w") as archive:
            for path in sorted(stage_root.rglob("*")):
                if path.is_file():
                    add_to_zip(archive, path, path.relative_to(stage_root.parent).as_posix(), epoch)

        with (
            tar_output.open("wb") as raw,
            gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=9) as compressed,
            tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive,
        ):
            for path in sorted(stage_root.rglob("*")):
                if path.is_file():
                    add_to_tar(archive, path, path.relative_to(stage_root.parent).as_posix(), epoch)

    subprocess.run(
        [os.environ.get("PYTHON", "python3"), str(ROOT / "scripts/update_dist_checksums.py"), "--version", version],
        check=True,
        cwd=ROOT,
    )
    print(zip_output)
    print(tar_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
