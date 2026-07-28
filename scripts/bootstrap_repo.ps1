$ErrorActionPreference = "Stop"
$Owner = "MontrealAI"
$Repo = "forecasting-a-world-that-accelerates"
$Full = "$Owner/$Repo"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Require-Command($Name) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "$Name is required." }
}
Require-Command git
Require-Command gh
& gh auth status | Out-Null
$Login = (& gh api user --jq .login).Trim()
if ($Login.ToLower() -ne $Owner.ToLower()) { throw "Authenticated as $Login; expected $Owner." }
if (-not (Test-Path "README.md") -or -not (Test-Path "VERSION")) { throw "Run this script from the prepared package." }

if (-not (Test-Path ".git")) {
  & git init -b main
  & git config user.name "MONTREAL.AI"
  & git config user.email "info@quebec.ai"
  & git add --all
  & git commit -s -m "chore: publish FWTA v$((Get-Content VERSION).Trim()) release candidate"
}
& git branch -M main
try { & gh repo view $Full | Out-Null } catch {
  & gh repo create $Full --public --description "Evidence-grounded, constraint-limited, regime-switching forecasting for a world whose rate of change may itself change." --disable-wiki
}
$Remote = (& git remote get-url origin 2>$null)
if (-not $Remote) { & git remote add origin "https://github.com/$Full.git" }
elseif (($Remote -notlike "*github.com/$Full*") -and ($Remote -notlike "*github.com`:$Full*")) { throw "origin points to $Remote, not $Full." }
& git push --set-upstream origin main
& "$PSScriptRoot\configure_repo.ps1"
Write-Host "Published: https://github.com/$Full"
