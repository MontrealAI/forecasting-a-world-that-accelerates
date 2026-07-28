#!/usr/bin/env bash
set -Eeuo pipefail
OWNER="MontrealAI"
REPO="forecasting-a-world-that-accelerates"
FULL="$OWNER/$REPO"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v gh >/dev/null || { echo "GitHub CLI is required." >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Run gh auth login first." >&2; exit 1; }
gh repo view "$FULL" >/dev/null 2>&1 || { echo "Repository $FULL does not exist or is inaccessible." >&2; exit 1; }

printf 'Configuring repository defaults...\n'
gh api --method PATCH "repos/$FULL" \
  -f has_issues=true -f has_projects=false -f has_wiki=false \
  -f allow_squash_merge=true -f allow_merge_commit=false -f allow_rebase_merge=false \
  -f allow_update_branch=true -f delete_branch_on_merge=true >/dev/null

optional(){ if ! "$@" >/dev/null 2>&1; then printf 'Manual follow-up may be required:' >&2; printf ' %q' "$@" >&2; printf '\n' >&2; fi; }
optional gh api --method PUT "repos/$FULL/actions/permissions/workflow" -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
optional gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$FULL/vulnerability-alerts"
optional gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$FULL/automated-security-fixes"
optional gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$FULL/private-vulnerability-reporting"
optional gh api --method POST -H "Accept: application/vnd.github+json" "repos/$FULL/pages" -f build_type=workflow
optional gh api --method PUT "repos/$FULL/environments/release"

RULESET_ID="$(gh api "repos/$FULL/rulesets" --jq '.[] | select(.name=="Protected main") | .id' 2>/dev/null | head -n1 || true)"
if [[ -n "$RULESET_ID" ]]; then
  gh api --method PUT "repos/$FULL/rulesets/$RULESET_ID" --input scripts/ruleset-main.json >/dev/null
  printf 'Updated ruleset Protected main.\n'
else
  gh api --method POST "repos/$FULL/rulesets" --input scripts/ruleset-main.json >/dev/null || {
    printf 'Could not create the ruleset automatically. Import scripts/ruleset-main.json in Settings → Rules → Rulesets.\n' >&2
  }
fi

printf 'Automated settings complete. Review the security, Actions, environments, Pages, and CodeQL checklist in docs/UPLOAD_AND_CONFIGURE.md.\n'
