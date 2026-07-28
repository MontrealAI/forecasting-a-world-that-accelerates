# Third-party notices and provenance

This project is designed to avoid silently absorbing third-party code, data, or expressive material. Each substantive external dataset or factual excerpt must have a provenance record stating its source, retrieval date, transformation, checksum or source identifier where available, use basis, and limitations.

Nothing in this repository relicenses upstream material. Names, marks, data, and factual measurements remain subject to the rights and terms of their respective owners. Inclusion is for attributed research, criticism, validation, and reproducibility; it does not imply endorsement, affiliation, or verification by the upstream publisher.

## External research evidence included in the package

### METR time-horizon excerpts

- `data/public/metr_time_horizon_excerpt.csv`
- `data/public/metr_time_horizon_hindcast.csv`
- `data/provenance/metr_time_horizon_excerpt.yaml`

These are compact, hand-transcribed research excerpts used to demonstrate rolling-origin analysis and model comparison. The upstream METR website, paper, and public analysis repository are authoritative. The files are not complete mirrors, official leaderboards, or substitutes for the upstream dataset. The record above the source's stated reliable measurement ceiling is excluded from the frozen hindcast.

### SWE-bench Verified frontier excerpt

- `data/public/swe_bench_verified_frontier_excerpt.csv`
- `data/provenance/swe_bench_verified_frontier_excerpt.yaml`

This is a selective dated excerpt from the official SWE-bench leaderboard data. It preserves the source's `checked` status and records the observed repository commit and blob identifier. It is not a complete leaderboard mirror, does not isolate the contribution of a model from its scaffold or attempt budget, and is not represented as independent reproduction.

### GitHub operational evidence excerpt

- `data/public/github_operational_evidence.csv`
- `data/provenance/github_operational_evidence.yaml`

This file records a small number of official GitHub operational statistics used to illustrate evidence-clock, adoption, and throughput reasoning. The measurements are heterogeneous. Pull-request volume is not equivalent to verified economic output, and work-start latency is not total completion time.

### U.S. Census Bureau BTOS AI-adoption anchors

- `data/public/census_btos_ai_adoption_anchors.csv`
- `data/provenance/census_btos_ai_adoption_anchors.yaml`

This file records selected official Business Trends and Outlook Survey and related Census research anchors. A documented measurement-definition break separates “AI used to produce goods or services” from the later, broader “AI used in any business function” measure. The package deliberately refuses to splice those groups into one uninterrupted time series without a bridge model.

## Software dependencies and automation

Runtime and development dependencies are declared in `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `requirements-lock.txt`. They remain governed by their own licenses. `release/sbom.cdx.json` provides a machine-readable dependency inventory for the generated release. Before deployment in a regulated or commercial environment, review the inventory, vulnerability reports, license obligations, and the exact built artifacts.

GitHub Actions are referenced by immutable commit identifiers in the workflow files. The upstream actions and their bundled dependencies remain governed by their own licenses and security policies.

## Scholarly sources

Bibliographic references, short quotations, factual summaries, and mathematical antecedents are credited in `paper/references.bib` and the paper. Citation does not imply endorsement. No third-party paper or article is redistributed in full.

## Contribution rule

Do not add copied code, datasets, figures, model outputs, marks, or substantial text unless the contributor has verified that the project may lawfully receive and redistribute them. Every addition must preserve required notices, include a provenance record, disclose transformations and limitations, and pass the pre-publication review gate.
