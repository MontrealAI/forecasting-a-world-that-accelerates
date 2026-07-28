$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q --cov=fwta --cov-branch --cov-report=term-missing
$Cases = @(
  @("example-input.yaml", "input.schema.json"),
  @("example-output.yaml", "output.schema.json"),
  @("example-evidence-record.yaml", "evidence-record.schema.json"),
  @("example-workflow.yaml", "task-graph.schema.json"),
  @("example-hindcast-case.yaml", "hindcast-case.schema.json"),
  @("example-protocol-envelope.yaml", "protocol-envelope.schema.json")
)
foreach ($Case in $Cases) {
  python -m fwta validate "protocol/examples/$($Case[0])" "protocol/$($Case[1])"
}
python -m fwta run-all --output results/reference --figures paper/figures --seed 20260728
Write-Host "Bootstrap and controlled verification completed. Run make paper in an environment with XeLaTeX and latexmk."
