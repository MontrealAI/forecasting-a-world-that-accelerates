from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_REPOSITORY = "https://github.com/MontrealAI/forecasting-a-world-that-accelerates"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh deterministic release metadata and SHA-256 checksums.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--dist", default=str(ROOT / "dist"))
    args = parser.parse_args()

    dist = Path(args.dist).resolve()
    dist.mkdir(parents=True, exist_ok=True)
    metadata_path = dist / "release-metadata.json"
    checksum_path = dist / "SHA256SUMS.txt"

    artifact_paths = sorted(
        path
        for path in dist.iterdir()
        if path.is_file() and path.name not in {metadata_path.name, checksum_path.name}
    )
    metadata = {
        "version": args.version,
        "canonical_repository": CANONICAL_REPOSITORY,
        "hash_algorithm": "SHA-256",
        "artifacts": [
            {"name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in artifact_paths
        ],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    checksum_targets = [*artifact_paths, metadata_path]
    checksum_path.write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_targets),
        encoding="utf-8",
    )
    print(checksum_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
