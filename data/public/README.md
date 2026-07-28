# Public evidence excerpts

This directory contains small, frozen, provenance-recorded research excerpts. They exist to exercise the forecasting protocol and make source-linked demonstrations reproducible. They are **not** complete mirrors of upstream datasets, and they do not convert source-linked demonstrations into independent validation of future forecasts.

| File | What it demonstrates | Principal limitation | Provenance |
|---|---|---|---|
| `metr_time_horizon_excerpt.csv` | Task-horizon trend, comparability filtering, acceleration measurement | Hand-transcribed, task-suite-specific, not complete | `../provenance/metr_time_horizon_excerpt.yaml` |
| `metr_time_horizon_hindcast.csv` | Frozen rolling-origin model comparison | Excludes an observation beyond the stated reliable measurement ceiling | same as above |
| `swe_bench_verified_frontier_excerpt.csv` | Bounded frontier growth and saturation stress testing | Selective system-level leaderboard records; model/scaffold/attempt effects are entangled | `../provenance/swe_bench_verified_frontier_excerpt.yaml` |
| `github_operational_evidence.csv` | Adoption and operational-throughput evidence clock | Heterogeneous metrics; PR volume is not verified economic output | `../provenance/github_operational_evidence.yaml` |
| `census_btos_ai_adoption_anchors.csv` | Adoption measurement and explicit series-break handling | The 2026 measure is broader than the earlier measure and must not be naively spliced | `../provenance/census_btos_ai_adoption_anchors.yaml` |

## METR frozen hindcast

Run the frozen public-series example from the repository root:

```bash
fwta hindcast data/public/metr_time_horizon_hindcast.csv \
  --time release_date \
  --value p50_minutes \
  --min-train 7 \
  --output results/public-metr-hindcast.json
```

Or apply the recorded comparability flag directly to the fuller excerpt:

```bash
fwta hindcast data/public/metr_time_horizon_excerpt.csv \
  --time release_date \
  --value p50_minutes \
  --include-column use_for_hindcast \
  --min-train 7 \
  --output results/public-metr-hindcast.json
```

## Source-linked forecast demonstrations

```bash
fwta forecast examples/metr-time-horizon-forecast.yaml \
  --schema protocol/v2/input.schema.json \
  --output results/empirical/metr-forecast.json \
  --report results/empirical/metr-forecast.html \
  --output-schema protocol/v2/output.schema.json

fwta forecast examples/swe-bench-verified-frontier-forecast.yaml \
  --schema protocol/v2/input.schema.json \
  --output results/empirical/swe-bench-forecast.json \
  --report results/empirical/swe-bench-forecast.html \
  --output-schema protocol/v2/output.schema.json
```

## Interpretation rule

Use these files to test mechanics, historical model discrimination, provenance, and comparability controls. Do not describe them as proof that a model will forecast future AI progress, adoption, or economic outcomes accurately. The prospective registry and independent-replication process define the stronger validation levels.

The files' inclusion does not alter any upstream license, trademark, or usage restriction. For substantive empirical publication, obtain and freeze an authorized source snapshot, document all transformations, and treat the upstream publisher as authoritative.
