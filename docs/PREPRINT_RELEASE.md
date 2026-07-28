# Versioned release, DOI, and preprint procedure

This sequence creates several independent records. No single step substitutes for the others.

## 1. Freeze and inspect the release candidate

```bash
make clean
make verify
make release-bundle VERSION=2.0.0
```

Review the compiled PDF and rendered pages, source archive, machine-readable schemas, generated tables and figures, release manifest, SHA-256 file, third-party notices, and absence of secrets or private material.

## 2. Publish protected Git history

Merge through protected `main`. Create a signed annotated tag where signing is configured:

```bash
git tag -s v2.0.0 -m "Forecasting a World That Accelerates v2.0.0"
git push origin v2.0.0
```

Where signing is not configured, use an annotated tag and say so. Never move a published version tag; correct errors with a new version.

## 3. Publish the GitHub release

The release workflow verifies the package and attaches the compiled paper, repository source archive, preprint-source archive, prompt, protocol specification, manifest, checksums, and build provenance. Confirm that the source corresponds exactly to the tagged commit.

## 4. Mint an independent archival DOI

Connect `MontrealAI/forecasting-a-world-that-accelerates` to Zenodo before the archival release, enable the repository, publish the release, and record both the version DOI and concept DOI. Update citation metadata in a subsequent version rather than rewriting the released tag.

## 5. Submit the preprint

Upload `dist/Forecasting_A_World_That_Accelerates_preprint_source_v2.0.0.zip`, not the complete repository. Compile it in a clean directory first. Verify title, author, affiliation, abstract, bibliography, figures, complete prompt appendix, disclosure statement, and license choice. The paper package is prepared for **CC BY-NC-SA 4.0**; select a compatible preprint license only where the submission service offers it and record the exact choice.

## 6. Record only completed facts

Use “release published,” “DOI issued,” “preprint submitted,” and “preprint published” only after each corresponding public record exists. Record identifiers, commit SHA, tag verification state, release URL, and artifact hashes in `release/PUBLICATION_RECORD.md`.
