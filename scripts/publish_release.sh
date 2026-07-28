#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
VERSION="$(cat VERSION)"
TAG="v$VERSION"
command -v gh >/dev/null || { echo "GitHub CLI is required." >&2; exit 1; }
gh auth status >/dev/null
[[ -z "$(git status --porcelain)" ]] || { echo "Working tree must be clean." >&2; exit 1; }
make release-bundle VERSION="$VERSION"
python -m build
python scripts/update_dist_checksums.py --version "$VERSION"
if ! git rev-parse "$TAG" >/dev/null 2>&1; then
  if git config user.signingkey >/dev/null 2>&1; then
    git tag -s "$TAG" -m "FWTA $TAG"
  else
    git tag -a "$TAG" -m "FWTA $TAG"
  fi
fi
git push origin "$TAG"
gh release create "$TAG" dist/* \
  --title "Forecasting a World That Accelerates $TAG" \
  --notes-file release/RELEASE_NOTES_v${VERSION}.md \
  --verify-tag \
  --draft
