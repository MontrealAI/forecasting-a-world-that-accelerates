# Forecasting a World That Accelerates

## An evidence-grounded, constraint-limited, regime-switching framework for AI-era decisions

**Version 2.0.0 — Ceiling Edition — July 28, 2026**  
**Author:** Vincent Boucher, President, MONTREAL.AI & QUEBEC.AI  
**Canonical publication target:** `https://github.com/MontrealAI/forecasting-a-world-that-accelerates`

> **Never extrapolate stale timelines. Forecast a world that may accelerate during the forecast itself.**

This package is a formal paper, executable forecasting protocol, complete probabilistic engine, strict machine-readable contract, validation program, and publication-ready research repository.

It separates stages that are often collapsed:

```text
technical capability
        ↓
reliable task completion
        ↓
independently verified completion
        ↓
authorized deployment
        ↓
organizational / market adoption
        ↓
economically or mission-realized output
        ↓
physical-world execution
```

## Start in 30 seconds

Open [`START_HERE.html`](START_HERE.html) in a browser. It explains every deliverable and provides the shortest path for:

- reading the paper;
- running a complete forecast;
- inspecting the public-evidence demonstrations;
- creating the GitHub repository without a terminal;
- completing the IP, legal, security, release, DOI, and preprint gates.

## Compact canonical model

Under scenario \(s\), technical capacity and absorptive demand jointly limit realized output:

\[
\boxed{
Y_s(t)=B_s(t)\min\left\{
Q_0\exp\left[\int_0^t g_{Q,s}(u)\,du\right],
M_s(t)D_s(t)U_s(t)
\right\}
}
\]

The technical-output growth rate is:

\[
\boxed{
g_{Q,s}(t)=
\beta_\theta\dot\theta_s
-\beta_c\frac{\dot c_s}{c_s}
-\beta_\tau\frac{\dot\tau_s}{\tau_s}
+\beta_A\frac{\dot A_s}{A_s+\varepsilon}
+\beta_P\frac{\dot P_s}{P_s}
+\beta_R\frac{\dot R_s}{R_s}
}
\]

In plain language: **realized output is the lesser of what can be technically produced and what the relevant market, institution, or mission can absorb, after remaining real-world bottlenecks are applied.**

Version 2.0.0 also implements a generalized realization family with separate technical, demand, and transfer bottlenecks and optional partial substitution. The compact hard minimum remains the transparent primary case.

## What makes this edition different

Version 2.0.0 closes the principal gaps of the original release candidate:

1. **Complete end-to-end engine.** One input produces the evidence clock, pace comparison, model competition, probabilistic scenarios, milestones, bottlenecks, triggers, action plan, report, and validated output record.
2. **Probabilistic forecasting.** Residual-bootstrap model averaging produces median, mean, 50%, 80%, and 95% intervals.
3. **Four explicit regimes.** Downside, base, accelerated, and hazard-driven discontinuous scenarios remain separate.
4. **Generalized realization.** Technical, demand, and transfer constraints are assigned explicitly; hard-min and finite-substitution operators are supported.
5. **Strict schemas.** Inputs, outputs, evidence records, task graphs, protocol envelopes, and registry records are typed and validated.
6. **Prospective registry.** Forecasts can be preregistered in a SHA-256 hash chain and scored after resolution.
7. **Source-linked demonstrations.** Frozen METR and SWE-bench excerpts exercise unbounded, bounded, change-point, and saturation behaviour with explicit limitations.
8. **Release-grade reproducibility.** Tests, type checks, linting, cross-platform CI, source/wheel smoke tests, SBOM, manifests, paper build, arXiv package, and draft-release automation are coordinated.

## Run the complete reference forecast

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
fwta forecast protocol/v2/examples/canonical-reference-input.yaml \
  --schema protocol/v2/input.schema.json \
  --output results/ceiling/reference-forecast.json \
  --report results/ceiling/reference-forecast.html \
  --output-schema protocol/v2/output.schema.json
```

Then open:

```text
results/ceiling/reference-forecast.html
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -e ".[dev]"
fwta forecast protocol/v2/examples/canonical-reference-input.yaml `
  --schema protocol/v2/input.schema.json `
  --output results/ceiling/reference-forecast.json `
  --report results/ceiling/reference-forecast.html `
  --output-schema protocol/v2/output.schema.json
```

## Verify everything

```bash
make verify
```

The strict verification pipeline runs locally when all development tools are installed and is reproduced in GitHub Actions after upload:

- Ruff lint and formatting checks;
- mypy type checks;
- scientific-core branch coverage with a 90% release gate;
- strict schema validation;
- controlled experiments and ablations;
- METR and SWE-bench demonstrations;
- complete reference forecast and report generation;
- prospective registry verification;
- CycloneDX SBOM generation;
- LaTeX paper compilation;
- release preflight and manifest generation;
- source and distribution consistency checks.

The default scientific runs require no API key and use frozen local evidence. Dependency installation can require network access.

## Use the forecast registry

The distributed live registry is intentionally empty. The bundled reference forecast is retrospective and must remain labelled as a demonstration:

```bash
printf '[]\n' > registry/example-records.json
SOURCE_DATE_EPOCH=1785254400 fwta register results/ceiling/reference-forecast.json \
  --registry registry/example-records.json \
  --record results/ceiling/registry-record.json \
  --status demonstration-unscored
fwta registry-verify --registry registry/example-records.json
```

For a genuine prospective forecast, freeze a new target, evidence bundle, input, and output before the outcome is known, then register it in `registry/records.json` with `prospective-unscored`. A local hash chain detects later mutation only after the chain is anchored in a signed public release or independent archive.

## Validation ladder

The repository never labels retrospective or simulated evidence as prospective proof.

| Level | Evidence | Included in v2.0.0 |
|---|---|---:|
| L1 | Mechanical verification | Yes |
| L2 | Controlled mechanism and ablation tests | Yes |
| L3 | Source-linked historical demonstrations | Yes |
| L4 | Preregistered prospective forecasts | Infrastructure supplied; outcomes pending |
| L5 | Independent replication | Protocol supplied; external report pending |
| L6 | Decision validation | Research program |

See [`docs/VALIDATION_LADDER.md`](docs/VALIDATION_LADDER.md), [`docs/PROSPECTIVE_VALIDATION.md`](docs/PROSPECTIVE_VALIDATION.md), and [`docs/INDEPENDENT_REPLICATION.md`](docs/INDEPENDENT_REPLICATION.md). The exact local verification record is in [`release/VALIDATION_REPORT.md`](release/VALIDATION_REPORT.md), the final source-freeze and packaging evidence is in [`release/FINALIZATION_RECORD.md`](release/FINALIZATION_RECORD.md), and the declared 10/10 artifact rubric is in [`release/QUALITY_RUBRIC.md`](release/QUALITY_RUBRIC.md).

## Package map

```text
paper/                 Formal LaTeX paper, figures, tables, complete prompt appendix
protocol/              Complete prompt, v2 schemas, examples, variables, specification
src/fwta/              Forecast engine, models, uncertainty, task graphs, report, registry
results/ceiling/       Complete reference forecast JSON and standalone report
results/empirical/     METR and SWE-bench demonstration outputs
registry/              Hash-chain registry and preregistration template
data/public/           Frozen source-linked excerpts and controlled fixtures
data/provenance/       Retrieval, selection, hash, and limitation records
tests/                 Unit, schema, engine, scoring, registry, workflow, reproduction tests
docs/                  Quickstart, publication, replication, legal, GitHub, release guidance
release/               SBOM, manifest, validation report, publication status, release notes
site/                   GitHub Pages research site
.github/                CI, CodeQL, Pages, draft release, issue/PR templates
```

## Publish the exact repository

The required destination is:

```text
https://github.com/MontrealAI/forecasting-a-world-that-accelerates
```

Use [`UPLOAD_ME_FIRST.md`](UPLOAD_ME_FIRST.md) for the shortest no-terminal path and [`docs/UPLOAD_AND_CONFIGURE.md`](docs/UPLOAD_AND_CONFIGURE.md) for the complete owner checklist.

The recommended sequence is:

```text
IP / counsel gate
→ private repository
→ clean CI
→ branch and release protection
→ secret scanning and CodeQL
→ public repository
→ signed v2.0.0 tag
→ inspected draft release
→ Zenodo archive / DOI
→ timestamped preprint
→ citation metadata update
```

The package does not claim the repository, DOI, or preprint exists before the authorized account completes those external actions.

## Licensing and protection boundaries

This is a path-specific mixed-license repository:

- software and executable automation: **AGPL-3.0-or-later**;
- paper, prompt, schemas, documentation, and original research artifacts: **CC BY-NC-SA 4.0**;
- third-party material: remains under its original terms;
- trademarks: reserved;
- separate commercial rights: only by signed agreement from MONTREAL.AI.

Read [`LICENSE.md`](LICENSE.md), [`DISCLAIMER.md`](DISCLAIMER.md), [`PATENTS_AND_PRIOR_ART.md`](PATENTS_AND_PRIOR_ART.md), [`TRADEMARKS.md`](TRADEMARKS.md), [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md), and [`docs/COUNSEL_REVIEW_CHECKLIST.md`](docs/COUNSEL_REVIEW_CHECKLIST.md).

These controls improve attribution, provenance, licensing clarity, security, release integrity, and disclosure discipline. They do **not** guarantee patentability, freedom to operate, regulatory compliance, forecast accuracy, commercial results, or immunity from claims. Complete the pre-publication IP decision before public disclosure.

## Citation

Use [`CITATION.cff`](CITATION.cff). Until external identifiers are issued, cite the version and repository destination without inventing a DOI or preprint number.

## Contact

Research, publication, commercial licensing, and institutional inquiries: `info@quebec.ai`
