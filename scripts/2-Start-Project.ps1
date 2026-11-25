$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '0-Import-ProjectEnv.ps1')
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$vite = Join-Path $projectRoot 'frontend\node_modules\vite\bin\vite.js'
$nodeCommand = Get-Command 'node.exe' -ErrorAction SilentlyContinue
$runDirectory = Join-Path $projectRoot '.local'
$logDirectory = Join-Path $runDirectory 'logs'
$pidFile = Join-Path $runDirectory 'project-pids.json'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Project Python is missing. Create .venv and install ml-pipeline/requirements.txt first.'
}
if (-not (Test-Path -LiteralPath $vite -PathType Leaf) -or -not $nodeCommand) {
    throw 'Frontend dependencies are missing. Run npm install from the frontend folder first.'
}
if ([string]::IsNullOrWhiteSpace($env:TSL_EXPERIMENT_DIR)) {
    throw 'TSL_EXPERIMENT_DIR must name a model folder in .env.'
}
$experimentDirectory = $env:TSL_EXPERIMENT_DIR
if (-not [System.IO.Path]::IsPathRooted($experimentDirectory)) {
    $experimentDirectory = Join-Path $projectRoot $experimentDirectory
}
if (-not (Test-Path -LiteralPath (Join-Path $experimentDirectory 'best_model.pt') -PathType Leaf)) {
    throw "Model checkpoint is missing from '$experimentDirectory'. Prepare the dataset, run scripts/4-Train-Model.ps1, then update TSL_EXPERIMENT_DIR in .env."
}
if ($env:TSL_DEVICE -ne 'cuda') {
    throw 'This project is configured to use the GPU. Set TSL_DEVICE=cuda in .env.'
}
& $python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)"
if ($LASTEXITCODE -ne 0) {
    throw 'CUDA is unavailable. The API is configured to run on the GPU; check the PyTorch CUDA installation.'
}

if (Test-Path -LiteralPath $pidFile -PathType Leaf) {
    $previousRun = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
    $stillRunning = @($previousRun | Where-Object { Get-Process -Id $_.Id -ErrorAction SilentlyContinue })
    if ($stillRunning.Count -gt 0) {
        throw 'The project already appears to be running. Use scripts/3-Stop-Project.ps1 before starting it again.'
    }
    Remove-Item -LiteralPath $pidFile -Force
}

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$apiLog = Join-Path $logDirectory 'api.log'
$apiErrorLog = Join-Path $logDirectory 'api-error.log'
$frontendLog = Join-Path $logDirectory 'frontend.log'
$frontendErrorLog = Join-Path $logDirectory 'frontend-error.log'

$apiArguments = "-m uvicorn main:app --app-dir backend/app --host $env:TSL_API_HOST --port $env:TSL_API_PORT"
$apiProcess = Start-Process -FilePath $python -ArgumentList $apiArguments -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $apiLog -RedirectStandardError $apiErrorLog -PassThru

try {
    $frontendArguments = "`"$vite`" --host $env:TSL_FRONTEND_HOST --port $env:TSL_FRONTEND_PORT"
    $frontendProcess = Start-Process -FilePath $nodeCommand.Source -ArgumentList $frontendArguments -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErrorLog -PassThru
} catch {
    Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
    throw
}

$processes = @(
    [pscustomobject]@{ Name = 'api'; Id = $apiProcess.Id; StartTime = $apiProcess.StartTime.ToUniversalTime().ToString('o') },
    [pscustomobject]@{ Name = 'frontend'; Id = $frontendProcess.Id; StartTime = $frontendProcess.StartTime.ToUniversalTime().ToString('o') }
)
$processes | ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding utf8

Write-Host "API starting at http://$env:TSL_API_HOST`:$env:TSL_API_PORT"
Write-Host "Frontend starting at http://$env:TSL_FRONTEND_HOST`:$env:TSL_FRONTEND_PORT"
Write-Host "Logs: $logDirectory"
Write-Host 'Stop both services with: .\scripts\3-Stop-Project.ps1'
