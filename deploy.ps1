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

# Ensure child tools can locate git/gh even when run from fresh shells.
$env:PATH = "C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI;$env:PATH"

Set-Location $ProjectRoot

try {
    & $Gh auth status *> $null
} catch {
    throw "GitHub CLI is not authenticated. Run: gh auth login"
}
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated. Run: gh auth login"
}

$Owner = (& $Gh api user -q .login).Trim()
if (-not $Owner) {
    throw "Unable to resolve GitHub username from current auth session."
}
$RepoFull = "$Owner/$RepoName"

$HasOrigin = (& $Git remote) -contains "origin"
if (-not $HasOrigin) {
    & $Gh repo view $RepoFull *> $null
    if ($LASTEXITCODE -eq 0) {
        & $Git remote add origin "https://github.com/$RepoFull.git"
        $Branch = (& $Git rev-parse --abbrev-ref HEAD).Trim()
        & $Git push -u origin $Branch
    } else {
        & $Gh repo create $RepoName --source . --$Visibility --push
    }
} else {
    $Branch = (& $Git rev-parse --abbrev-ref HEAD).Trim()
    & $Git push -u origin $Branch
}

$RepoUrl = (& $Gh repo view $RepoFull --json url -q .url).Trim()
Write-Host ""
Write-Host "GitHub repo is live at: $RepoUrl"
Write-Host "Next: Deploy this repo on Streamlit Community Cloud using streamlit_app.py"
