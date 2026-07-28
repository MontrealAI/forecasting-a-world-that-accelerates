# GitHub Web UI publication guide - no terminal required

This is the browser-first, owner-safe publication path for the canonical repository:

`https://github.com/MontrealAI/forecasting-a-world-that-accelerates`

The safest order is:

> private repository -> complete upload -> automated verification -> legal/IP gate -> public visibility -> Pages -> immutable release -> Zenodo DOI -> arXiv identifier

Do not claim a public repository, release, DOI, or preprint identifier until the corresponding provider page actually exists.

## What to download

Use the separately supplied **GitHub Web UI Upload Kit**. It contains numbered batches that preserve the repository's directory structure and keep every browser upload below GitHub's limits.

Do not upload the master ZIP as one file inside the repository. Extract the kit and upload the contents of each numbered batch.

## 1. Create the repository privately

1. Sign in to GitHub with an account allowed to create repositories for `MontrealAI`.
2. Click the **+** menu at the upper right, then **New repository**.
3. Owner: `MontrealAI`.
4. Repository name: `forecasting-a-world-that-accelerates`.
5. Description: `Evidence-grounded, constraint-limited, regime-switching forecasting for a world whose rate of change may itself change.`
6. Visibility: **Private** for the upload and verification phase.
7. Leave **Add a README**, **.gitignore**, and **license** unchecked. They already exist in the package.
8. Click **Create repository**.

## 2. Upload the numbered batches

GitHub's browser currently accepts no more than 100 files in one upload and no more than 25 MiB per uploaded file. The prepared batches obey both limits.

For each batch in numerical order:

1. On the repository's **Code** page, click **Add file -> Upload files**.
2. Open the batch folder on your computer.
3. Select everything *inside* the batch folder, not the outer batch folder.
4. Drag the selected files and directories into GitHub.
5. Wait until all files finish processing.
6. Use the exact commit message shown in the batch's `BATCH_INSTRUCTIONS.txt`.
7. Choose **Commit directly to the `main` branch** during this initial bootstrap only.
8. Click **Commit changes**.

Upload the `.github` and other hidden files in the final batch. On macOS, press `Command + Shift + .` in Finder to reveal hidden files. On Windows, use **View -> Show -> Hidden items**.

Do not enable branch protection until every batch has been uploaded; GitHub does not permit browser uploads directly to a protected branch.

## 3. Confirm the repository is complete

The root should visibly contain at least:

- `.github/`
- `docs/`
- `evidence/`
- `experiments/`
- `paper/`
- `protocol/`
- `registry/`
- `release/`
- `results/`
- `scripts/`
- `site/`
- `src/`
- `tests/`
- `README.md`
- `START_HERE.html`
- `CITATION.cff`
- `LICENSE`
- `SECURITY.md`
- `VERSION`
- `pyproject.toml`

Open and inspect:

1. `paper/preprint.pdf` - 53 pages.
2. `protocol/prompt.md` - the complete executable protocol.
3. `release/FINALIZATION_RECORD.md` - completed local gates and external boundaries.
4. `release/MANIFEST.json` - the all-files source manifest.
5. `.github/workflows/` - CI, paper, security, Pages, CodeQL, and release workflows.

## 4. Configure Actions safely

Open **Settings -> Actions -> General**.

Recommended settings:

- Allow GitHub-owned actions and the specifically permitted actions used by this repository.
- Default workflow permission: **Read repository contents and packages**.
- Leave **Allow GitHub Actions to create and approve pull requests** off.
- Require approval for workflows from outside collaborators.

The workflows declare their own narrow additional permissions where needed and pin external Actions to full commit identifiers.

## 5. Run verification while the repository is private

Open the **Actions** tab and run or inspect:

- **CI**
- **Paper**
- **Security**
- **CodeQL**

Do not run **Release** yet.

Proceed only when the principal checks are green. The local package already records 56 passing tests, 90.54% combined line-plus-branch coverage, 13 schema validations, clean wheel/source-distribution smoke tests, a 53-page dual-render PDF check, and a clean-room arXiv source compile. GitHub's independent run is the public repository's confirmation of those gates.

## 6. Configure appearance

On the repository's **Code** page, click the gear beside **About**.

Use this description:

`Evidence-grounded, constraint-limited, regime-switching forecasting for a world whose rate of change may itself change.`

Suggested topics:

`ai-forecasting`, `forecasting`, `artificial-intelligence`, `technology-forecasting`, `probabilistic-forecasting`, `scenario-planning`, `decision-theory`, `regime-switching`, `risk-management`, `ai-agents`, `reproducible-research`, `open-science`, `python`, `latex`, `research-software`

Under **Settings -> General -> Social preview**, upload `site/assets/social-preview.png`.

Recommended repository features:

- Issues: on.
- Discussions: on after publication if actively moderated.
- Wiki: off; the repository already contains versioned documentation.
- Merge method: squash merging only.
- Automatically delete merged branches: on.

## 7. Complete the disclosure and legal/IP gate

Before public visibility, review:

- `docs/COUNSEL_REVIEW_CHECKLIST.md`
- `PATENTS_AND_PRIOR_ART.md`
- `LICENSE.md`
- `NOTICE`
- `COPYRIGHT`
- `DISCLAIMER.md`
- `TERMS_OF_USE.md`
- `THIRD_PARTY_NOTICES.md`
- `release/KNOWN_LIMITS.md`
- `release/PUBLICATION_STATUS.json`

Confirm that no credential, private key, confidential agreement, private dataset, unpublished customer information, or accidental personal information appears in files or Actions logs.

Repository notices reduce ambiguity but cannot guarantee patentability, freedom to operate, regulatory acceptance, enforceability in every jurisdiction, or immunity from claims. Obtain qualified counsel for the intended facts and jurisdictions before regulated, safety-critical, client-specific, or commercial deployment.

## 8. Make the repository public

After the disclosure gate:

1. Open **Settings -> General**.
2. Scroll to **Danger Zone**.
3. Choose **Change repository visibility -> Public**.
4. Confirm the exact repository name.
5. Recheck security and ruleset settings after the visibility change.

The canonical public address must be exactly:

`https://github.com/MontrealAI/forecasting-a-world-that-accelerates`

## 9. Enable GitHub Pages

1. Open **Settings -> Pages**.
2. Under **Build and deployment**, choose **GitHub Actions**.
3. Open **Actions -> Pages -> Run workflow** on `main`.
4. Wait for the workflow to become green.
5. Verify the site at `https://montrealai.github.io/forecasting-a-world-that-accelerates/`.
6. Add that Pages address to the repository's **About -> Website** field.

## 10. Enable security controls

Open **Settings -> Code security and analysis** and enable every applicable control:

- dependency graph;
- Dependabot alerts;
- Dependabot security updates;
- secret scanning;
- push protection;
- code scanning;
- private vulnerability reporting.

Use the supplied CodeQL workflow rather than creating a conflicting duplicate setup.

## 11. Protect `main`

Only after the browser upload is complete, open **Settings -> Rules -> Rulesets -> New branch ruleset**.

Recommended baseline:

- Name: `Protect main`.
- Target: default branch.
- Active enforcement.
- Block force pushes.
- Restrict deletion.
- Require linear history.
- Require a pull request before merging.
- Require conversation resolution.
- Require the successful CI, paper, security, and CodeQL checks.
- Require the branch to be up to date before merging.

For a sole maintainer, set required approvals to zero initially so updates remain possible through pull requests. Once a genuinely independent maintainer is available, require at least one approval, stale-approval dismissal, and Code Owner review.

## 12. Prepare the archival release

Before publishing the first release:

1. Open **Settings -> General -> Releases**.
2. Enable **release immutability** where available.
3. Connect GitHub to Zenodo and enable this repository *before* publishing the archival release.
4. Open **Actions -> Release -> Run workflow**.
5. Branch: `main`.
6. Version input: `2.0.0` without the `v`.
7. Wait for the workflow to finish.
8. Open the draft release and inspect every attached artifact.
9. Publish only after all assets, checksums, and attestations are present.

The workflow creates an annotated `v2.0.0` tag if absent, rebuilds the complete release, attests the artifacts, and prepares a draft release. The web-only high-assurance result is an immutable GitHub release plus GitHub artifact attestations. A cryptographically signed Git tag requires a signing key controlled by an authorized maintainer; do not represent an ordinary annotated tag as cryptographically signed.

## 13. Obtain the Zenodo DOI

1. Sign in to Zenodo and connect the same GitHub account under **Linked accounts**.
2. Open the Zenodo **GitHub** integration page.
3. Click **Sync now**.
4. Find `MontrealAI/forecasting-a-world-that-accelerates` and enable it.
5. Publish the inspected GitHub `v2.0.0` release.
6. Wait for Zenodo to ingest the release.
7. Open the resulting Zenodo record and copy the actual DOI.
8. Record it in `release/PUBLICATION_RECORD.md` and `release/PUBLICATION_STATUS.json` through a new pull request.
9. Update `CITATION.cff`, `.zenodo.json`, `codemeta.json`, README, and the paper in a patch release such as `v2.0.1`; do not rewrite the immutable `v2.0.0` tag.

A DOI can alternatively be reserved in a Zenodo draft before publication, but a reserved DOI is lost if that draft is deleted. Do not write a placeholder or guessed DOI into the repository.

## 14. Submit the timestamped preprint

Use the supplied file:

`Forecasting_A_World_That_Accelerates_preprint_source_v2.0.0.zip`

On arXiv:

1. Sign in as the author and select **Start New Submission**.
2. Upload the ZIP through **Choose File**.
3. Click **Check Files**.
4. Confirm the top-level TeX file is `main.tex`.
5. Select XeLaTeX if the automatic compiler choice is not correct.
6. Confirm that `main.bbl` is present and that the generated preview is 53 pages.
7. Compare the arXiv preview with `paper/preprint.pdf`, especially the title page, equations, figures, prompt appendix, references, and final page.
8. Enter the exact title, author, abstract, comments, categories, license, and related identifiers.
9. Complete arXiv's author declarations and final **Submit Article** step personally.
10. After arXiv issues the real identifier, record the identifier and submission version in the repository through a new pull request.

arXiv may require account registration, endorsement for a new user or category, moderation, and author acceptance of its license and submission agreement. An identifier cannot be manufactured locally or claimed before arXiv assigns it.

## 15. Final public verification

The release is complete only when all of these are true:

- the canonical GitHub repository opens publicly;
- all required Actions are green;
- `main` is protected;
- GitHub Pages opens and its downloads work;
- the immutable `v2.0.0` release contains the complete assets;
- the release artifacts match `SHA256SUMS.txt`;
- the GitHub release displays its attestation/immutability evidence;
- the real Zenodo DOI resolves to the correct version;
- the real preprint identifier resolves to the correct 53-page paper;
- `release/PUBLICATION_RECORD.md` records the commit, tag, release, DOI, preprint identifier, dates, and hashes without rewriting history.
