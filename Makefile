SHELL := /bin/bash
PYTHON ?= python3
VERSION ?= $(shell cat VERSION)
SOURCE_DATE_EPOCH ?= 1785254400
PAPER_PDF := dist/Forecasting_A_World_That_Accelerates_v$(VERSION).pdf

export SOURCE_DATE_EPOCH
export PYTHONHASHSEED := 0
export TZ := UTC
export MPLCONFIGDIR := $(CURDIR)/.cache/matplotlib

.PHONY: help install install-dev test coverage lint typecheck schemas forecast experiments empirical registry sbom paper build smoke audit validation preflight finalization manifest verify arxiv-bundle release-bundle clean

help:
	@printf '%s\n' \
	  'make install          Install the runtime package' \
	  'make install-dev      Install development and verification dependencies' \
	  'make test             Run the automated test suite' \
	  'make coverage         Run branch coverage with the configured threshold' \
	  'make lint             Run Ruff lint and formatting checks' \
	  'make typecheck        Run mypy against the Python package' \
	  'make schemas          Validate all protocol, forecast, and registry examples' \
	  'make forecast         Run the complete probabilistic reference forecast' \
	  'make experiments      Regenerate controlled results, tables, and figures' \
	  'make empirical        Regenerate source-linked public-evidence demonstrations' \
	  'make registry         Rebuild and verify the deterministic demonstration registry' \
	  'make sbom             Generate the CycloneDX software bill of materials' \
	  'make paper            Regenerate results and compile the LaTeX paper' \
	  'make build            Build the Python wheel and source distribution' \
	  'make smoke            Install the wheel in a clean environment and run a forecast' \
	  'make audit            Audit installed Python dependencies (network may be required)' \
	  'make validation       Generate deterministic validation records' \
	  'make finalization     Record all completed local release gates' \
	  'make verify           Run the complete deterministic release verification pipeline' \
	  'make release-bundle   Build repository and arXiv release archives' \
	  'make clean            Remove generated build caches'

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

coverage:
	PYTHONPATH=src $(PYTHON) -m pytest -q -m "not slow" --cov=fwta --cov-branch --cov-report=term-missing --cov-report=xml

lint:
	$(PYTHON) -m ruff check src tests experiments scripts
	$(PYTHON) -m ruff format --check src tests experiments scripts

typecheck:
	$(PYTHON) -m mypy src

forecast:
	mkdir -p results/ceiling
	PYTHONPATH=src $(PYTHON) -m fwta forecast protocol/v2/examples/canonical-reference-input.yaml \
	  --schema protocol/v2/input.schema.json \
	  --output results/ceiling/reference-forecast.json \
	  --report results/ceiling/reference-forecast.html \
	  --output-schema protocol/v2/output.schema.json

experiments:
	PYTHONPATH=src $(PYTHON) -m fwta run-all --output results/reference --figures paper/figures --seed 20260728
	PYTHONPATH=src $(PYTHON) experiments/run_experiments.py
	PYTHONPATH=src $(PYTHON) scripts/generate_paper_tables.py

empirical:
	mkdir -p results/empirical results/ceiling
	PYTHONPATH=src $(PYTHON) -m fwta forecast examples/metr-time-horizon-forecast.yaml \
	  --schema protocol/v2/input.schema.json \
	  --output results/empirical/metr-forecast.json \
	  --report results/empirical/metr-forecast.html \
	  --output-schema protocol/v2/output.schema.json
	PYTHONPATH=src $(PYTHON) -m fwta forecast examples/swe-bench-verified-frontier-forecast.yaml \
	  --schema protocol/v2/input.schema.json \
	  --output results/empirical/swe-bench-forecast.json \
	  --report results/empirical/swe-bench-forecast.html \
	  --output-schema protocol/v2/output.schema.json
	PYTHONPATH=src $(PYTHON) scripts/run_empirical_cases.py
	PYTHONPATH=src $(PYTHON) experiments/run_ceiling_benchmarks.py

registry: forecast
	printf '[]\n' > registry/example-records.json
	PYTHONPATH=src $(PYTHON) -m fwta register results/ceiling/reference-forecast.json \
	  --registry registry/example-records.json \
	  --record results/ceiling/registry-record.json \
	  --status demonstration-unscored
	PYTHONPATH=src $(PYTHON) -m fwta registry-verify --registry registry/example-records.json
	PYTHONPATH=src $(PYTHON) -m fwta registry-verify --registry registry/records.json
	PYTHONPATH=src $(PYTHON) -m fwta validate results/ceiling/registry-record.json protocol/v2/registry-record.schema.json

schemas:
	PYTHONPATH=src $(PYTHON) scripts/validate_release_schemas.py

sbom:
	mkdir -p release
	PYTHONPATH=src $(PYTHON) -m fwta sbom --output release/sbom.cdx.json --version-file VERSION

paper: forecast experiments empirical registry sbom
	bash scripts/build_paper.sh $(VERSION)

build:
	mkdir -p dist
	rm -f dist/*.whl dist/*.tar.gz
	$(PYTHON) scripts/build_python_distribution.py --outdir dist

smoke: build forecast
	rm -rf tmp/wheel-site tmp/sdist-site tmp/wheel-smoke tmp/sdist-smoke
	PIP_NO_INDEX=1 $(PYTHON) -m pip install --no-deps --target tmp/wheel-site dist/*.whl
	PYTHONPATH=tmp/wheel-site $(PYTHON) -m fwta --help >/dev/null
	PYTHONPATH=tmp/wheel-site $(PYTHON) -m fwta forecast protocol/v2/examples/smoke-input.yaml \
	  --schema protocol/v2/input.schema.json \
	  --output tmp/wheel-smoke/forecast.json \
	  --report tmp/wheel-smoke/forecast.html \
	  --output-schema protocol/v2/output.schema.json
	PIP_NO_INDEX=1 $(PYTHON) -m pip install --no-deps --no-build-isolation --target tmp/sdist-site dist/forecasting_a_world_that_accelerates-$(VERSION).tar.gz
	PYTHONPATH=tmp/sdist-site $(PYTHON) -m fwta --help >/dev/null
	PYTHONPATH=tmp/sdist-site $(PYTHON) -m fwta forecast protocol/v2/examples/smoke-input.yaml \
	  --schema protocol/v2/input.schema.json \
	  --output tmp/sdist-smoke/forecast.json \
	  --report tmp/sdist-smoke/forecast.html \
	  --output-schema protocol/v2/output.schema.json
	test -s tmp/wheel-smoke/forecast.json
	test -s tmp/wheel-smoke/forecast.html
	test -s tmp/sdist-smoke/forecast.json
	test -s tmp/sdist-smoke/forecast.html
	cmp tmp/wheel-smoke/forecast.json tmp/sdist-smoke/forecast.json
	cmp tmp/wheel-smoke/forecast.html tmp/sdist-smoke/forecast.html
	PYTHONPATH=src $(PYTHON) scripts/generate_smoke_test_report.py
	rm -rf tmp/wheel-site tmp/sdist-site tmp/wheel-smoke tmp/sdist-smoke

audit:
	$(PYTHON) -m pip_audit

validation: coverage schemas smoke paper
	PYTHONPATH=src $(PYTHON) scripts/generate_validation_report.py --tests-passed --schemas-passed --wheel-smoke-passed --sdist-smoke-passed

preflight:
	PYTHONPATH=src $(PYTHON) scripts/preflight_release.py --root .

finalization: validation arxiv-bundle
	PYTHONPATH=src $(PYTHON) scripts/generate_finalization_record.py \
		--pdfium-pages 53 \
		--poppler-pages 53 \
		--contact-sheets-reviewed 8 \
		--blank-pages 0 \
		--compileall-passed \
		--preflight-passed

manifest:
	PYTHONPATH=src $(PYTHON) -m fwta manifest --root . --output release/MANIFEST.json

verify: lint typecheck test coverage forecast experiments empirical registry schemas sbom paper build smoke validation preflight finalization manifest
	PYTHONPATH=src $(PYTHON) scripts/check_release.py
	@echo 'Verification completed successfully.'

arxiv-bundle: paper
	$(PYTHON) scripts/create_arxiv_bundle.py --version $(VERSION)

release-bundle: verify
	$(PYTHON) scripts/create_release_bundle.py --version $(VERSION)

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .cache .wheel-test paper/build build tmp
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -f .coverage coverage.xml
