from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

_DEFAULT_EXCLUDED_PARTS = frozenset(
    {
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
)
_DEFAULT_EXCLUDED_PATHS = frozenset(
    {
        ".coverage",
        "coverage.xml",
        "paper/build",
        "release/MANIFEST.json",
        "tmp",
    }
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_excluded(relative: Path, excluded: set[str]) -> bool:
    relative_text = relative.as_posix()
    if any(part in excluded or part.endswith(".egg-info") for part in relative.parts):
        return True
    return any(relative_text == item or relative_text.startswith(f"{item}/") for item in excluded)


def build_manifest(
    root: str | Path,
    excluded: Iterable[str] = (*_DEFAULT_EXCLUDED_PARTS, *_DEFAULT_EXCLUDED_PATHS),
) -> list[dict[str, object]]:
    base = Path(root).resolve()
    excluded_set = set(excluded)
    records: list[dict[str, object]] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if _is_excluded(relative, excluded_set) or path.suffix == ".pyc":
            continue
        records.append(
            {
                "path": relative.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return records


def write_manifest(root: str | Path, output: str | Path) -> None:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    records = build_manifest(root)
    payload = {
        "algorithm": "SHA-256",
        "canonical_repository": "https://github.com/MontrealAI/forecasting-a-world-that-accelerates",
        "files": records,
    }
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
