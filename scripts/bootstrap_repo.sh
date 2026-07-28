#!/usr/bin/env bash
set -Eeuo pipefail
OWNER="MontrealAI"
REPO="forecasting-a-world-that-accelerates"
FULL="$OWNER/$REPO"
EXPECTED="https://github.com/$FULL"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail(){ printf 'ERROR: %s\n' "$*" >&2; exit 1; }
command -v git >/dev/null || fail "Git is required."
command -v gh >/dev/null || fail "GitHub CLI is required. Install it, then run: gh auth login"
gh auth status >/dev/null 2>&1 || fail "Authenticate first with: gh auth login"
[[ -f VERSION && -f README.md && -d paper && -d protocol ]] || fail "Run this script from the prepared package."
LOGIN="$(gh api user --jq .login)"
[[ "${LOGIN,,}" == "${OWNER,,}" ]] || fail "Authenticated as '$LOGIN'; expected '$OWNER'. Switch accounts with gh auth login."

if [[ ! -d .git ]]; then
  git init -b main
  git config user.name "${GIT_AUTHOR_NAME:-MONTREAL.AI}"
  git config user.email "${GIT_AUTHOR_EMAIL:-info@quebec.ai}"
  git add --all
  git commit -s -m "chore: publish FWTA v$(cat VERSION) release candidate"
fi

CURRENT_BRANCH="$(git branch --show-current)"
[[ "$CURRENT_BRANCH" == "main" ]] || git branch -M main

if gh repo view "$FULL" >/dev/null 2>&1; then
  printf 'Repository already exists: %s\n' "$EXPECTED"
else
  gh repo create "$FULL" --public --description "Evidence-grounded, constraint-limited, regime-switching forecasting for a world whose rate of change may itself change." --disable-wiki
fi

if git remote get-url origin >/dev/null 2>&1; then
  REMOTE="$(git remote get-url origin)"
  [[ "$REMOTE" == *"github.com/${FULL}"* || "$REMOTE" == *"github.com:${FULL}"* ]] || fail "origin points to '$REMOTE', not '$EXPECTED'."
else
  git remote add origin "https://github.com/$FULL.git"
fi

git push --set-upstream origin main
bash scripts/configure_repo.sh
printf '\nPublished and configured: %s\n' "$EXPECTED"
printf 'Watch Actions: gh run watch\n'
printf 'Then follow docs/UPLOAD_AND_CONFIGURE.md for release, Zenodo, and preprint steps.\n'
