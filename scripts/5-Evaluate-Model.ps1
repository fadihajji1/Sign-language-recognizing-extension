$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '0-Import-ProjectEnv.ps1')
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Project Python is missing. Create .venv and install ml-pipeline/requirements.txt first.'
}
if ($env:TSL_DEVICE -ne 'cuda') {
    throw 'GPU evaluation is required. Set TSL_DEVICE=cuda in .env.'
}
& $python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)"
if ($LASTEXITCODE -ne 0) {
    throw 'CUDA is unavailable. Evaluation was not started.'
}

$experimentDirectory = $env:TSL_EVALUATION_DIR
if ([string]::IsNullOrWhiteSpace($experimentDirectory)) {
    $lastRunFile = Join-Path $projectRoot '.local\last-training-output.txt'
    if (Test-Path -LiteralPath $lastRunFile -PathType Leaf) {
        $experimentDirectory = (Get-Content -LiteralPath $lastRunFile -Raw).Trim()
    } else {
        $experimentDirectory = $env:TSL_EXPERIMENT_DIR
    }
}
if ([string]::IsNullOrWhiteSpace($experimentDirectory)) {
    throw 'Set TSL_EVALUATION_DIR or TSL_EXPERIMENT_DIR in .env, or train a model first.'
}

Push-Location $projectRoot
try {
    & $python ml-pipeline/src/evaluate.py --device $env:TSL_DEVICE --experiment-dir $experimentDirectory
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
