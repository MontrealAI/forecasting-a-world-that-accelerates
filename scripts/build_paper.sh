#!/usr/bin/env bash
set -Eeuo pipefail
VERSION="${1:-$(cat VERSION)}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p paper/build dist
LATEXMK_ARGS=(
  -xelatex
  -bibtex
  -interaction=nonstopmode
  -halt-on-error
  -file-line-error
  -outdir=paper/build
)
if ! command -v bibtex >/dev/null 2>&1; then
  if command -v bibtex8 >/dev/null 2>&1; then
    LATEXMK_ARGS+=( -e '$bibtex = "bibtex8 %O %B";' )
  else
    printf 'ERROR: bibtex or bibtex8 is required.\n' >&2
    exit 1
  fi
fi
latexmk "${LATEXMK_ARGS[@]}" paper/main.tex
cp paper/build/main.pdf paper/preprint.pdf
cp paper/build/main.pdf "dist/Forecasting_A_World_That_Accelerates_v${VERSION}.pdf"
printf 'Built %s and %s\n' \
  'paper/preprint.pdf' \
  "dist/Forecasting_A_World_That_Accelerates_v${VERSION}.pdf"
