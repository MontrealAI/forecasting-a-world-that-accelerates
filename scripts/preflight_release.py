from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

CANONICAL_REPOSITORY = "https://github.com/MontrealAI/forecasting-a-world-that-accelerates"
FORBIDDEN_NAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
TEXT_SUFFIXES = {".py", ".md", ".tex", ".yaml", ".yml", ".json", ".toml", ".txt", ".csv", ".html", ".sh", ".ps1"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{24,}\b"),
    "generic bearer token": re.compile(r"Authorization:\s*Bearer\s+[A-Za-z0-9._~-]{20,}", re.I),
}
EXCLUDED_PARTS = {".git", ".venv", ".wheel-test", ".cache", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist", "tmp"}
EXCLUDED_PREFIXES = {"paper/build"}
REQUIRED_FILES = {
    ".github/CODEOWNERS",
    ".github/workflows/ci.yml",
    ".github/workflows/paper.yml",
    "CITATION.cff",
    "DISCLAIMER.md",
    "LICENSE",
    "LICENSE.md",
    "README.md",
    "START_HERE.html",
    "SECURITY.md",
    "TERMS_OF_USE.md",
    "TRADEMARKS.md",
    "paper/main.tex",
    "paper/preprint.pdf",
    "protocol/prompt.md",
    "protocol/prompt.txt",
    "protocol/protocol-specification.json",
    "protocol/protocol-specification.yaml",
    "protocol/v2/input.schema.json",
    "protocol/v2/output.schema.json",
    "protocol/v2/registry-record.schema.json",
    "registry/records.json",
    "registry/example-records.json",
    "results/ceiling/reference-forecast.json",
    "results/ceiling/reference-forecast.html",
    "release/PUBLICATION_STATUS.json",
    "release/ARXIV_COMPILE_VALIDATION.json",
    "release/ARXIV_COMPILE_VALIDATION.md",
    "release/PDF_RENDER_VALIDATION.json",
    "release/PDF_RENDER_VALIDATION.md",
    "release/VALIDATION_REPORT.md",
    "release/FINALIZATION_RECORD.json",
    "release/FINALIZATION_RECORD.md",
    "release/VALIDATION_REPORT.json",
    "release/QUALITY_RUBRIC.md",
    "release/KNOWN_LIMITS.md",
    "release/sbom.cdx.json",
}


def excluded(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    text = relative.as_posix()
    return any(part in EXCLUDED_PARTS for part in relative.parts) or any(
        text == prefix or text.startswith(f"{prefix}/") for prefix in EXCLUDED_PREFIXES
    )


def scan_action_pins(root: Path, findings: list[str]) -> None:
    for workflow in sorted((root / ".github/workflows").glob("*.yml")):
        for line_number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), start=1):
            match = re.search(r"^\s*-?\s*uses:\s*([^\s#]+)", line)
            if not match:
                continue
            value = match.group(1).strip("'\"")
            if value.startswith("./"):
                continue
            if not re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", value):
                findings.append(f"unpinned GitHub Action: {workflow.relative_to(root)}:{line_number}: {value}")


def parse_metadata(root: Path, findings: list[str]) -> None:
    for path in sorted(root.rglob("*.json")):
        if excluded(path, root):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            findings.append(f"invalid JSON: {path.relative_to(root)}: {exc}")
    for path in sorted(root.rglob("*.yaml")) + sorted(root.rglob("*.yml")):
        if excluded(path, root) or ".github/workflows" in path.as_posix():
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            findings.append(f"invalid YAML: {path.relative_to(root)}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run publication and secret-safety preflight checks.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    findings: list[str] = []

    for item in sorted(REQUIRED_FILES):
        if not (root / item).is_file():
            findings.append(f"missing required file: {item}")
    if (root / "schema").exists():
        findings.append("duplicate root schema/ directory exists; protocol/ is the sole schema authority")

    for path in root.rglob("*"):
        if excluded(path, root):
            continue
        if path.is_symlink():
            findings.append(f"symbolic link requires manual review: {path.relative_to(root)}")
            continue
        if not path.is_file():
            continue
        if path.name in FORBIDDEN_NAMES:
            findings.append(f"forbidden sensitive filename: {path.relative_to(root)}")
        if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 5_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"possible {label}: {path.relative_to(root)}")

    scan_action_pins(root, findings)
    parse_metadata(root, findings)

    for item in ("README.md", "CITATION.cff", "codemeta.json", "protocol/protocol-specification.json"):
        path = root / item
        if path.is_file() and CANONICAL_REPOSITORY not in path.read_text(encoding="utf-8"):
            findings.append(f"canonical repository missing from {item}")

    if findings:
        print("Release preflight failed:")
        for finding in sorted(set(findings)):
            print(f"- {finding}")
        return 1
    print("Release preflight passed: required controls are present, metadata parses, Actions are SHA-pinned, and no obvious secret pattern was detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
