#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
make coverage schemas
python -m fwta run-all --output results/reference --figures paper/figures --seed 20260728
printf 'Bootstrap and controlled verification completed. Run make paper when XeLaTeX and latexmk are installed.\n'
