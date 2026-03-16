param(
    [string]$RepoName = "solar-sentinel-webapp",
    [ValidateSet("public", "private")]
    [string]$Visibility = "public"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Git = "C:\Program Files\Git\cmd\git.exe"
$Gh = "C:\Program Files\GitHub CLI\gh.exe"

if (-not (Test-Path $Git)) {
    throw "Git is not installed at $Git"
}
if (-not (Test-Path $Gh)) {
    throw "GitHub CLI is not installed at $Gh"
}

Set-Location $ProjectRoot

& $Gh auth status | Out-Null

$HasOrigin = (& $Git remote) -contains "origin"
if (-not $HasOrigin) {
    & $Gh repo create $RepoName --source . --$Visibility --push
} else {
    $Branch = (& $Git rev-parse --abbrev-ref HEAD).Trim()
    & $Git push -u origin $Branch
}

$RepoUrl = (& $Gh repo view --json url -q .url).Trim()
Write-Host ""
Write-Host "GitHub repo is live at: $RepoUrl"
Write-Host "Next: Deploy this repo on Streamlit Community Cloud using streamlit_app.py"
