# Empirical-data adapters

The reference package deliberately separates **controlled validation** from **external empirical evidence**.

## Required provenance fields

Every external series should record:

- dataset and series identifier;
- authoritative source and custodian;
- event, measurement, publication, and retrieval dates;
- original unit and transformed unit;
- extraction method;
- exclusions and comparability bridge;
- license, permission, or other lawful-use basis;
- original-file checksum;
- transformation script and output checksum;
- known limitations.

Use `protocol/evidence-record.schema.json` and keep the provenance record beside the data.

## METR example

The small file in `data/public/` demonstrates the mechanics only. It is a hand-transcribed excerpt, not an official mirror. For substantive work:

1. retrieve the authoritative source and public analysis repository;
2. preserve the exact commit or version;
3. retain upstream notices and terms;
4. execute the upstream analysis when feasible;
5. map only comparable task-suite versions;
6. exclude or separately model measurements the source identifies as unreliable;
7. run rolling-origin hindcasts without exposing future observations to earlier cutoffs;
8. document every transformation.

## No silent web scraping

The core package has no automatic web scraper. This avoids silently changing evidence, violating source terms, or making an old analysis irreproducible. A production deployment may add source-specific connectors, but each connector should cache immutable snapshots, respect access controls and terms, validate schemas, and fail closed when provenance is incomplete.

## Evidence quality

Grade primary and reproducible measurements above indirect or promotional evidence. A recently published source containing old measurements is not current evidence. When series definitions change, bridge them explicitly or keep them separate.
