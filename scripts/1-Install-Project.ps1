$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    $pythonLauncher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
    if ($pythonLauncher) {
        & $pythonLauncher.Source -3 -m venv (Join-Path $projectRoot '.venv')
        if ($LASTEXITCODE -ne 0) {
            throw 'Could not create .venv with the Python launcher. Install a Python version supported by the pinned PyTorch CUDA wheels, then create .venv manually.'
        }
    } else {
        $pythonCommand = Get-Command 'python.exe' -ErrorAction SilentlyContinue
        if (-not $pythonCommand) { throw 'Python was not found. Install Python, then run this installer again.' }
        & $pythonCommand.Source -m venv (Join-Path $projectRoot '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the project virtual environment.' }
    }
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw 'The virtual environment did not create its Python executable.'
}

$envFile = Join-Path $projectRoot '.env'
if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) {
    Copy-Item -LiteralPath (Join-Path $projectRoot '.env.example') -Destination $envFile
}

Write-Host 'Installing Python packages (this may take a while because the CUDA PyTorch wheels are large)...'
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Could not upgrade pip in .venv.' }
& $venvPython -m pip install -r (Join-Path $projectRoot 'ml-pipeline\requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Could not install ml-pipeline/requirements.txt.' }

$npmCommand = Get-Command 'npm.cmd' -ErrorAction SilentlyContinue
if (-not $npmCommand) { throw 'npm was not found. Install Node.js/npm and run this installer again.' }
Push-Location (Join-Path $projectRoot 'frontend')
try {
    & $npmCommand.Source install
    if ($LASTEXITCODE -ne 0) { throw 'Could not install frontend npm packages.' }
} finally {
    Pop-Location
}

Write-Host 'Checking CUDA availability...'
& $venvPython -c "import torch, sys; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'unavailable'); sys.exit(0 if torch.cuda.is_available() else 1)"
if ($LASTEXITCODE -ne 0) {
    throw 'Dependencies were installed, but CUDA is unavailable. Check the NVIDIA driver and CUDA PyTorch installation before model work.'
}

Write-Host 'Installation complete. Edit .env for model/training settings.'
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'data\splits\v2\train.csv') -PathType Leaf)) {
    Write-Host 'Dataset split manifests are missing. Follow Phases 1-3 in setup.md before training.'
}
Write-Host 'Start the app with: .\scripts\2-Start-Project.ps1'
