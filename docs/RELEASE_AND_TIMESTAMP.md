# Release, DOI, preprint, and provenance procedure

## Release identity

A release is identified by the tuple:

```text
(repository owner, repository name, commit SHA, signed tag, semantic version,
artifact SHA-256, workflow attestation, archival DOI, preprint identifier)
```

Any changed component creates a different artifact. Never move or overwrite a published version tag.

## Clean-room release

1. Clone the repository into a new directory.
2. Check out the exact release commit.
3. Run `make verify` without using untracked local data.
4. Compare generated files with the committed reference artifacts.
5. Build `make dist`.
6. Inspect the PDF visually and extract its text.
7. Scan the source archive for secrets and personal paths.
8. Verify dependency licenses and vulnerabilities.
9. Generate `release/MANIFEST.json` and `dist/SHA256SUMS.txt`.
10. Sign the tag and publish through the protected `release` environment.

## Archival metadata

Zenodo and the preprint record should include:

- full title and subtitle;
- Vincent Boucher as author;
- MONTREAL.AI & QUEBEC.AI affiliations;
- release date July 28, 2026;
- version 2.0.0;
- abstract matching the paper;
- keywords from `.zenodo.json`;
- licenses accurately split by artifact category;
- repository URL and commit/tag;
- related identifiers for software, paper, and future versions.

Do not state that a DOI, peer review, independent replication, or timestamp exists before it is actually assigned or completed.
