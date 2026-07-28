# Reproducibility protocol

## Reference environment

- Python: 3.11 or later
- Deterministic seed: `20260728`
- Package version: `2.0.0`
- Runtime dependency bounds: `pyproject.toml`
- Reference resolved versions: `requirements-lock.txt`

## Clean-room reproduction

```bash
git clone https://github.com/MontrealAI/forecasting-a-world-that-accelerates.git
cd forecasting-a-world-that-accelerates
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
make clean
make verify
```

Expected automated-test result for v2.0.0: all tests pass. Reference numerical outputs are compared with tolerances because optimization libraries and platforms can differ slightly.

## Generated files

Do not hand-edit:

- `results/reference/*`
- `paper/figures/*`
- `paper/tables/generated-*`
- `release/MANIFEST.json`
- `dist/SHA256SUMS.txt`

Regenerate them through `make experiments`, `make paper`, or `make release-bundle`.

## Provenance

`fwta manifest` records SHA-256 digests for release-relevant files. External datasets require a provenance record. The release workflow creates checksums after all artifacts are finalized.

## Nondeterminism

The controlled experiments set explicit random seeds. Floating-point optimization, fonts, PDF metadata, dependency resolution, and operating-system libraries can still produce byte-level differences. Scientific verification should compare declared metrics and rendered content, not assume that every PDF byte will be identical across machines.

## Reproducibility claim

The package is intended to make the declared analyses reproducible. It does not claim that every third-party source will remain available, unchanged, or licensed on the same terms indefinitely. Archive source snapshots lawfully and record their checksums.
