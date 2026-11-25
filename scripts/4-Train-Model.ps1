$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '0-Import-ProjectEnv.ps1')
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Project Python is missing. Create .venv and install ml-pipeline/requirements.txt first.'
}
if ($env:TSL_DEVICE -ne 'cuda') {
    throw 'GPU training is required. Set TSL_DEVICE=cuda in .env.'
}
& $python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)"
if ($LASTEXITCODE -ne 0) {
    throw 'CUDA is unavailable. Training was not started.'
}

$outputDirectory = $env:TSL_OUTPUT_DIR
if ([string]::IsNullOrWhiteSpace($outputDirectory)) {
    throw 'TSL_OUTPUT_DIR must be set in .env.'
}
if (Test-Path -LiteralPath (Join-Path $projectRoot $outputDirectory)) {
    $outputDirectory = "$outputDirectory-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
}

$arguments = @(
    'ml-pipeline/src/train.py',
    '--architecture', $env:TSL_ARCHITECTURE,
    '--epochs', $env:TSL_EPOCHS,
    '--batch-size', $env:TSL_BATCH_SIZE,
    '--learning-rate', $env:TSL_LEARNING_RATE,
    '--weight-decay', $env:TSL_WEIGHT_DECAY,
    '--seed', $env:TSL_SEED,
    '--num-workers', $env:TSL_NUM_WORKERS,
    '--device', $env:TSL_DEVICE,
    '--output-dir', $outputDirectory
)

Push-Location $projectRoot
try {
    & $python @arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $lastRunFile = Join-Path $projectRoot '.local\last-training-output.txt'
    New-Item -ItemType Directory -Path (Split-Path -Parent $lastRunFile) -Force | Out-Null
    Set-Content -LiteralPath $lastRunFile -Value $outputDirectory -Encoding utf8
    Write-Host "Training output: $outputDirectory"
} finally {
    Pop-Location
}
