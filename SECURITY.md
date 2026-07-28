# Security policy

## Supported versions

Only the latest tagged release and the current `main` branch receive security review. Research results and forecasts are not security certifications.

## Report privately

Do not open a public issue for a suspected vulnerability, secret, privacy exposure, unsafe workflow, dependency compromise, arbitrary file access, code execution, or supply-chain concern.

Use GitHub’s **private vulnerability reporting** feature after it is enabled in repository settings. If that feature is unavailable, email `info@quebec.ai` with subject `SECURITY — Forecasting a World That Accelerates`.

Include:

- affected version/commit and environment;
- reproducible steps or proof of concept;
- actual and potential impact;
- whether data, credentials, users, releases, Actions, Pages, or dependencies are affected;
- suggested remediation, if known;
- whether the report can be shared with coordinators or affected upstream projects.

Do not access data beyond what is necessary, disrupt services, persist access, exfiltrate secrets, exploit third parties, demand payment, or disclose before a coordinated resolution.

## Response process

Receipt may be acknowledged, triaged, reproduced, fixed, assigned a severity, coordinated with dependencies, and disclosed through a security advisory. No bounty, response deadline, embargo duration, safe-harbor determination, or reward is promised unless agreed in writing.

## Supply-chain controls

The release process uses least-privilege workflow permissions, pinned action revisions, protected release environments, dependency review, secret scanning, signed tags where configured, SHA-256 manifests, and provenance attestations. These controls reduce risk but do not eliminate it.
