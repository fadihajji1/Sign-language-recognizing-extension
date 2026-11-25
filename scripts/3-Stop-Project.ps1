$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $projectRoot '.local\project-pids.json'

if (-not (Test-Path -LiteralPath $pidFile -PathType Leaf)) {
    Write-Host 'No project process record was found.'
    exit 0
}

$processes = @(Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json)
foreach ($entry in $processes) {
    $process = Get-Process -Id $entry.Id -ErrorAction SilentlyContinue
    if ($process -and $process.StartTime.ToUniversalTime().ToString('o') -eq $entry.StartTime) {
        Stop-Process -Id $entry.Id -Force
        Write-Host "Stopped $($entry.Name)."
    }
}

Remove-Item -LiteralPath $pidFile -Force
