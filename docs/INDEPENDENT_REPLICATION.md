# Independent Replication Guide

An independent verifier should receive only the public release archive and its checksum manifest.

## Clean-room procedure

1. Verify the archive digest against `SHA256SUMS.txt`.
2. Extract into a new directory with no access to the author’s build caches.
3. Create a fresh Python environment.
4. Install the pinned requirements and the local package.
5. Run `make test`, `make schemas`, `make forecast`, `make experiments`, `make empirical`, `make registry`, and `make sbom`.
6. Build the paper and compare its digest with the release record.
7. Inspect the generated HTML reports and rendered PDF pages.
8. Record operating system, Python, TeX, dependency versions, commands, results, deviations, and reviewer identity.

## Independence standard

The verifier must disclose employment, funding, authorship, and other material relationships. A successful replication verifies artifact reproducibility, not the truth of forecasts or legal claims.
