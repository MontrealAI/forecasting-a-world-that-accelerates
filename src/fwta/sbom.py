from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .timeutil import reproducible_utc_iso

_REQUIREMENT = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;]+)$")


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _locked_components(requirements_path: Path) -> list[dict[str, str]]:
    if not requirements_path.is_file():
        raise FileNotFoundError(f"requirements lock not found: {requirements_path}")
    components: list[dict[str, str]] = []
    seen: set[str] = set()
    for number, raw in enumerate(requirements_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = _REQUIREMENT.fullmatch(line)
        if match is None:
            raise ValueError(f"unsupported requirements-lock entry on line {number}: {line!r}")
        name, version = match.groups()
        normalized = _normalize(name)
        if normalized in seen:
            raise ValueError(f"duplicate locked dependency: {name}")
        seen.add(normalized)
        reference = f"pkg:pypi/{normalized}@{version}"
        components.append(
            {
                "type": "library",
                "bom-ref": reference,
                "name": name,
                "version": version,
                "purl": reference,
                "scope": "required",
            }
        )
    if not components:
        raise ValueError(f"requirements lock contains no exact runtime dependencies: {requirements_path}")
    return sorted(components, key=lambda item: item["purl"])


def generate_cyclonedx_sbom(
    destination: str | Path,
    project_name: str,
    project_version: str,
    requirements_path: str | Path = "requirements-lock.txt",
) -> Path:
    """Generate a deterministic CycloneDX SBOM from the release lock file.

    The release artifact deliberately inventories only the project's declared,
    exactly locked runtime dependencies. It does not capture unrelated packages
    installed in the build host, which would make the SBOM environment-dependent
    and could silently include obsolete local installations.
    """

    lock = Path(requirements_path)
    components = _locked_components(lock)
    project_ref = f"pkg:pypi/{_normalize(project_name)}@{project_version}"
    identity = json.dumps(
        {"project": project_ref, "components": components},
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(identity.encode()).hexdigest()
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{digest[:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}",
        "version": 1,
        "metadata": {
            "timestamp": reproducible_utc_iso(),
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "Forecasting a World That Accelerates SBOM generator",
                        "version": project_version,
                    }
                ]
            },
            "component": {
                "type": "application",
                "bom-ref": project_ref,
                "name": project_name,
                "version": project_version,
                "purl": project_ref,
            },
            "properties": [
                {"name": "fwta:dependency-source", "value": lock.as_posix()},
                {"name": "fwta:scope", "value": "direct locked runtime dependencies"},
            ],
        },
        "components": components,
        "dependencies": [
            {"ref": project_ref, "dependsOn": [component["bom-ref"] for component in components]},
            *[{"ref": component["bom-ref"], "dependsOn": []} for component in components],
        ],
    }
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
