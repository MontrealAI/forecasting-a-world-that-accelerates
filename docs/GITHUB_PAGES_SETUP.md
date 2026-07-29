# GitHub Pages: one-time setup and autonomous publication

This repository is prepared to publish its own research website and paper at:

```text
https://montrealai.github.io/forecasting-a-world-that-accelerates/
```

The deployment workflow is:

```text
.github/workflows/pages.yml
```

## What happens automatically

After GitHub Pages is enabled once, every relevant push to `main` automatically:

1. checks out the repository;
2. verifies that the committed paper and required research artifacts exist;
3. assembles a static publication website;
4. copies the paper to `paper.pdf` and a versioned download path;
5. publishes the protocol, reference forecast, METR case and SWE-bench case;
6. generates SHA-256 checksums and a machine-readable build record;
7. checks every local link;
8. uploads the Pages artifact;
9. deploys it to the `github-pages` environment.

The Pages workflow deliberately deploys the already reviewed, version-controlled `paper/preprint.pdf`. It does **not** reinstall the entire Python and TeX toolchain merely to publish a static website. The separate `Paper` workflow remains responsible for rebuilding the PDF from LaTeX source. This separation makes the public website faster, safer and substantially more reliable.

## One-time GitHub Web UI steps

### 1. Enable GitHub Pages before merging

Open the repository and click:

```text
Settings
→ Pages
```

Under **Build and deployment**, select:

```text
Source: GitHub Actions
```

GitHub may save the setting immediately. If a Save button appears, click it.

Enabling the source first lets the merge trigger the first successful deployment automatically.

### 2. Merge the prepared pull request

Open the pull request titled:

```text
Publish the paper automatically with GitHub Pages
```

Review the file list, then click:

```text
Merge pull request
→ Squash and merge
→ Confirm squash and merge
```

The merge changes watched publication paths on `main`, so the **Publish GitHub Pages** workflow should begin automatically.

### 3. Watch the first deployment

Open:

```text
Actions
→ Publish GitHub Pages
```

Wait for both jobs to become green:

```text
Build publication website
Deploy publication website
```

If no run begins within about one minute, click:

```text
Run workflow
→ Branch: main
→ Run workflow
```

### 4. Open the website

The final address is:

```text
https://montrealai.github.io/forecasting-a-world-that-accelerates/
```

The first deployment can take a few minutes to become visible.

## What the website publishes

| Public path | Source in the repository |
|---|---|
| `/` | `site/index.html` |
| `/paper.html` | `site/paper.html` |
| `/paper.pdf` | `paper/preprint.pdf` |
| `/downloads/Forecasting_A_World_That_Accelerates_v2.0.0.pdf` | `paper/preprint.pdf` |
| `/prompt.md` | `protocol/prompt.md` |
| `/protocol-specification.json` | `protocol/protocol-specification.json` |
| `/reports/reference-forecast.html` | `results/ceiling/reference-forecast.html` |
| `/reports/metr-forecast.html` | `results/empirical/metr-forecast.html` |
| `/reports/swe-bench-forecast.html` | `results/empirical/swe-bench-forecast.html` |
| `/SHA256SUMS.txt` | generated during deployment |
| `/build.json` | generated during deployment |

## How future updates work

You do not need to rebuild or upload the website manually.

When a change is merged into `main` under any watched path—including the site, paper PDF, protocol or published reports—the workflow runs automatically and replaces the live site only after a successful build.

A failed build does **not** replace the currently working website.

## Recommended environment protection

After the first successful deployment, open:

```text
Settings
→ Environments
→ github-pages
```

Under deployment branches and tags, restrict deployments to:

```text
Selected branches and tags
→ main
```

Do not require a manual reviewer unless you intentionally want every website update to pause for human approval.

## Recommended Actions settings

Open:

```text
Settings
→ Actions
→ General
```

Use:

- GitHub-owned actions allowed;
- workflow permissions set to read repository contents by default;
- actions pinned to full commit SHAs where the setting is available;
- outside-collaborator approval required.

The Pages workflow itself declares only:

```text
contents: read
pages: write
id-token: write
```

It does not use repository secrets and does not push code.

## Troubleshooting

### “Get Pages site failed” or “Pages site not found”

GitHub Pages has not been enabled yet.

Go to:

```text
Settings → Pages → Source: GitHub Actions
```

Then rerun the workflow.

### The website shows 404 immediately after deployment

Wait two to five minutes and refresh. Also confirm that both workflow jobs are green.

### The build says `paper/preprint.pdf` is missing

Confirm that this exact file exists in `main`:

```text
paper/preprint.pdf
```

### A local-link check failed

Open the failed workflow, expand **Assemble and verify the static publication site**, and read the exact missing path. Correct the link or restore the missing file.

### The site deploys but an old page remains visible

Use a hard refresh:

- macOS: `Command + Shift + R`
- Windows: `Ctrl + F5`

Also confirm the `build.json` commit matches the latest `main` commit.

## Publication integrity

Every deployment publishes:

- the exact source commit;
- the paper SHA-256 digest;
- checksums for public research artifacts;
- the workflow-run URL.

This proves which repository state produced the live website. It does not by itself establish peer review, independent replication, legal approval or guaranteed forecast validity.
