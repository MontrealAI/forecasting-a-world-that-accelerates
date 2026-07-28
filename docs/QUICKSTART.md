# Quickstart

## Prerequisites

- Python 3.11–3.13
- Git
- XeLaTeX and `latexmk` only if building the paper
- Docker is optional

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Windows PowerShell activation:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Validate an input

```bash
fwta validate protocol/examples/example-input.yaml protocol/input.schema.json
```

## Run all controlled experiments

```bash
fwta run-all --output results/reference --figures paper/figures
```

## Verify the package

```bash
make verify
```

This runs tests, schema checks, controlled experiments, paper compilation when TeX is available, and a provenance-manifest check.

## Interpret generated outputs

`results/reference/` contains deterministic reference outputs. They demonstrate that the implementation behaves as specified under known controlled conditions. They are not claims about real-world AI timelines.

`data/public/` demonstrates how an external source can enter the pipeline with a provenance record and explicit caveats. Replace illustrative excerpts with an authoritative, source-controlled snapshot before substantive empirical use.
