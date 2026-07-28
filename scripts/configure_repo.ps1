$ErrorActionPreference = "Stop"
$Owner = "MontrealAI"
$Repo = "forecasting-a-world-that-accelerates"
$Full = "$Owner/$Repo"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Invoke-Optional([scriptblock]$Action, [string]$Description) {
  try { & $Action | Out-Null }
  catch { Write-Warning "$Description requires manual follow-up: $($_.Exception.Message)" }
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI (gh) is required." }
& gh auth status | Out-Null
& gh repo view $Full | Out-Null

Write-Host "Configuring $Full..."
& gh api --method PATCH "repos/$Full" `
  -F has_issues=true -F has_projects=false -F has_wiki=false `
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false `
  -F allow_update_branch=true -F delete_branch_on_merge=true | Out-Null

Invoke-Optional { gh api --method PUT "repos/$Full/actions/permissions/workflow" -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false } "Actions default permissions"
Invoke-Optional { gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$Full/vulnerability-alerts" } "Dependabot alerts"
Invoke-Optional { gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$Full/automated-security-fixes" } "Dependabot security updates"
Invoke-Optional { gh api --method PUT -H "Accept: application/vnd.github+json" "repos/$Full/private-vulnerability-reporting" } "Private vulnerability reporting"
Invoke-Optional { gh api --method POST -H "Accept: application/vnd.github+json" "repos/$Full/pages" -f build_type=workflow } "GitHub Pages"
Invoke-Optional { gh api --method PUT "repos/$Full/environments/release" } "Release environment"

$RulesetId = (& gh api "repos/$Full/rulesets" --jq '.[] | select(.name=="Protected main") | .id' 2>$null | Select-Object -First 1)
if ($RulesetId) {
  & gh api --method PUT "repos/$Full/rulesets/$RulesetId" --input scripts/ruleset-main.json | Out-Null
  Write-Host "Updated ruleset: Protected main."
} else {
  try {
    & gh api --method POST "repos/$Full/rulesets" --input scripts/ruleset-main.json | Out-Null
    Write-Host "Created ruleset: Protected main."
  } catch {
    Write-Warning "Could not create the ruleset automatically. Import scripts/ruleset-main.json in Settings > Rules > Rulesets."
  }
}

Write-Host "Automated configuration complete. Review docs/UPLOAD_AND_CONFIGURE.md."
