# Upload this package first

## Destination

`https://github.com/MontrealAI/forecasting-a-world-that-accelerates`

## Safest no-terminal route: GitHub Web UI

### A. Complete the disclosure gate

Before making anything public, open:

- `docs/COUNSEL_REVIEW_CHECKLIST.md`
- `PATENTS_AND_PRIOR_ART.md`
- `docs/LEGAL_AND_GOVERNANCE.md`

Decide whether the work should be patented, held confidentially, defensively published, or immediately released. Public upload can affect rights. Keep the repository private until this decision is documented.

### B. Create the repository privately

1. Follow `docs/GITHUB_WEB_UI_GUIDE.md`.
2. Owner: `MontrealAI`.
3. Name: `forecasting-a-world-that-accelerates`.
4. Keep the repository private during upload and verification.
5. Do not initialize another README, license, or `.gitignore`; the package already contains them.
6. Extract the supplied GitHub Web UI Upload Kit and upload its numbered batches in order.

### C. Verify before disclosure

1. Confirm all expected folders and hidden files are present.
2. Run CI, Paper, Security, and CodeQL through the Actions tab.
3. Inspect the release records and complete the counsel/IP checklist.
4. Make the repository public only after owner authorization.

### D. Run and inspect the gates

1. Open the repository's **Actions** tab.
2. Confirm CI, paper, and CodeQL workflows pass.
3. Configure the `main` ruleset, required checks, review requirements, force-push prohibition, and tag protection using `docs/GITHUB_SETUP.md`.
4. Enable secret scanning and push protection where the organization plan permits.
5. Inspect `release/PUBLICATION_STATUS.json` and `release/VALIDATION_REPORT.md`.
6. Have an authorized owner approve public disclosure.

### E. Publish and archive

1. Change repository visibility to public only after the gate is signed off.
2. Enable immutable releases and connect the repository to Zenodo.
3. Let the Release workflow create the annotated `v2.0.0` tag, attested assets, and a **draft** release.
4. Inspect every asset and checksum before manually publishing the release.
5. Enable Zenodo for the repository before the public release if a DOI is required.
6. Submit `dist/Forecasting_A_World_That_Accelerates_preprint_source_v2.0.0.zip` to the selected preprint service.
7. Add the issued DOI and preprint identifier to `CITATION.cff`, `.zenodo.json`, the README, and the paper in a metadata-only patch release.

## Final verification

Confirm that:

- `README.md` and `START_HERE.html` render correctly;
- `make verify` passes from a clean checkout;
- the paper builds and all pages render correctly;
- the reference forecast report opens locally;
- the v2 schemas validate their examples and outputs;
- the registry hash chain verifies;
- the release contains the paper, repository archives, arXiv bundle, SBOM, manifest, and checksum file;
- no secrets, private keys, unpublished customer data, or confidential materials are present;
- no DOI, signature, public timestamp, independent replication, or legal approval is claimed unless it actually exists.

For the complete click-by-click sequence, use `docs/GITHUB_WEB_UI_GUIDE.md`.
