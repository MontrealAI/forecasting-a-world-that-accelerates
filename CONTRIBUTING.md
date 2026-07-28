# Contributing

Thank you for helping improve the research. The project welcomes reproducibility reports, source corrections, hindcast cases, mathematical critiques, tests, accessibility improvements, and security reports.

## Before opening a pull request

1. Open an issue describing the proposed change unless it is a small typo or a security matter.
2. Do not submit confidential, personal, privileged, export-controlled, unlawfully obtained, or license-incompatible material.
3. Preserve source provenance and distinguish observed, derived, estimated, assumed, scenario-conditional, and synthetic quantities.
4. Run `make verify` and include the exact command, operating system, Python version, and result.
5. Sign every commit with the Developer Certificate of Origin line: `Signed-off-by: Your Name <email>`.
6. Complete the project Contributor License Agreement before the contribution is merged. This is required so MONTREAL.AI can maintain the public licenses and offer compatible commercial licenses without fragmenting rights.

## Scientific contribution rules

A contribution must not:

- present simulated data as observed evidence;
- silently change a source, release date, measurement date, unit, or benchmark definition;
- add a coefficient, probability, or forecast result without a traceable derivation or declared assumption;
- claim priority, replication, endorsement, or empirical validation beyond the evidence;
- remove a limitation, uncertainty range, failure mode, or double-counting control merely to strengthen a conclusion.

New empirical datasets require a provenance file under `data/provenance/`, a license/rights note, a stable source identifier, a retrieval date, a checksum where lawful, and a reproducible transformation script.

## Code standards

- Python 3.11 or later.
- Deterministic seeds for controlled experiments.
- Tests for new behavior and edge cases.
- No network calls in the default test suite.
- No secrets, credentials, private endpoints, or hidden telemetry.
- Dependencies must be justified, version-bounded, and license-compatible.
- Public APIs require type annotations and validation of invalid inputs.

## Licensing of contributions

By submitting a contribution, you represent that you have the right to submit it and agree that, if accepted, it is governed by the applicable repository license and the Contributor License Agreement. A pull request does not transfer ownership of MONTREAL.AI, the repository, trademarks, or pre-existing intellectual property.

Corporate contributors should ensure an authorized representative approves the contribution and that employment, contractor, university, or sponsor agreements permit it.

## Review and acceptance

Maintainers may decline, edit, postpone, or close a contribution for scientific, legal, security, product, scope, or maintenance reasons. No submission is accepted until merged by an authorized maintainer. Issue comments and unmerged pull requests are not canonical protocol changes.
