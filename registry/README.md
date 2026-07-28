# FWAA Forecast Registry

This directory supplies an append-only, SHA-256-linked registry for forecasts. It deliberately separates **live prospective records** from **demonstration records**.

- `records.json` is the live registry and ships empty. A record belongs there only when it is frozen before the outcome is known and publicly anchored through a signed commit, release, archive, or equivalent timestamp.
- `example-records.json` is a deterministic demonstration chain generated from bundled reference outputs. Its records use `demonstration-unscored`; they are not prospective evidence.
- `PREREGISTRATION_TEMPLATE.md` defines the human review gate.

## Create a genuine prospective record

```bash
fwta register path/to/frozen-forecast.json \
  --registry registry/records.json \
  --status prospective-unscored
fwta registry-verify --registry registry/records.json
```

Then commit the evidence bundle, input, output, and registry record together; sign the tag or commit; and anchor it in an independent archive. Never edit a registered forecast. Recalibration requires a new record.

## Reproduce the demonstration chain

```bash
SOURCE_DATE_EPOCH=1785254400 fwta register \
  results/ceiling/reference-forecast.json \
  --registry registry/example-records.json \
  --record results/ceiling/registry-record.json \
  --status demonstration-unscored
fwta registry-verify --registry registry/example-records.json
```

The local hash chain detects mutation but is not, by itself, an independent timestamp, proof of authorship, patent right, validation result, or regulatory approval.
