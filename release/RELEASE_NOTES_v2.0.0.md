# Forecasting a World That Accelerates — v2.0.0 Ceiling Edition

Version 2.0.0 is the complete coordinated research release: formal paper, complete prompt, strict schemas, probabilistic engine, controlled and source-linked demonstrations, prospective registry, reproducibility infrastructure, and publication/legal controls.

## Principal additions

- End-to-end `fwta forecast` command.
- Compact canonical model plus generalized realization family.
- Residual-bootstrap model averaging and interval forecasts.
- Explicit uncertainty propagation through market size, adoption, utilization, and technical, demand, and transfer bottlenecks.
- Common-random-number scenario comparisons to reduce Monte Carlo noise.
- Downside, base, accelerated, and discontinuous scenarios.
- Typed evidence, forecast, milestone, trigger, action, and provenance records.
- Self-contained executive HTML reports.
- Hash-chained preregistration registry and proper scoring functions.
- Source-linked METR and SWE-bench demonstrations.
- Expanded cross-platform CI, SBOM, package smoke tests, paper QA, and draft-release workflow.

## Evidence status

The release supplies mechanical verification, controlled mechanism tests, and source-linked historical demonstrations. It does not claim prospective calibration, independent replication, peer-review acceptance, forecast certainty, patentability, or legal immunity. Those are separate gates documented in the paper and repository.

## Publication status

The canonical destination is:

`https://github.com/MontrealAI/forecasting-a-world-that-accelerates`

A repository, DOI, preprint, signature, or independent timestamp is not claimed until the corresponding external record exists. The release workflow creates a draft release for owner inspection.

## Final release hardening

- Corrected the final provenance manifest to exclude ephemeral clean-install smoke directories while preserving their verification hashes in the finalization record.
- Regenerated the manuscript, figures, controlled experiments, historical demonstrations, registries, package distributions, manifests, and deterministic release archives from one frozen source state.

## Final publication package completion

- Added a fixed PDF trailer identifier so repeated release builds are byte-reproducible under the declared source-date epoch.
- Completed clean wheel and source-distribution builds twice and confirmed byte identity.
- Completed independent clean-install CLI and forecast smoke tests for both distributions with byte-identical JSON and HTML outputs.
- Completed the clean-room XeLaTeX/BibTeX arXiv source compilation, text equivalence, and render spot checks.
- Added dual-render, all-page PDF validation and four reviewed full-document contact sheets.
- Added the complete no-terminal GitHub Web UI, Zenodo, and arXiv publication guide.
- Added explicit separation between an annotated release tag, GitHub artifact attestations, an immutable release, and a cryptographically signed tag.
- Prepared deterministic master repository ZIP/TAR.GZ archives, arXiv upload source, checksums, release metadata, and external-publication placeholders without inventing provider identifiers.
