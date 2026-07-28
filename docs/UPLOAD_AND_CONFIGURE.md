# Upload, configure, verify, and publish the canonical repository

## Exact target

- Owner: `MontrealAI`
- Repository: `forecasting-a-world-that-accelerates`
- Canonical URL: `https://github.com/MontrealAI/forecasting-a-world-that-accelerates`
- Default branch: `main`
- Initial visibility: **private**
- Final visibility after disclosure review: **public**

Do not place this package inside `AGI-Agent-v0` or another repository.

## Browser-only path

Non-technical users should follow the complete click-by-click guide:

[`GITHUB_WEB_UI_GUIDE.md`](GITHUB_WEB_UI_GUIDE.md)

Use the separately supplied GitHub Web UI Upload Kit, which divides the source tree into browser-safe batches and preserves hidden files and directory paths.

## Scripted path - macOS/Linux

1. Install Git and GitHub CLI.
2. Authenticate with `gh auth login` using an account authorized for the `MontrealAI` organization.
3. Extract the master repository archive.
4. From the repository root, run:

```bash
bash scripts/bootstrap_repo.sh
```

## Scripted path - Windows PowerShell

1. Install Git for Windows and GitHub CLI.
2. Authenticate with `gh auth login`.
3. Extract the master repository archive.
4. From the repository root, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap_repo.ps1
```

The scripts refuse an unexpected owner or repository name. Review every requested change before authorization.

## Required publication order

1. Create the repository privately.
2. Upload or push the complete source tree.
3. Run CI, paper, schema, security, and CodeQL checks.
4. Complete the disclosure, IP, licensing, privacy, and counsel checklist.
5. Enable security controls and repository rules.
6. Change visibility to public.
7. Enable GitHub Pages through GitHub Actions.
8. Connect and enable the repository in Zenodo.
9. Enable immutable releases where available.
10. Run the Release workflow for version `2.0.0`.
11. Inspect the draft release and all attached assets.
12. Publish the release.
13. Record the actual Zenodo DOI after issuance.
14. Submit the supplied arXiv source ZIP and record the actual preprint identifier after issuance.
15. Add external identifiers through a new pull request and patch release; never rewrite the original tag.

## Protection and security baseline

- Squash merging only.
- Automatically delete merged branches.
- Pull requests required after bootstrap.
- Force pushes and branch deletion blocked.
- Required CI, paper, security, and CodeQL checks.
- Stale approvals dismissed when independent reviewers exist.
- Secret scanning, push protection, dependency alerts, security updates, and private vulnerability reporting enabled where available.
- Workflow permissions default to read-only; additional permissions declared per workflow.
- External Actions pinned to full commit identifiers.
- Release artifacts generated in CI, checksummed, and attested.

## Signed-release boundary

The supplied release workflow creates an annotated version tag, prepares a draft release, generates release assets, and obtains GitHub artifact attestations. A cryptographically signed Git tag additionally requires a GPG, SSH, or S/MIME signing key controlled by an authorized maintainer. Do not describe an ordinary annotated tag as cryptographically signed.

For a browser-only owner, the strongest directly available controls are:

- protected `main`;
- an immutable GitHub release;
- GitHub artifact attestations;
- a Zenodo DOI;
- a timestamped preprint identifier;
- recorded hashes and provider URLs.

## Final external record

After publication, update `release/PUBLICATION_RECORD.md` with:

- public repository URL;
- release URL;
- immutable tag and commit SHA;
- tag-signature status;
- GitHub attestation evidence;
- Zenodo DOI;
- preprint identifier and version;
- publication dates;
- top-level SHA-256 checksums.

No identifier or external gate may be marked complete until the provider record exists and resolves correctly.
